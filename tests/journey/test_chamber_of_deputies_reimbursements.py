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

        for year in range(2009, date.today().year + 1):
            downloader = Reimbursements(year)
            downloader()
            assert(os.path.exists(downloader.path))

if __name__ == '__main__':
    main()
