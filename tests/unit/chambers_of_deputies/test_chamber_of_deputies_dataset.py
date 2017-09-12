import csv
import lzma
import os
from shutil import copy, rmtree
from tempfile import mkdtemp
from unittest import TestCase
from unittest.mock import patch

import numpy as np
import pandas as pd

from serenata_toolbox.chamber_of_deputies.dataset import Dataset


class TestChamberOfDeputiesDataset(TestCase):

    def setUp(self):
        self.path = mkdtemp(prefix='serenata-')
        print(self.path)
        self.subject = Dataset(self.path, [2017])
        self.years = [2017]
        self.fixtures_path = os.path.join('tests', 'fixtures', 'chamber_of_deputies')

    def tearDown(self):
        rmtree(self.path, ignore_errors=True)

    @patch('serenata_toolbox.chamber_of_deputies.dataset.urlretrieve')
    def test_fetch_chambers_of_deputies_datasets(self, mocked_urlretrieve):
        path_to_2017_dataset_zip = os.path.join(self.fixtures_path, 'Ano-2017.zip')
        path_to_dataset_format_html = os.path.join(self.fixtures_path, 'datasets-format.html')
        copy(path_to_2017_dataset_zip, self.path)
        copy(path_to_dataset_format_html, self.path)
        expected_files = ['Ano-2017.zip', 'datasets-format.html']

        retrieved_files = self.subject.fetch()

        self.assertTrue(mocked_urlretrieve.called)
        self.assertEqual(mocked_urlretrieve.call_count, len(expected_files))
        for retrieved_file, expected_file in zip(retrieved_files, expected_files):
            self.assertIn(expected_file, retrieved_file)

    def test_translate_2017_dataset(self):
        xz_path = os.path.join(self.path, 'reimbursements-2017.xz')
        csv_path = os.path.join(self.fixtures_path, 'Ano-2017.csv')
        copy(csv_path, self.path)

        data_frame_2017_as_csv = self._read_csv(csv_path)
        self._assert_that_the_columns_are_as_expected_before_translation(data_frame_2017_as_csv)

        self.subject.translate()
        reimbursements_2017 = self._read_xz(xz_path)

        self._assert_that_the_columns_are_as_expected_after_translation(reimbursements_2017)

    def test_clean_2017_reimbursements(self):
        copy(os.path.join(self.fixtures_path, 'reimbursements-2017.xz'), self.path)
        file_path = os.path.join(self.path, 'reimbursements.xz')

        self.subject.clean()

        assert(os.path.exists(file_path))

        dataset = pd.read_csv(file_path, compression='xz')
        all_subquotas = [subquota[1] for subquota in self.subject.subquotas]

        present_subquotas = pd.unique(dataset['subquota_description'])
        for subquota in present_subquotas:
            with self.subTest():
                assert(subquota in all_subquotas)

    def test_translate_csv_with_reimbursement_with_net_value_with_comma(self):
        csv_with_comma = os.path.join(self.fixtures_path, 'Ano-with-comma.csv')
        with open(os.path.join(self.fixtures_path, 'reimbursements-with-comma'), 'r') as csv_expected:
            expected = csv_expected.read()
        
        xz_output = Dataset('')._translate_file(csv_with_comma)
        output = lzma.open(xz_output).read().decode('utf-8')
        assert(output == expected)

    def _read_csv(self, path):
        return pd.read_csv(path,
                           decimal=',',
                           encoding='utf-8',
                           delimiter=";",
                           quoting=csv.QUOTE_NONE,
                           dtype={'ideDocumento': np.str,
                                  'idecadastro': np.str,
                                  'nuCarteiraParlamentar': np.str,
                                  'codLegislatura': np.str,
                                  'txtCNPJCPF': np.str,
                                  'numRessarcimento': np.str},
                           )

    def _read_xz(self, filepath):
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

    def _assert_that_the_columns_are_as_expected_before_translation(self, data_frame_2017):
        expected_columns = self.subject.translate_columns.keys()

        for column in expected_columns:
            with self.subTest():
                self.assertIn(column, data_frame_2017.columns)

    def _assert_that_the_columns_are_as_expected_after_translation(self, reimbursements):
        expected_columns = expected_columns = self.subject.translate_columns.values()

        for column in expected_columns:
            with self.subTest():
                self.assertIn(column, reimbursements.columns)
