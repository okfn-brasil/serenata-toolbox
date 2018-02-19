import os.path
from tempfile import gettempdir
from urllib.request import urlretrieve
from zipfile import ZipFile

from .reimbursements_cleaner import ReimbursementsCleaner

URL = 'https://www.camara.leg.br/cotas/Ano-{}.csv.zip'


def extract_zip(zip_path, destination_path):
    zip_file = ZipFile(zip_path, 'r')
    zip_file.extractall(destination_path)
    zip_file.close()


class ReimbursementsDownloader:
    """
    Get an updated version of the reimbursements dataset for a given year.
    """

    def __init__(self, year, path=gettempdir()):
        self.year = year
        self.path = path

    def execute(self):
        self.fetch()
        self.clean()
        file_path = os.path.join(
            self.path, 'reimbursements-{}.csv'.format(self.year))
        return file_path

    def fetch(self):
        file_path = os.path.join(self.path, 'Ano-{}.zip'.format(self.year))
        urlretrieve(URL.format(self.year), file_path)
        extract_zip(file_path, self.path)

    def clean(self):
        ReimbursementsCleaner(self.year, self.path).execute()
