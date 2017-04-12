import configparser
import os

import boto3

from serenata_toolbox.datasets.contextmanager import status_message


class RemoteDatasets:

    def __init__(self):
        self.settings = configparser.RawConfigParser()
        self.settings.read('config.ini')
        self.credentials = {
            'aws_access_key_id': self.settings.get('Amazon', 'AccessKey'),
            'aws_secret_access_key': self.settings.get('Amazon', 'SecretKey'),
            'region_name': self.settings.get('Amazon', 'Region')
        }
        self.s3 = boto3.client('s3', **self.credentials)
        self.bucket = self.settings.get('Amazon', 'Bucket')

    @property
    def all(self):
        response =  self.s3.list_objects(Bucket=self.bucket)
        yield from (obj.get('Key') for obj in response.get('Contents', []))

    def upload(self, file_path):
        _, file_name = os.path.split(file_path)
        with status_message('Uploading {}…'.format(file_name)):
            self.s3.upload_file(file_path, self.bucket, file_name)

    def delete(self, file_name):
        with status_message('Deleting {}…'.format(file_name)):
            self.s3.delete_object(Bucket=self.bucket, Key=file_name)
