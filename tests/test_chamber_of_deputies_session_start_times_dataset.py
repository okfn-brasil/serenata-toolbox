import os
from datetime import datetime

from unittest import main, skipIf, TestCase

import numpy as np

from serenata_toolbox.chamber_of_deputies.session_start_times_dataset import SessionStartTimesDataset

class TestSpeechesDataset(TestCase):
    def setUp(self):
        self.subject = SessionStartTimesDataset()

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_fetch(self):
        pivot = 19
        df = self.subject.fetch(pivot, [
            datetime(2015, 2, 3),
            datetime(2015, 2, 4),
            datetime(2015, 2, 5)
        ])
        actualColumns = df.columns

        expectedColumns = [
            'date', 'session', 'started_at'
        ]
        self.assertTrue((np.array(expectedColumns) == np.array(actualColumns)).all())
        self.assertEqual(4, len(df))

if __name__ == '__main__':
    main()
