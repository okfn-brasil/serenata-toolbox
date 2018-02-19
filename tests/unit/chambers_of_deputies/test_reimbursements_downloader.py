import os.path
from unittest import TestCase
from unittest.mock import patch

from serenata_toolbox.chamber_of_deputies.reimbursements_downloader import \
    URL, ReimbursementsDownloader


class TestReimbursementsDownloader(TestCase):
    def setUp(self):
        self.subject = ReimbursementsDownloader(2017)

    @patch.object(ReimbursementsDownloader, 'fetch')
    @patch.object(ReimbursementsDownloader, 'clean')
    def test_execute_fetch_and_clean(self, clean_mock, fetch_mock):
        self.subject.execute()
        fetch_mock.assert_called_with()
        clean_mock.assert_called_with()

    @patch.object(ReimbursementsDownloader, 'fetch')
    @patch.object(ReimbursementsDownloader, 'clean')
    def test_execute_return_file_path(self, _clean_mock, _fetch_mock):
        file_path = os.path.join(self.subject.path, 'reimbursements-2017.csv')
        self.assertEqual(file_path, self.subject.execute())

    @patch('serenata_toolbox.chamber_of_deputies.reimbursements_downloader.extract_zip')
    @patch('serenata_toolbox.chamber_of_deputies.reimbursements_downloader.urlretrieve')
    def test_fetch_download_zip_file(self, urlretrieve_mock, _):
        url = URL.format(2017)
        path = os.path.join(self.subject.path, 'Ano-2017.zip')
        self.subject.fetch()
        urlretrieve_mock.assert_called_with(url, path)

    @patch('serenata_toolbox.chamber_of_deputies.reimbursements_downloader.extract_zip')
    @patch('serenata_toolbox.chamber_of_deputies.reimbursements_downloader.urlretrieve')
    def test_fetch_extract_zip(self, _, extract_zip_mock):
        file_path = os.path.join(self.subject.path, 'Ano-2017.zip')
        path = self.subject.path
        self.subject.fetch()
        extract_zip_mock.assert_called_with(file_path, path)

    @patch('serenata_toolbox.chamber_of_deputies.reimbursements_downloader.ReimbursementsCleaner')
    def test_clean_delegate_to_reimbursements_cleaner(self, cleaner_mock):
        self.subject.clean()
        cleaner_mock.return_value.execute.assert_called_with()
