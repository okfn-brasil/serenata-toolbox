import os
from unittest import main, skipIf, TestCase

import numpy as np
import pandas as pd

from serenata_toolbox.chamber_of_deputies.presences_dataset import PresencesDataset

class TestPresencesDataset(TestCase):
    def setUp(self):
        self.deputies = pd.DataFrame([
            ['GOULART', 361],
            ['BETO FARO', 19],
        ], columns=[
            'congressperson_name',
            'congressperson_document'
        ])
        self.subject = PresencesDataset()

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_fetch(self):
        df = self.subject.fetch(self.deputies, '02/02/2015', '05/02/2015')
        actualColumns = df.columns

        expectedColumns = [
            'term', 'congressperson_document', 'congressperson_name', 'party',
            'state', 'date', 'present_on_day', 'justification', 'session',
            'presence'
        ]
        self.assertTrue((np.array(expectedColumns) == np.array(actualColumns)).all())
        self.assertEqual(6, len(df))

if __name__ == '__main__':
    main()
