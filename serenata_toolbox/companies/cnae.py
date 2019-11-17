import re
from tempfile import NamedTemporaryFile

import requests
from openpyxl import load_workbook

from serenata_toolbox import log


class Cnae:
    """This database abstraction complements the CNPJ dataset with economic
    activities (CNAE) description that comes from a separate file from the
    Federal Revenue."""

    CHUNK = 2 ** 12
    CNAE_DESCRIPTION_FILE = (
        "https://cnae.ibge.gov.br"
        "/images/concla/documentacao/"
        "CNAE_Subclasses_2_3_Estrutura_Detalhada.xlsx"
    )

    def __init__(self):
        self._activities = dict()  # cache

    @staticmethod
    def parse_code(code):
        if not code:
            return

        cleaned = re.sub(r"\D", "", code)
        try:
            return int(cleaned)
        except ValueError:
            return

    def load_activities(self):
        log.info("Fetching CNAE descriptions…")
        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            response = requests.get(self.CNAE_DESCRIPTION_FILE)

            with open(tmp.name, "wb") as fobj:
                log.debug(f"Dowloading {response.url} to {tmp.name}…")
                for chunk in response.iter_content(self.CHUNK):
                    if chunk:
                        fobj.write(chunk)

            wb = load_workbook(tmp.name)
            for row in wb.active.rows:
                code = self.parse_code(row[4].value)
                description = row[5].value
                if not all((code, description)):
                    continue

                self._activities[code] = description

    @property
    def activities(self):
        """Dictionary with the descriptions of the economic activity (CNAE)
        not included in the Reveita Federal dataset."""
        if self._activities:
            return self._activities

        self.load_activities()
        return self._activities

    def __call__(self, code):
        return self.activities.get(code)
