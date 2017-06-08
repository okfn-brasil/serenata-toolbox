import os
from tempfile import gettempdir
from unittest import TestCase, skipIf

from serenata_toolbox.federal_senate.dataset import Dataset


class TestJourneyFederalSenateDataset(TestCase):
    def setUp(self):
        self.path = gettempdir()
        self.subject = Dataset(self.path)

    def test_journey_federal_senate_dataset(self):
        # fetch_saves_raw_files
        self.subject.fetch()
        federal_senate_csv_files = ['federal-senate-{}.csv'.format(year) for year in self.subject.year_range]
        for federal_senate_csv_file in federal_senate_csv_files:
            file_path = os.path.join(self.path, federal_senate_csv_file)
            self.assertTrue(os.path.exists(file_path), 'fetch_saves_raw_files')

        # translate_creates_english_versions_for_every_csv
        self.subject.translate()
        federal_senate_xz_files = ['federal-senate-{}.xz'.format(year) for year in self.subject.year_range]
        for federal_senate_xz_file in federal_senate_xz_files:
            file_path = os.path.join(self.path, federal_senate_xz_file)
            self.assertTrue(os.path.exists(file_path), 'translate_creates_english_versions_for_every_csv')

        # clean_creates_a_reimbursements_file
        self.subject.clean()
        file_path = os.path.join(self.path, 'federal-senate-reimbursements.xz')
        self.assertTrue(os.path.exists(file_path), 'clean_creates_a_reimbursements_file')
