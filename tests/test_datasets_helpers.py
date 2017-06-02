import os
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

from serenata_toolbox.datasets import helpers

class TestDatasetsHelpersXml(TestCase):

    def setUp(self):
        self.sampleXml = ET.fromstring("""<?xml version=\"1.0\" encoding=\"utf-8\"?>
        <root>
            <simpleText> Sample text </simpleText>
            <brDate>31/05/2017</brDate>
            <usDate>04/30/2017</usDate>
            <brDateTime>31/05/2017 23:59:59</brDateTime>
            <usDateTime>04/30/2017 11:59:59PM</usDateTime>
        </root>
        """)

    def test_extract_text(self):
        extracted = helpers.xml_extract_text(self.sampleXml, 'simpleText')
        expected = 'Sample text'

        self.assertEqual(expected, extracted)

    def test_extract_date_default_to_br_format(self):
        extracted = helpers.xml_extract_date(self.sampleXml, 'brDate')
        expected = datetime(2017, 5, 31, 0, 0)

        self.assertEqual(expected, extracted)

    def test_extract_date_supports_custom_format(self):
        extracted = helpers.xml_extract_date(self.sampleXml, 'usDate', '%m/%d/%Y')
        expected = datetime(2017, 4, 30, 0, 0)

        self.assertEqual(expected, extracted)

    def test_extract_datetime_default_to_br_format(self):
        extracted = helpers.xml_extract_datetime(self.sampleXml, 'brDateTime')
        expected = datetime(2017, 5, 31, 23, 59, 59)

        self.assertEqual(expected, extracted)

    def test_extract_datetime_supports_custom_format(self):
        extracted = helpers.xml_extract_datetime(self.sampleXml, 'usDateTime', '%m/%d/%Y %I:%M:%S%p')
        expected = datetime(2017, 4, 30, 23, 59, 59)

        self.assertEqual(expected, extracted)

class TestDatasetsHelpersDataframes(TestCase):

    def test_translate_column(self):
        records = [
            ['masculino'],
            ['feminino'],
            ['masculino'],
            ['feminino'],
        ]
        df = pd.DataFrame(records, columns=['gender'])

        helpers.translate_column(df, 'gender', {
            'masculino': 'male',
            'feminino': 'female',
        })
        translated = df.gender.unique()
        expected = ['male', 'female']

        self.assertTrue((np.array(expected) == np.array(translated)).all())

    @patch('pandas.DataFrame')
    def test_save_to_csv(self, mock_df):
        today = datetime.strftime(datetime.now(), '%Y-%m-%d')
        helpers.save_to_csv(mock_df, '../data', 'sample-data')

        mock_df.to_csv.assert_called_with(
            '../data/{}-sample-data.xz'.format(today),
            compression='xz',
            encoding='utf-8',
            index=False
        )
