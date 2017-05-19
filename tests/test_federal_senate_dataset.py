from tempfile import gettempdir
from unittest import TestCase
from unittest.mock import patch


from serenata_toolbox.federal_senate.federal_senate_dataset import FederalSenateDataset


class TestFederalSenateDataset(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expected_files = ['federal-senate-2008.csv',
                              'federal-senate-2009.csv']

    @patch("serenata_toolbox.federal_senate.federal_senate_dataset.urlretrieve")
    def test_fetch_files_from_S3(self, mockedUrlRetrieve):
        self.path = gettempdir()
        self.subject = FederalSenateDataset(self.path)

        retrieved_files, not_found_files = self.subject.fetch()

        self.assertTrue(mockedUrlRetrieve.called)
        self.assertEqual(mockedUrlRetrieve.call_count, 10)
        for retrieved_file, expected_file in zip(
                retrieved_files, self.expected_files):

            self.assertIn(expected_file, retrieved_file)

    def test_fetch_not_found_files_from_S3(self):
        self.path = gettempdir()
        self.subject = FederalSenateDataset(self.path, 2007, 2008)

        retrieved_files, not_found_files = self.subject.fetch()

        for not_found_file, expected_file in zip(
                not_found_files, self.expected_files):

            self.assertIn('federal-senate-2007.csv', not_found_file)

    def test_dataset_translation(self):
        self.subject = FederalSenateDataset('tests/fixtures/csv/', 2008, 2009)

        expected_files = ['federal-senate-2008.csv']

        translated_files, not_found_files = self.subject.translate()

        for translated_file, expected_file in zip(
                translated_files, expected_files):

            self.assertIn(expected_file, translated_file)

    def test_dataset_translation_failing_to_find_file(self):
        self.subject = FederalSenateDataset('tests/fixtures/csv/', 2007, 2008)

        expected_files = ['federal-senate-2007.csv']

        translated_files, not_found_files = self.subject.translate()

        for not_found_files, expected_file in zip(
                not_found_files, expected_files):

            self.assertIn(expected_file, not_found_files)

    def test_dataset_cleanup(self):
        self.subject = FederalSenateDataset('tests/fixtures/xz/', 2008, 2010)

        reimbursement_path = self.subject.clean()

        self.assertEqual(
            reimbursement_path,
            'tests/fixtures/xz/federal-senate-reimbursements.xz'
        )
