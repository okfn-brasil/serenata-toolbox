import configparser
import os

import boto3

from serenata_toolbox.datasets.contextmanager import status_message


class RemoteDatasets:

    CONFIG = 'config.ini'

    def __init__(self):
        if not all((os.path.exists(self.CONFIG), os.path.isfile(self.CONFIG))):
            print('Could not find {} file.'.format(self.CONFIG))
            print('You need Amzon section in it to interact with S3')
            print('(Check config.ini.example if you need a reference.)')
            return

        self.settings = configparser.RawConfigParser()
        self.settings.read(self.CONFIG)

        try:
            self.credentials = dict(
                aws_access_key_id=self.settings.get('Amazon', 'AccessKey'),
                aws_secret_access_key=self.settings.get('Amazon', 'SecretKey'),
                region_name=self.settings.get('Amazon', 'Region')
            )
            self.bucket = self.settings.get('Amazon', 'Bucket')

        except configparser.NoSectionError:
            msg = 'You need Amzon section in {}  to interact with S3'
            print(msg.format(self.CONFIG))
            print('(Check config.ini.example if you need a reference.)')
            return

        else:
            self.s3 = boto3.client('s3', **self.credentials)

    @property
    def all(self):
        if self.s3 and self.bucket:
            response =  self.s3.list_objects(Bucket=self.bucket)
            yield from (obj.get('Key') for obj in response.get('Contents', []))

    def upload(self, file_path):
        if self.s3 and self.bucket:
            _, file_name = os.path.split(file_path)
            with status_message('Uploading {}…'.format(file_name)):
                self.s3.upload_file(file_path, self.bucket, file_name)

    def delete(self, file_name):
        if self.s3 and self.bucket:
            with status_message('Deleting {}…'.format(file_name)):
                self.s3.delete_object(Bucket=self.bucket, Key=file_name)
