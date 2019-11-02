from contextlib import contextmanager
from gzip import GzipFile
from tempfile import NamedTemporaryFile

import requests

from serenata_toolbox import log


class GoogleDriveTokenNotFound(Exception):
    pass


class GoogleDriveFile:
    """This abstraction downloads the SQLite file from Brasil.IO"""

    CHUNK = 2 ** 12
    URL = "https://docs.google.com/uc?export=download"
    DEFAULT_GOOGLE_DRIVE_FILE_ID = "19DU3bi_XycAPISWrMniMYbwoiLpAO3D4"

    def __init__(self, file_id=None):
        """`file_id` is the Google Drive file ID for the SQLite version of the
        database maintaned by Brasil.IO."""
        self.file_id = file_id or self.DEFAULT_GOOGLE_DRIVE_FILE_ID
        self.file = NamedTemporaryFile(suffix=".sqlite3")

    def save(self, response, target):
        log.debug(f"Dowloading {response.url} to {target}…")
        with open(target, "wb") as fobj:
            for chunk in response.iter_content(self.CHUNK):
                if chunk:
                    fobj.write(chunk)

    @contextmanager
    def token(self, session):
        params = {"id": self.file_id}
        log.debug(f"Requesting token for {self.file_id}…")
        response = session.get(self.URL, params=params, stream=True)
        token = None
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                token = value
                break

        if not token:
            raise log.error(f"Cannot get the token {self.URL}")

        yield token

    def decompress(self, path):
        log.info(f"Decompressing {path} to {self.file.name}…")
        with GzipFile(path, mode="rb") as gzip:
            with open(self.file.name, mode="wb") as fobj:
                chunck = gzip.read(self.CHUNK)
                while chunck:
                    fobj.write(chunck)
                    chunck = gzip.read(self.CHUNK)

    def download(self):
        session = requests.Session()
        with self.token(session) as token:
            params = {"id": self.file_id, "confirm": token}
            response = session.get(self.URL, params=params, stream=True)

        with NamedTemporaryFile(suffix=".gz") as tmp:
            self.save(response, tmp.name)
            self.decompress(tmp.name)

        log.info(f"Database file ready at {self.file.name}")
        return self.file.name
