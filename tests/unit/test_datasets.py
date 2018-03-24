from unittest import TestCase
from unittest.mock import patch

from serenata_toolbox.datasets import Datasets, fetch, fetch_latest_backup


class TestDatasets(TestCase):

    @patch('serenata_toolbox.datasets.LocalDatasets')
    @patch('serenata_toolbox.datasets.Downloader')
    def test_init_without_local_directory(self, downloader, local):
        Datasets()
        local.assert_called_once_with('data')
        downloader.assert_called_once_with('data', timeout=None)

    @patch('serenata_toolbox.datasets.LocalDatasets')
    @patch('serenata_toolbox.datasets.Downloader')
    def test_init_with_local_directory(self, downloader, local):
        Datasets('test')
        local.assert_called_once_with('test')
        downloader.assert_called_once_with('test', timeout=None)


class TestFetch(TestCase):

    @patch('serenata_toolbox.datasets.Datasets')
    def test_fetch(self, datasets):
        fetch('file.xz', 'test')
        datasets.assert_called_once_with('test')
        datasets.return_value.downloader.download.assert_called_once_with('file.xz')

    @patch('serenata_toolbox.datasets.Datasets')
    def test_fetch_latest_backup(self, datasets):
        fetch_latest_backup('test')
        self.assertTrue(datasets.return_value.downloader.download.called)

    @patch('os.path.exists')
    @patch('serenata_toolbox.datasets.Datasets')
    def test_fetch_latest_backup_only_when_missing(self, datasets, os_path_exists):
        datasets().downloader.LATEST = ('file1', 'file2', 'file3')
        os_path_exists.side_effect = [False, True, False]
        fetch_latest_backup('test')
        datasets.return_value.downloader.download.assert_called_once_with(('file1', 'file3'))

    @patch('os.path.exists')
    @patch('serenata_toolbox.datasets.Datasets')
    def test_fetch_latest_backup_with_force_all(self, datasets, os_path_exists):
        datasets().downloader.LATEST = ('file1', 'file2', 'file3')
        os_path_exists.side_effect = [False, True, False]
        fetch_latest_backup('test', force_all=True)
        datasets.return_value.downloader.download.assert_called_once_with(('file1', 'file2', 'file3'))
