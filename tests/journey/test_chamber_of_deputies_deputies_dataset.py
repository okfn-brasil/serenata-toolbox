import os
from unittest import main, skipIf, TestCase

import numpy as np

from serenata_toolbox.chamber_of_deputies.deputies_dataset import DeputiesDataset

class TestDeputiesDataset(TestCase):
    def setUp(self):
        self.subject = DeputiesDataset()

    def test_fetch(self):
        df = self.subject.fetch()
        actualColumns = set(df.columns)

        expectedColumns = {
            'congressperson_id', 'budget_id', 'condition',
            'congressperson_document', 'civil_name', 'congressperson_name',
            'picture_url', 'gender', 'state', 'party', 'phone_number', 'email'
        }
        self.assertTrue((np.array(expectedColumns) == np.array(actualColumns)).all())

        expectedGenders = {'male', 'female'}
        actualGenders = set(df.gender.unique())
        self.assertTrue(expectedGenders, actualGenders)

        expectedConditions = {'Substitute', 'Holder'}
        actualConditions = set(df.condition.unique())
        self.assertEqual(expectedConditions, actualConditions)

if __name__ == '__main__':
    main()
