from unittest import TestCase

import numpy as np
import pandas as pd
from numpy.testing import assert_array_equal

from serenata_toolbox.chamber_of_deputies.reimbursements import Reimbursements


class TestReimbursements(TestCase):

    def setUp(self):
        self.dataset = pd.read_csv('tests/unit/receipts.csv',
                                    dtype={'cnpj_cpf': np.str})
        self.subject = Reimbursements('tests')

    def test_aggregates_partial_reimbursements_in_single_record(self):
        receipts = self.subject.read_csv('unit/receipts.csv')
        aggregated = self.subject.group(receipts)
        numbers = aggregated['reimbursement_numbers']
        assert_array_equal(np.r_[90], aggregated['total_net_value'])
        assert_array_equal(np.r_[90], aggregated['reimbursement_value_total'])
        assert_array_equal(numbers[0].split(', '),
                           aggregated['reimbursement_numbers'][0].split(', '))
