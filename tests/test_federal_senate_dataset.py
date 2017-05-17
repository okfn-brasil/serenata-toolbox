from tempfile import gettempdir
from unittest import TestCase
from unittest.mock import patch


from serenata_toolbox.federal_senate.federal_senate_dataset import FederalSenateDataset


class TestFederalSenateDataset(TestCase):
    def setUp(self):
        self.path = gettempdir()
        print(self.path)
        self.subject = FederalSenateDataset(self.path)

    @patch("serenata_toolbox.federal_senate.federal_senate_dataset.urlretrieve")
    def test_mocking_fetch(self, mockedUrlRetrieve):
        self.subject.fetch()
        self.assertTrue(mockedUrlRetrieve.called)
