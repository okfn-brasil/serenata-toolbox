import os
import glob
import pandas as pd
from datetime import date
from tempfile import mkdtemp
from shutil import rmtree
from unittest import main, TestCase, skip

import pandas as pd

from serenata_toolbox.chamber_of_deputies.reimbursements import Reimbursements


class TestChamberOfDeputiesReimbursements(TestCase):

    def test_call_integration(self):
        downloader = Reimbursements(date.today().year)
        downloader()
        assert(os.path.exists(downloader.path))


if __name__ == '__main__':
    main()
