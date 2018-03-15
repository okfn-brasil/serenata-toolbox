import os
from unittest import TestCase
from unittest.mock import PropertyMock, patch

from serenata_toolbox.datasets.remote import RemoteDatasets
from serenata_toolbox import settings



class TestRemote(TestCase):

    def test_init(self):
        """Test the RemoteDatasets properly load storage info from settings"""
        remote = RemoteDatasets()
        expected_credentials = (
            ('aws_access_key_id', settings.AMAZON_ACCESS_KEY),
            ('aws_secret_access_key', settings.AMAZON_SECRET_KEY),
            ('region_name', settings.AMAZON_REGION)
        )
        self.assertEqual(remote.BUCKET, settings.AMAZON_BUCKET)
        self.assertEqual(remote.CREDENTIALS, expected_credentials)

    @patch('serenata_toolbox.datasets.remote.boto3')
    def test_s3(self, boto3):
        remote = RemoteDatasets()
        remote.credentials = dict(test=42)
        self.assertIsNotNone(remote.s3)
        boto3.client.assert_called_once_with('s3', test=42)

    @patch.object(RemoteDatasets, 's3', new_callable=PropertyMock)
    @patch.object(RemoteDatasets, 'BUCKET', new_callable=PropertyMock)
    def test_all(self, bucket, s3):
        response = {'Contents': [{'Key': 'file1.xz'}, {'Key': 'file2.xz'}]}
        s3.return_value.list_objects.return_value = response
        bucket.return_value = 'bucket'
        remote = RemoteDatasets()
        self.assertEqual(('file1.xz', 'file2.xz'), tuple(remote.all))

    @patch('serenata_toolbox.datasets.contextmanager.print')
    @patch.object(RemoteDatasets, 's3', new_callable=PropertyMock)
    @patch.object(RemoteDatasets, 'BUCKET', new_callable=PropertyMock)
    def test_upload(self, bucket, s3, print_):
        bucket.return_value = 'serenata-de-amor-data'
        remote = RemoteDatasets()
        remote.upload('/root/serenata/data/42.csv')
        s3.return_value.upload_file.assert_called_once_with(
            '/root/serenata/data/42.csv',
            'serenata-de-amor-data',
            '42.csv'
        )

    @patch('serenata_toolbox.datasets.contextmanager.print')
    @patch.object(RemoteDatasets, 's3', new_callable=PropertyMock)
    @patch.object(RemoteDatasets, 'BUCKET', new_callable=PropertyMock)
    def test_delete(self, bucket, s3, print_):
        bucket.return_value = 'serenata-de-amor-data'
        remote = RemoteDatasets()
        remote.delete('42.csv')
        s3.return_value.delete_object.assert_called_once_with(
            Bucket='serenata-de-amor-data',
            Key='42.csv'
        )
