import os

from serenata_toolbox.datasets.contextmanager import status_message


class LocalDatasets:

    def __init__(self, directory):
        if not all((os.path.exists(directory), os.path.isdir(directory))):
            raise FileNotFoundError('{} is not a directory'.format(directory))

        self.directory = os.path.abspath(directory)

    @property
    def all(self):
        yield from filter(self._is_file, os.listdir(self.directory))

    def delete(self, file_name):
        full_path = os.path.join(self.directory, file_name)
        if not all((os.path.exists(full_path), os.path.isfile(full_path))):
            raise FileNotFoundError('{} is not a flile'.format(full_path))

        with status_message('Deleting {}…'.format(file_name)):
            os.remove(full_path)

    def _is_file(self, filename):
        full_path = os.path.join(self.directory, filename)
        return os.path.isfile(full_path)
