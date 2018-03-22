import os

from serenata_toolbox import log, settings
from serenata_toolbox.datasets.downloader import Downloader
from serenata_toolbox.datasets.local import LocalDatasets


class Datasets:
    """
    This is a wrapper for three different classes that together handle the
    datasets locally and the download of new ones).

    Datasets class takes one argument: the path to the local directory of the
    dataset files (e.g. data/ or /tmp/serenata-data). The argument is optional
    and the default value is data/ (following the default usage in the main
    repo, serenata-de-amor).

    Inside this object there are two main objects: local and downloader:

    * `Datasets.local` handles listing all local datasets through the property
      `Datasets.local.all` (hint: it's a generator) and deleting local datasets
      with the method `Datasets.local.delete(filename)`;

    * `Datasets.downloader` implements a async manager to download files from
      the remote bucket. It's `Datasets.downloader.download(files)` take the
      path for a single file (str) as argument or an iterable of paths (str).

    :param local_directory: (str) path to local directory of the datasets
    :param timeout: (float) timeout parameter to Downloader,
           None or 0 disables timeout check.
    """

    def __init__(self, local_directory=None, timeout=None):
        if not local_directory:
            local_directory = 'data'

        self.local = LocalDatasets(local_directory)
        self.downloader = Downloader(local_directory, timeout=timeout)


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
