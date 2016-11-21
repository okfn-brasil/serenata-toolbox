import datetime
import os
import re
import pandas as pd
import numpy as np


class Reimbursements:

    FILE_BASE_NAME = 'reimbursements.xz'

    CSV_PARAMS = {
        'compression': 'xz',
        'encoding': 'utf-8',
        'index': False
    }

    def __init__(self, path):
        self.path = path

    def read_csv(self, name):
        filepath = os.path.join(self.path, '{}.xz'.format(name))
        print('Loading {}…'.format(name))
        dtype = {
            'applicant_id': np.str,
            'batch_number': np.str,
            'cnpj_cpf': np.str,
            'congressperson_document': np.str,
            'congressperson_id': np.str,
            'document_id': np.str,
            'document_number': np.str,
            'document_type': np.str,
            'leg_of_the_trip': np.str,
            'passenger': np.str,
            'reimbursement_number': np.str,
            'subquota_group_description': np.str,
            'subquota_group_id': np.str,
            'subquota_number': np.str,
            'term_id': np.str,
        }
        return pd.read_csv(filepath, dtype=dtype)

    @property
    def receipts(self):
        print('Merging all datasets…')
        datasets = ('current-year', 'last-year', 'previous-years')
        data = (self.read_csv(name) for name in datasets)
        return pd.concat(data)

    @staticmethod
    def aggregate(grouped, old, new, func):
        """
        Gets a GroupBy object, aggregates it on `old` using `func`, then rename
        the series name from `old` to `new`, returning a DataFrame.
        """
        output = grouped[old].agg(func)
        output = output.rename(index=new, inplace=True)
        return output.reset_index()

    def group(self, receipts):
        print('Dropping rows without document_value or reimbursement_number…')
        subset = ('document_value', 'reimbursement_number')
        receipts = receipts.dropna(subset=subset)

        print('Grouping dataset by applicant_id, document_id and year…')
        keys = ('year', 'applicant_id', 'document_id')
        valid_receipts = receipts[(~receipts['document_id'].isnull()) &
                                  (~receipts['year'].isnull()) &
                                  (~receipts['applicant_id'].isnull())]
        grouped = valid_receipts.groupby(keys)

        print('Gathering all reimbursement numbers together…')
        numbers = self.aggregate(
            grouped,
            'reimbursement_number',
            'reimbursement_numbers',
            lambda x: ', '.join(set(x))
        )

        print('Summing all net values together…')
        net_total = self.aggregate(
            grouped,
            'net_value',
            'total_net_value',
            np.sum
        )

        print('Summing all reimbursement values together…')
        total = self.aggregate(
            grouped,
            'reimbursement_value',
            'reimbursement_value_total',
            np.sum
        )

        print('Generating the new dataset…')
        final = pd.merge(
            pd.merge(pd.merge(total, net_total, on=keys), numbers, on=keys),
            valid_receipts,
            on=keys
        )
        final.rename(columns={'net_value': 'net_values',
                              'reimbursement_value': 'reimbursement_values'},
                     inplace=True)
        final = final.drop('reimbursement_number', 1)
        return final

    @staticmethod
    def unique_str(strings):
        return ', '.join(set(strings))

    def write_reimbursement_file(self, receipts):
        print('Casting changes to a new DataFrame…')
        df = pd.DataFrame(data=receipts)

        print('Writing it to file…')
        filepath = os.path.join(self.path, self.FILE_BASE_NAME)
        df.to_csv(filepath, **self.CSV_PARAMS)

        print('Done.')


if __name__ == '__main__':
    reimbursements = Reimbursements()
    df = reimbursements.group(reimbursements.receipts)
    reimbursements.write_reimbursement_file(df)
