from unittest import TestCase, main
from serenata_toolbox.reimbursements import Reimbursements


class TestReimbursements(TestCase):

    def test_it_works(self):
        subject = Reimbursements('/tmp')
        self.assertEqual(4, 2 + 2)
