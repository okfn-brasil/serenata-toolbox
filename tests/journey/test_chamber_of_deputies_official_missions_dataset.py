import os
from datetime import date

from unittest import main, TestCase

import numpy as np

from serenata_toolbox.chamber_of_deputies.official_missions_dataset import OfficialMissionsDataset

class TestOfficialMissionsDataset(TestCase):
    def setUp(self):
        self.subject = OfficialMissionsDataset()

    def test_fetch(self):
        df = self.subject.fetch(date(2017, 1, 1), date(2017, 2, 28))
        actualColumns = df.columns

        expectedColumns = [
            'participant', 'destination', 'subject', 'start', 'end',
            'canceled', 'report_status', 'report_details_link'
        ]
        self.assertTrue(np.array_equal(expectedColumns, actualColumns))
        self.assertEqual(56, len(df))

        expectedCanceled = ['No', 'Yes']
        actualCanceled = df.canceled.unique()
        self.assertTrue(np.array_equal(np.array(expectedCanceled), np.array(actualCanceled)))

if __name__ == '__main__':
    main()
