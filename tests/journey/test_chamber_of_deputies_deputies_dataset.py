import os
from unittest import main, skipIf, TestCase

import numpy as np

from serenata_toolbox.chamber_of_deputies.deputies_dataset import DeputiesDataset

class TestDeputiesDataset(TestCase):
    def setUp(self):
        self.subject = DeputiesDataset()

    def test_fetch(self):
        df = self.subject.fetch()
        actualColumns = df.columns

        expectedColumns = [
            'congressperson_id', 'budget_id', 'condition',
            'congressperson_document', 'civil_name', 'congressperson_name',
            'picture_url', 'gender', 'state', 'party', 'phone_number', 'email'
        ]
        self.assertTrue((np.array(expectedColumns) == np.array(actualColumns)).all())

        expectedGenders = ['male', 'female']
        actualGenders = df.gender.unique()
        self.assertTrue((np.array(expectedGenders) == np.array(actualGenders)).all())

        expectedConditions = ['Holder', 'Substitute']
        actualConditions = df.condition.unique()
        self.assertTrue((np.array(expectedConditions) == np.array(actualConditions)).all())

if __name__ == '__main__':
    main()
