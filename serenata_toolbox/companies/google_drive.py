from contextlib import contextmanager

import requests

from serenata_toolbox import log


class GoogleDriveTokenNotFound(Exception):
    pass


class GoogleDriveFile:
    """This abstraction downloads the SQLite file from Brasil.IO"""

    CHUNK = 2 ** 12
    URL = "https://docs.google.com/uc?export=download"
    DEFAULT_GOOGLE_DRIVE_FILE_ID = "19DU3bi_XycAPISWrMniMYbwoiLpAO3D4"

    def __init__(self, target, file_id=None):
        """`file_id` is the Google Drive file ID for the SQLite version of the
        database maintaned by Brasil.IO."""
        self.file_id = file_id or self.DEFAULT_GOOGLE_DRIVE_FILE_ID
        self.target = target

    def save(self, response):
        log.debug(f"Dowloading {response.url} to {self.target}…")
        with self.target.open("wb") as fobj:
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

    def download(self):
        session = requests.Session()
        with self.token(session) as token:
            params = {"id": self.file_id, "confirm": token}
            response = session.get(self.URL, params=params, stream=True)
            self.save(response)

        log.info(f"Database file ready at {self.target}")
        return self.target
