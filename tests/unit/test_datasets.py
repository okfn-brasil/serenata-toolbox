import os
from unittest import TestCase
from unittest.mock import call, patch

from serenata_toolbox.datasets import Datasets, fetch, fetch_latest_backup


class TestDatasets(TestCase):

    @patch('serenata_toolbox.datasets.LocalDatasets')
    @patch('serenata_toolbox.datasets.RemoteDatasets')
    @patch('serenata_toolbox.datasets.Downloader')
    def test_init_without_local_directory(self, downloader, remote, local):
        remote.return_value.bucket = 'mybucket'
        remote.return_value.credentials = dict(user='user', password='password')
        Datasets()
        local.assert_called_once_with('data')
        remote.assert_called_once_with()
        downloader.assert_called_once_with(
            'data',
            bucket='mybucket',
            user='user',
            password='password'
        )

    @patch('serenata_toolbox.datasets.LocalDatasets')
    @patch('serenata_toolbox.datasets.RemoteDatasets')
    @patch('serenata_toolbox.datasets.Downloader')
    def test_init_with_local_directory(self, downloader, remote, local):
        remote.return_value.bucket = 'mybucket'
        remote.return_value.credentials = dict(user='user', password='password')
        Datasets('test')
        local.assert_called_once_with('test')
        remote.assert_called_once_with()
        downloader.assert_called_once_with(
            'test',
            bucket='mybucket',
            user='user',
            password='password'
        )

    @patch('serenata_toolbox.datasets.LocalDatasets')
    @patch('serenata_toolbox.datasets.RemoteDatasets')
    @patch('serenata_toolbox.datasets.Downloader')
    def test_pending(self, downloader, remote, local):
        local.return_value.all = (1, 2, 3, 4, 5, 6)
        remote.return_value.all = (1, 3, 4)
        expected = (2, 5, 6)
        datasets = Datasets()
        self.assertEqual(expected, tuple(datasets.pending))

    @patch('serenata_toolbox.datasets.LocalDatasets')
    @patch('serenata_toolbox.datasets.RemoteDatasets')
    @patch('serenata_toolbox.datasets.Downloader')
    def test_upload_all(self, downloader, remote, local):
        local.return_value.all = ('file1.xz', 'file2.xz', 'file3.xz')
        remote.return_value.all = ('file3.xz',)
        local.return_value.directory = os.path.join('tmp', 'serenata-data')
        datasets = Datasets()
        datasets.upload_all()
        expected = [
            call(os.path.join('tmp', 'serenata-data', 'file1.xz')),
            call(os.path.join('tmp', 'serenata-data', 'file2.xz'))
        ]
        remote.return_value.upload.assert_has_calls(expected, any_order=True)


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
