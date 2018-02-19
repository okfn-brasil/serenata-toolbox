import os.path
from unittest import TestCase
from unittest.mock import patch

import pandas as pd

from serenata_toolbox.chamber_of_deputies.reimbursements_cleaner import \
    COLUMNS, ReimbursementsCleaner

FIXTURES_PATH = os.path.join('tests', 'fixtures', 'chamber_of_deputies')
DATASET_COLS = [
    'congressperson_name',
    'congressperson_id',
    'congressperson_document',
    'term',
    'state',
    'party',
    'term_id',
    'subquota_number',
    'subquota_description',
    'subquota_group_id',
    'subquota_group_description',
    'supplier',
    'cnpj_cpf',
    'document_number',
    'document_type',
    'issue_date',
    'document_value',
    'remark_value',
    'total_net_value',
    'month',
    'year',
    'installment',
    'passenger',
    'leg_of_the_trip',
    'batch_number',
    'numbers',
    'total_value',
    'applicant_id',
    'document_id',
]


class TestReimbursementsCleaner(TestCase):
    def setUp(self):
        self.subject = ReimbursementsCleaner(2017, FIXTURES_PATH)

    @patch.object(ReimbursementsCleaner, 'load_source_file')
    @patch.object(ReimbursementsCleaner, 'translate')
    @patch.object(ReimbursementsCleaner, 'aggregate_multiple_payments')
    @patch.object(ReimbursementsCleaner, 'save')
    def test_execute_run_internal_functions(self, save_mock, aggregate_mock,
                                            translate_mock, load_source_mock):
        self.subject.execute()
        load_source_mock.assert_called_with()
        translate_mock.assert_called_with()
        aggregate_mock.assert_called_with()
        save_mock.assert_called_with()

    def test_load_source_file_into_data_variable(self):
        self.assertIsNone(self.subject.data)
        self.subject.load_source_file()
        self.assertIsInstance(self.subject.data, pd.DataFrame)

    def test_translate_columns(self):
        expected_cols = list(COLUMNS.values())
        self.subject.load_source_file()
        self.subject.translate()
        self.assertEqual(expected_cols, list(self.subject.data.columns))

    def test_translate_subquotas(self):
        expected_subquotas = [
            'Maintenance of office supporting parliamentary activity',
            'Maintenance of office supporting parliamentary activity',
            'Fuels and lubricants',
            'Fuels and lubricants',
            'Fuels and lubricants',
            'Fuels and lubricants',
        ]
        self.subject.load_source_file()
        self.subject.translate()
        data = self.subject.data
        self.assertEqual(expected_subquotas,
                         data.subquota_description.tolist())
        self.assertEqual(['1', '1', '3', '3', '3', '3'],
                         data.subquota_number.tolist())

    def test_aggregate_multiple_payments_run_payments_functions(self):
        self.subject.load_source_file()
        self.subject.translate()
        self.subject.aggregate_multiple_payments()
        self.assertEqual((5, 29), self.subject.data.shape)

    @patch.object(pd.DataFrame, 'to_csv')
    def test_save_into_csv_file(self, to_csv_mock):
        self.subject.load_source_file()
        self.subject.translate()
        self.subject.aggregate_multiple_payments()
        self.subject.save()
        path = os.path.join(FIXTURES_PATH, 'reimbursements-2017.csv')
        to_csv_mock.assert_called_once_with(path, index=False)

    def test_house_payments_rename_columns(self):
        self.subject.load_source_file()
        self.subject.translate()
        data = self.subject._house_payments()
        self.assertEqual(DATASET_COLS, data.columns.tolist())

    def test_house_payments_reshape_numbers_as_list(self):
        self.subject.load_source_file()
        self.subject.translate()
        data = self.subject._house_payments()
        self.assertEqual([['0']], data['numbers'].tolist())

    def test_non_house_payments_group_by_document_id(self):
        self.subject.load_source_file()
        self.subject.translate()
        data = self.subject._non_house_payments()
        self.assertEqual(sorted(DATASET_COLS), sorted(data.columns.tolist()))
        cols = ['numbers', 'total_net_value', 'total_value']
        values = [
            [['5828'], 296.0, 0.0],
            [['5868', '5869'], 300.0, 0.0],
            [['5993'], 175.0, 0.0],
            [['6041'], 100.0, 0.0],
        ]
        self.assertEqual(values, data[cols].values.tolist())
