import os
from unittest import main, skipIf, TestCase

import numpy as np

from serenata_toolbox.chamber_of_deputies.speeches_dataset import SpeechesDataset

class TestSpeechesDataset(TestCase):
    def setUp(self):
        self.subject = SpeechesDataset()

    @skipIf(os.environ.get('RUN_INTEGRATION_TESTS') != '1',
            'Skipping integration test')
    def test_fetch(self):
        df = self.subject.fetch('03/02/2015', '03/02/2015')
        actualColumns = df.columns

        expectedColumns = [
            'session_code', 'session_date', 'session_num', 'phase_code',
            'phase_desc', 'speech_speaker_num', 'speech_speaker_name',
            'speech_speaker_party', 'speech_speaker_state',
            'speech_started_at', 'speech_room_num', 'speech_insertion_num'
        ]
        self.assertTrue((np.array(expectedColumns) == np.array(actualColumns)).all())
        self.assertEqual(208, len(df))

if __name__ == '__main__':
    main()
