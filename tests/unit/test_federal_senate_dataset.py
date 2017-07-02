import os
import urllib
from tempfile import gettempdir
from unittest import TestCase
from unittest.mock import patch

import pandas as pd

from serenata_toolbox.federal_senate.dataset import Dataset


class TestFederalSenateDataset(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected_files = ['federal-senate-2008.csv',
                              'federal-senate-2009.csv']

    @patch('serenata_toolbox.federal_senate.dataset.urlretrieve')
    def test_fetch_files_from_S3(self, mocked_url_retrieve):
        path = gettempdir()
        subject = Dataset(path)

        retrieved_files, _ = subject.fetch()

        self.assertTrue(mocked_url_etrieve.called)
        self.assertEqual(mocked_url_etrieve.call_count, len(self.subject.years))
        for retrieved_file, expected_file in zip(
                retrieved_files, self.expected_files):

            self.assertIn(expected_file, retrieved_file)

    @patch('serenata_toolbox.federal_senate.dataset.urlretrieve')
    def test_fetch_raises_HTTPError(self, mocked_url_retrieve):
        mocked_url_retrieve.side_effect = urllib.error.HTTPError(None, None, None, None, None)
        self.path = gettempdir()
        self.subject = Dataset(self.path, [2007])

        with self.assertRaises(urllib.error.HTTPError) as context:
            subject.fetch()

        self.assertTrue(isinstance(context.exception, urllib.error.HTTPError))

    @patch('serenata_toolbox.federal_senate.dataset.urlretrieve')
    def test_fetch_raises_URLError(self, mocked_url_retrieve):
        mocked_url_retrieve.side_effect = urllib.error.URLError('tests reason')
        path = gettempdir()
        subject = Dataset(path, 2007, 2008)

        with self.assertRaises(urllib.error.URLError) as context:
            subject.fetch()

        self.assertTrue(isinstance(context.exception, urllib.error.URLError))

    def test_dataset_translation(self):
        self.subject = Dataset(os.path.join('tests', 'fixtures', 'csv'),
                               [2008])

        expected_files = ['federal-senate-2008.csv']

        translated_files, _ = subject.translate()

        for translated_file, expected_file in zip(
                translated_files, expected_files):

            self.assertIn(expected_file, translated_file)

    def test_if_translation_happened_as_expected(self):
        self.subject = Dataset(os.path.join('tests', 'fixtures', 'csv'),
                               [2008])

        file_path = os.path.join(subject.path, 'federal-senate-2008.csv')
        federal_senate_2008 = pd.read_csv(file_path,
                                          sep=';',
                                          encoding='ISO-8859-1',
                                          skiprows=1)
        self.assertIsNotNone(federal_senate_2008['ANO'],
                             'expects \'ANO\' as column in this dataset')

        subject.translate()

        translated_file_path = os.path.join(subject.path, 'federal-senate-2008.xz')
        translated_federal_senate_2008 = pd.read_csv(translated_file_path,
                                                     encoding='utf-8')

        self.assertIsNotNone(translated_federal_senate_2008['year'],
                             'expects \'year\' as column in this dataset')

        os.remove(os.path.join(subject.path, 'federal-senate-2008.xz'))

    def test_dataset_translation_failing_to_find_file(self):
        self.subject = Dataset(os.path.join('tests', 'fixtures', 'csv'),
                               [2007])

        with self.assertRaises(FileNotFoundError) as context:
            subject.translate()

        self.assertTrue(isinstance(context.exception, FileNotFoundError))

    def test_dataset_cleanup(self):
        self.subject = Dataset(os.path.join('tests', 'fixtures', 'xz'),
                               [2009])

        reimbursement_path = subject.clean()

        expected_path = os.path.join('tests',
                                     'fixtures',
                                     'xz',
                                     'federal-senate-reimbursements.xz')
        self.assertEqual(
            reimbursement_path,
            expected_path
        )

        os.remove(expected_path)
