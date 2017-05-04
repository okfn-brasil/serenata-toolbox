import os
from tempfile import gettempdir
from unittest import main, skipIf, TestCase, TestLoader

from serenata_toolbox.chamber_of_deputies.chamber_of_deputies_dataset import ChamberOfDeputiesDataset

if os.environ.get('RUN_INTEGRATION_TESTS') == '1':
    TestLoader.sortTestMethodsUsing = None

class TestChamberOfDeputiesDataset(TestCase):
    def setUp(self):
        self.path = gettempdir()
        self.subject = ChamberOfDeputiesDataset(self.path)

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_fetch_saves_raw_files(self):
        self.subject.fetch()
        for name in ['AnoAtual.xml', 'AnoAnterior.xml', 'AnosAnteriores.xml', 'datasets-format.html']:
            file_path = os.path.join(self.path, name)
            assert(os.path.exists(file_path))

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_convert_to_csv_creates_csvs_for_every_xml_from_fetch(self):
        self.subject.convert_to_csv()
        for name in ['AnoAtual.csv', 'AnoAnterior.csv', 'AnosAnteriores.csv']:
            file_path = os.path.join(self.path, name)
            assert(os.path.exists(file_path))

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_translate_creates_english_versions_for_every_csv(self):
        self.subject.translate()
        for name in ['current-year.xz', 'last-year.xz', 'previous-years.xz']:
            file_path = os.path.join(self.path, name)
            assert(os.path.exists(file_path))

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_clean_creates_a_reimbursements_file(self):
        self.subject.clean()
        file_path = os.path.join(self.path, 'reimbursements.xz')
        assert(os.path.exists(file_path))

if __name__ == '__main__':
    main()
