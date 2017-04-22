from configparser import NoSectionError, RawConfigParser
from unittest import TestCase
from unittest.mock import PropertyMock, patch

from serenata_toolbox.datasets.remote import RemoteDatasets


class TestRemote(TestCase):

    @patch('serenata_toolbox.datasets.remote.os.path.exists')
    @patch('serenata_toolbox.datasets.remote.os.path.isfile')
    def test_config_exists_when_it_doesnt_exist(self, is_file, exists):
        exists.return_value = False
        is_file.return_value = False
        remote = RemoteDatasets()
        self.assertFalse(remote.config_exists)

    @patch('serenata_toolbox.datasets.remote.os.path.exists')
    @patch('serenata_toolbox.datasets.remote.os.path.isfile')
    def test_config_exists_when_it_is_a_directory(self, is_file, exists):
        exists.return_value = True
        is_file.return_value = False
        remote = RemoteDatasets()
        self.assertFalse(remote.config_exists)

    @patch('serenata_toolbox.datasets.remote.os.path.exists')
    @patch('serenata_toolbox.datasets.remote.os.path.isfile')
    def test_config_exists_when_it_is_a_file(self, is_file, exists):
        exists.return_value = True
        is_file.return_value = True
        remote = RemoteDatasets()
        self.assertTrue(remote.config_exists)

    @patch.object(RemoteDatasets, 'config_exists', new_callable=PropertyMock)
    @patch('serenata_toolbox.datasets.remote.print')
    def test_init_without_config(self, print_, config_exist):
        config_exist.return_value = False
        remote = RemoteDatasets()
        self.assertIsNone(remote.s3)
        self.assertIsNone(remote.bucket)
        self.assertTrue(print_.called)

    @patch.object(RemoteDatasets, 'config_exists', new_callable=PropertyMock)
    @patch('serenata_toolbox.datasets.remote.boto3')
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    def test_successful_init(self, raw_config_parser, boto3, config_exists):
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

    @patch.object(RemoteDatasets, 'config_exists', new_callable=PropertyMock)
    def test_bucket_no_config(self, config_exists):
        config_exists.return_value = False
        remote = RemoteDatasets()
        self.assertIsNone(remote.bucket)

    @patch.object(RemoteDatasets, 'config_exists', new_callable=PropertyMock)
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    def test_bucket_no_section(self, raw_config_parser, config_exists):
        config_exists.return_value = True
        raw_config_parser.return_value.get.side_effect = NoSectionError('foo')
        remote = RemoteDatasets()
        self.assertIsNone(remote.bucket)

    @patch.object(RemoteDatasets, 'config_exists', new_callable=PropertyMock)
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    def test_bucket(self, raw_config_parser, config_exists):
        config_exists.return_value = True
        raw_config_parser.return_value.get.return_value = 42
        remote = RemoteDatasets()
        self.assertEqual(42, remote.bucket)

    @patch.object(RemoteDatasets, 'config_exists', new_callable=PropertyMock)
    @patch('serenata_toolbox.datasets.remote.configparser.RawConfigParser')
    @patch('serenata_toolbox.datasets.remote.boto3')
    def test_s3(self, boto3, raw_config_parser, config_exists):
        config_exists.return_value = True
        remote = RemoteDatasets()
        remote.credentials = dict(test=42)
        self.assertIsNotNone(remote.s3)
        boto3.client.assert_called_once_with('s3', test=42)
        remote.client = remote.s3

    @patch.object(RemoteDatasets, 'config_exists')
    @patch.object(RemoteDatasets, 's3', new_callable=PropertyMock)
    @patch.object(RemoteDatasets, 'bucket', new_callable=PropertyMock)
    def test_all(self, bucket, s3, config_exists):
        response = {'Contents': [{'Key': 'file1.xz'}, {'Key': 'file2.xz'}]}
        s3.return_value.list_objects.return_value = response
        bucket.return_value = 'bucket'
        remote = RemoteDatasets()
        self.assertEqual(('file1.xz', 'file2.xz'), tuple(remote.all))

    @patch('serenata_toolbox.datasets.contextmanager.print')
    @patch.object(RemoteDatasets, 'config_exists')
    @patch.object(RemoteDatasets, 's3', new_callable=PropertyMock)
    @patch.object(RemoteDatasets, 'bucket', new_callable=PropertyMock)
    def test_upload(self, bucket, s3, config_exists, print_):
        bucket.return_value = 'serenata-de-amor-data'
        remote = RemoteDatasets()
        remote.upload('/root/serenata/data/42.csv')
        s3.return_value.upload_file.assert_called_once_with(
            '/root/serenata/data/42.csv',
            'serenata-de-amor-data',
            '42.csv'
        )

    @patch('serenata_toolbox.datasets.contextmanager.print')
    @patch.object(RemoteDatasets, 'config_exists')
    @patch.object(RemoteDatasets, 's3', new_callable=PropertyMock)
    @patch.object(RemoteDatasets, 'bucket', new_callable=PropertyMock)
    def test_delete(self, bucket, s3, config_exists, print_):
        bucket.return_value = 'serenata-de-amor-data'
        remote = RemoteDatasets()
        remote.delete('42.csv')
        s3.return_value.delete_object.assert_called_once_with(
            Bucket='serenata-de-amor-data',
            Key='42.csv'
        )
