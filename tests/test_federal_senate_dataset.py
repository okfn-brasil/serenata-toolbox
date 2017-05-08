import os
from tempfile import gettempdir
from unittest import main, skipIf, TestCase, TestLoader

from serenata_toolbox.federal_senate.federal_senate_dataset import FederalSenateDataset

if os.environ.get('RUN_INTEGRATION_TESTS') == '1':
    TestLoader.sortTestMethodsUsing = None

class TestFederalSenateDataset(TestCase):
    def setUp(self):
        self.path = gettempdir()
        self.subject = FederalSenateDataset(self.path)

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_fetch_saves_raw_files(self):
        self.subject.fetch()
        names = ['federal-senate-{}.csv'.format(year) for year in range(2008, 2018)]
        for name in names:
            file_path = os.path.join(self.path, name)
            assert(os.path.exists(file_path))

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_translate_creates_english_versions_for_every_csv(self):
        self.subject.translate()
        names = ['federal-senate-{}.xz'.format(year) for year in range(2008, 2018)]
        for name in names:
            file_path = os.path.join(self.path, name)
            assert(os.path.exists(file_path))

if __name__ == '__main__':
    main()