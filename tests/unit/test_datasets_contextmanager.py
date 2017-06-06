from unittest import TestCase
from unittest.mock import call, patch

from serenata_toolbox.datasets.contextmanager import status_message

class TestContextManager(TestCase):

    @patch('serenata_toolbox.datasets.contextmanager.print')
    def test_status_message(self, print_):
        with status_message('test'):
            pass
        print_.assert_has_calls((
            call('test', end=' '),
            call('Done!')
        ))
