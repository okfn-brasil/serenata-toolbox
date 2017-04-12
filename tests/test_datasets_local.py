import os
from unittest import TestCase
from unittest.mock import patch

from serenata_toolbox.datasets.local import LocalDatasets


class TestLocal(TestCase):

    @patch('serenata_toolbox.datasets.local.os.path.isdir')
    @patch('serenata_toolbox.datasets.local.os.path.exists')
    def test_init(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        local = LocalDatasets('test')
        self.assertTrue(local.directory.endswith(os.sep + 'test'))

    @patch('serenata_toolbox.datasets.local.os.path.isdir')
    @patch('serenata_toolbox.datasets.local.os.path.exists')
    def test_init_with_file_path(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = False
        with self.assertRaises(FileNotFoundError):
            LocalDatasets('test')

    @patch('serenata_toolbox.datasets.local.os.path.isdir')
    @patch('serenata_toolbox.datasets.local.os.path.exists')
    def test_init_non_existent_dir(self, exists, isdir):
        exists.return_value = False
        isdir.return_value = False
        with self.assertRaises(FileNotFoundError):
            LocalDatasets('test')

    @patch('serenata_toolbox.datasets.local.os.listdir')
    @patch('serenata_toolbox.datasets.local.os.path.isfile')
    @patch('serenata_toolbox.datasets.local.os.path.isdir')
    @patch('serenata_toolbox.datasets.local.os.path.exists')
    def test_all(self, exists, isdir, isfile, listdir):
        exists.return_value = True
        isdir.return_value = True
        isfile.side_effect = (True, False, True)
        listdir.return_value = range(3)
        local = LocalDatasets('test')
        self.assertEqual((0, 2), tuple(local.all))


    @patch('serenata_toolbox.datasets.contextmanager.print')
    @patch('serenata_toolbox.datasets.local.os.remove')
    @patch('serenata_toolbox.datasets.local.os.path.isfile')
    @patch('serenata_toolbox.datasets.local.os.path.isdir')
    @patch('serenata_toolbox.datasets.local.os.path.exists')
    def test_delete(self, exists, isdir, isfile, remove, print_):
        exists.return_value = True
        isdir.return_value = True
        isfile.return_value = True
        local = LocalDatasets('test')
        local.delete('42')
        expected = os.path.join(os.path.abspath('test'), '42')
        remove.assert_called_once_with(expected)

    @patch('serenata_toolbox.datasets.local.os.path.isfile')
    @patch('serenata_toolbox.datasets.local.os.path.isdir')
    @patch('serenata_toolbox.datasets.local.os.path.exists')
    def test_delete_dir(self, exists, isdir, isfile):
        exists.return_value = True
        isdir.return_value = True
        isfile.return_value = False
        local = LocalDatasets('test')
        with self.assertRaises(FileNotFoundError):
            local.delete('test')

    @patch('serenata_toolbox.datasets.local.os.remove')
    @patch('serenata_toolbox.datasets.local.os.path.isfile')
    @patch('serenata_toolbox.datasets.local.os.path.isdir')
    @patch('serenata_toolbox.datasets.local.os.path.exists')
    def test_delete_non_existent_file(self, exists, isdir, isfile, remove):
        exists.side_effect = (True, False)
        isdir.return_value = True
        isfile.return_value = False
        local = LocalDatasets('test')
        with self.assertRaises(FileNotFoundError):
            local.delete('test')
