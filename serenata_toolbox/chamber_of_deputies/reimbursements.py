import os

from datetime import date

import pandas as pd
import numpy as np

AVAILABLE_YEARS = [year for year in range(2009, date.today().year + 1)]


class Reimbursements:

    FILE_BASE_NAME = 'reimbursements.xz'

    CSV_PARAMS = {
        'compression': 'xz',
        'encoding': 'utf-8',
        'index': False
    }

    def __init__(self, path, years=AVAILABLE_YEARS):
        self.path = path
        self.years = years if isinstance(years, list) else [years]

    def read_csv(self, name):
        filepath = os.path.join(self.path, name)
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
        datasets = ["reimbursements-{}.xz".format(n) for n in self.years]
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

        groupby_keys = ('year', 'applicant_id', 'document_id')
        receipts = receipts.dropna(subset=subset + groupby_keys)

        receipts = receipts[receipts['document_value'] != 0]
        receipts = receipts[receipts['reimbursement_number'] != '0']
        receipts = receipts[receipts['year'] != 0]
        receipts = receipts[receipts['applicant_id'] != '0']
        receipts = receipts[receipts['document_id'] != '0']

        print('Grouping dataset by applicant_id, document_id and year…')
        grouped = receipts.groupby(groupby_keys)

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
            pd.merge(pd.merge(total, net_total, on=groupby_keys), numbers, on=groupby_keys),
            receipts,
            on=groupby_keys
        )
        final = final.drop_duplicates(subset=groupby_keys)
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
