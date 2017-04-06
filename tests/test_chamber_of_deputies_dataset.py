import os
import glob
from datetime import date
from tempfile import gettempdir
from unittest import main, skipIf, TestCase, TestLoader

from serenata_toolbox.chamber_of_deputies.chamber_of_deputies_dataset import ChamberOfDeputiesDataset

if os.environ.get('RUN_INTEGRATION_TESTS') == '1':
    TestLoader.sortTestMethodsUsing = None

class TestChamberOfDeputiesDataset(TestCase):
    def setUp(self):
        self.path = gettempdir()
        self.subject = ChamberOfDeputiesDataset(self.path)
        self.years = [n for n in range(2009, date.today().year + 1)]


    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_fetch_translate_clean_integration(self):
        # cleaning up previous tests
        try:
            os.remove(os.path.join(self.path, "datasets-format.html"))
        except:
            pass
        for filename in glob.glob(os.path.join(self.path, "Ano-*")):
            os.remove( filename )
        for filename in glob.glob(os.path.join(self.path, "reimbursements*")):
            os.remove( filename )

        self.subject.fetch()
        files = ["Ano-{}.csv".format(n) for n in self.years]
        files.append('datasets-format.html')

        for name in files:
            file_path = os.path.join(self.path, name)
            assert(os.path.exists(file_path))

        self.subject.translate()
        for name in ["reimbursements-{}.xz".format(n) for n in self.years]:
            file_path = os.path.join(self.path, name)
            assert(os.path.exists(file_path))

        self.subject.clean()
        file_path = os.path.join(self.path, 'reimbursements.xz')
        assert(os.path.exists(file_path))

if __name__ == '__main__':
    main()
