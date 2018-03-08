import os

from serenata_toolbox import log
from serenata_toolbox.datasets.downloader import Downloader
from serenata_toolbox.datasets.local import LocalDatasets
from serenata_toolbox.datasets.remote import RemoteDatasets


class Datasets:
    """
    This is a wrapper for three different classes that together handle the
    datasets (locally and remotely).

    Datasets class takes one argument: the path to the local directory of the
    dataset files (e.g. data/ or /tmp/serenata-data). The argument is optional
    and the default value is data/ (following the default usage in the main
    repo, serenata-de-amor).

    The remote part of the class expect to find Amazon credentials in
    environment variables.

    Inside it object there are three main objects: local, remote, and
    downloader:

    * `Datasets.local` handles listing all local datasets through the property
      `Datasets.local.all` (hint: it's a generator) and deleting local datasets
      with the method `Datasets.local.delete(filename)`;

    * `Datasets.remote` has the `Datasets.remote.all` property (hint: it's also
      a generator) and `Dataset.remote.delete(filename)` method just like its
      local equivalent; in addition to them this object offers the
      `Datasets.remote.upload(file_path)` method to upload a local file to the
      remote bucket; `Datasets.remote` does not handles downloads because
      `boto3` does not support `asyncio` and we prefer to use async tasks to
      allow the download of more than one file in parallel;

    * `Datasets.downloader` implements a async manager to download files from
      the remote bucket. It's `Datasets.downloader.download(files)` take the
      path for a single file (str) as argument or an iterable of paths (str).

    Yet this wrapper implement the `Dataset.upload_all()` method to upload all
    local datasets that are not present in the remote bucket.

    :param local_directory: (str) path to local directory of the datasets
    :param timeout: (float) timeout parameter to Downloader,
           None or 0 disables timeout check.
    """

    def __init__(self, local_directory=None, timeout=None):
        if not local_directory:
            local_directory = 'data'

        self.local = LocalDatasets(local_directory)
        self.remote = RemoteDatasets()
        self.downloader = Downloader(
            local_directory,
            bucket=self.remote.bucket,
            timeout=timeout,
            **self.remote.credentials
        )

    @property
    def pending(self):
        """Files that are in the local datasets but not in S3."""
        local = set(self.local.all)
        remote = set(self.remote.all)
        yield from (local - remote)

    def upload_all(self):
        for file_name in self.pending:
            full_path = os.path.join(self.local.directory, file_name)
            self.remote.upload(full_path)


# shortcuts & retrocompatibility

def fetch(filename, destination_path):
    datasets = Datasets(destination_path)
    return datasets.downloader.download(filename)


def fetch_latest_backup(destination_path, force_all=False):
    datasets = Datasets(destination_path)

    if force_all:
        files = datasets.downloader.LATEST
    else:
        files = tuple(
            f for f in datasets.downloader.LATEST
            if not os.path.exists(os.path.join(destination_path, f))
        )

    if not files:
        log.info('You already have all the latest datasets! Nothing to download.')

    return datasets.downloader.download(files)
