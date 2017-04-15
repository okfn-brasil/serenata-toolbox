import os
from configparser import NoSectionError, RawConfigParser
from functools import partial
from unittest import TestCase
from unittest.mock import patch

from serenata_toolbox.datasets.remote import RemoteDatasets


class TestLocal(TestCase):

    @patch('serenata_toolbox.datasets.remote.print')
    @patch('serenata_toolbox.datasets.remote.os.path.exists')
    def test_init_without_config_ini(self, exists, print_):
        exists.return_value = False
        remote = RemoteDatasets()
        with self.assertRaises(AttributeError):
            remote.s3
        with self.assertRaises(AttributeError):
            remote.bucket
        self.assertTrue(print_.called)

    @patch('serenata_toolbox.datasets.remote.print')
    @patch('serenata_toolbox.datasets.remote.os.path.exists')
    @patch('serenata_toolbox.datasets.remote.os.path.isfile')
    def test_init_with_config_ini_as_directory(self, exists, is_file, print_):
        exists.return_value = True
        is_file.return_value = False
        remote = RemoteDatasets()
        with self.assertRaises(AttributeError):
            remote.s3
        with self.assertRaises(AttributeError):
            remote.bucket
        self.assertTrue(print_.called)

    @patch.object(RawConfigParser, 'read')
    @patch('serenata_toolbox.datasets.remote.print')
    @patch('serenata_toolbox.datasets.remote.os.path.exists')
    @patch('serenata_toolbox.datasets.remote.os.path.isfile')
    def test_init_with_inproper_config_ini(self, exists, is_file, print_, read):
        exists.return_value = True
        is_file.return_value = True
        remote = RemoteDatasets()
        with self.assertRaises(AttributeError):
            remote.s3
        with self.assertRaises(AttributeError):
            remote.bucket
        self.assertTrue(print_.called)

    @patch('serenata_toolbox.datasets.remote.boto3')
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    def test_successful_init(self, raw_config_parser, boto3):
        raw_config_parser.return_value.get.side_effect = (
            'YOUR_ACCESS_KEY',
            'YOUR_SECRET_KEY',
            'sa-east-1',
            'serenata-de-amor-data'
        )
        credentials = {
            'aws_access_key_id': 'YOUR_ACCESS_KEY',
            'aws_secret_access_key': 'YOUR_SECRET_KEY',
            'region_name': 'sa-east-1'
        }
        remote = RemoteDatasets()
        self.assertEqual('serenata-de-amor-data', remote.bucket)
        self.assertEqual(credentials, remote.credentials)

    @patch('serenata_toolbox.datasets.remote.boto3')
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    def test_all(self, raw_config_parser, boto3):
        response = {'Contents': [{'Key': 'file1.xz'}, {'Key': 'file2.xz'}]}
        boto3.client.return_value.list_objects.return_value = response
        remote = RemoteDatasets()
        self.assertEqual(('file1.xz', 'file2.xz'), tuple(remote.all))

    @patch('serenata_toolbox.datasets.contextmanager.print')
    @patch('serenata_toolbox.datasets.remote.boto3')
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    def test_upload(self, raw_config_parser, boto3, print_):
        raw_config_parser.return_value.get.side_effect = (
            'YOUR_ACCESS_KEY',
            'YOUR_SECRET_KEY',
            'sa-east-1',
            'serenata-de-amor-data'
        )
        remote = RemoteDatasets()
        remote.upload('/root/serenata/data/42.csv')
        boto3.client.return_value.upload_file.assert_called_once_with(
            '/root/serenata/data/42.csv',
            'serenata-de-amor-data',
            '42.csv'
        )

    @patch('serenata_toolbox.datasets.contextmanager.print')
    @patch('serenata_toolbox.datasets.remote.boto3')
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    def test_delete(self, raw_config_parser, boto3, print_):
        raw_config_parser.return_value.get.side_effect = (
            'YOUR_ACCESS_KEY',
            'YOUR_SECRET_KEY',
            'sa-east-1',
            'serenata-de-amor-data'
        )
        remote = RemoteDatasets()
        remote.delete('42.csv')
        boto3.client.return_value.delete_object.assert_called_once_with(
            Bucket='serenata-de-amor-data',
            Key='42.csv'
        )
