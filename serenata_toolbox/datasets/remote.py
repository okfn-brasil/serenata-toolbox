import os

import boto3

from serenata_toolbox import settings
from serenata_toolbox.datasets.contextmanager import status_message


class RemoteDatasets:

    BUCKET = settings.AMAZON_BUCKET
    CREDENTIALS = (
        ('aws_access_key_id', settings.AMAZON_ACCESS_KEY),
        ('aws_secret_access_key', settings.AMAZON_SECRET_KEY),
        ('region_name', settings.AMAZON_REGION),
    )

    def __init__(self):
        self.client = None
        self.credentials = {k: v for k, v in self.CREDENTIALS if v}

    @property
    def s3(self):
        if not self.client:
            self.client = boto3.client('s3', **self.credentials)
        return self.client

    @property
    def all(self):
        response = self.s3.list_objects(Bucket=self.BUCKET)
        yield from (obj.get('Key') for obj in response.get('Contents', []))

    def upload(self, file_path):
        _, file_name = os.path.split(file_path)
        with status_message('Uploading {}…'.format(file_name)):
            self.s3.upload_file(file_path, self.BUCKET, file_name)

    def delete(self, file_name):
        with status_message('Deleting {}…'.format(file_name)):
            self.s3.delete_object(Bucket=self.BUCKET, Key=file_name)
