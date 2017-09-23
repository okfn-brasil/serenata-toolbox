import configparser
from functools import partial
import os

import boto3

from serenata_toolbox.datasets.contextmanager import status_message
from serenata_toolbox.datasets.helpers import find_config


class RemoteDatasets:

    CONFIG = 'config.ini'

    def __init__(self):
        self.credentials = None
        self.client = None
        self.config = find_config(self.CONFIG)

        if not self.config_exists:
            print('Could not find {} file.'.format(self.CONFIG))
            print('You need Amazon section in it to interact with S3')
            print('(Check config.ini.example if you need a reference.)')
            return

        settings = configparser.RawConfigParser()
        settings.read(self.config)
        self.settings = partial(settings.get, 'Amazon')

        try:
            self.credentials = {
                'aws_access_key_id': self.settings('AccessKey'),
                'aws_secret_access_key': self.settings('SecretKey'),
                'region_name': self.settings('Region')
            }

            # friendly user message warning about old config.ini version
            region = self.credentials.get('region_name', '')
            if region and region.startswith('s3-'):
                msg = (
                    'It looks like you have an old version of the config.ini '
                    'file. We do not need anymore the service (s3) appended '
                    'to the region (sa-east-1). Please update your config.ini '
                    'replacing regions like `s3-sa-east-1` by `sa-east-1`.'
                )
                print(msg)

        except configparser.NoSectionError:
            msg = (
                'You need an Amazon section in {} to interact with S3 '
                '(Check config.ini.example if you need a reference.)'
            )
            print(msg.format(self.CONFIG))

    @property
    def config_exists(self):
        return all((os.path.exists(self.config), os.path.isfile(self.config)))

    @property
    def bucket(self):
        if hasattr(self, 'settings'):
            try:
                return self.settings('Bucket')
            except configparser.NoSectionError:
                return None

    @property
    def s3(self):
        if not self.client and self.credentials:
            self.client = boto3.client('s3', **self.credentials)
        return self.client

    @property
    def all(self):
        if self.s3 and self.bucket:
            response = self.s3.list_objects(Bucket=self.bucket)
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
