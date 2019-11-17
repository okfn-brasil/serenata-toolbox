import re
import sqlite3
from functools import partial
from gzip import GzipFile
from pathlib import Path

from serenata_toolbox import log
from serenata_toolbox.companies.cnae import Cnae
from serenata_toolbox.companies.google_drive import GoogleDriveFile
from serenata_toolbox.companies.open_street_maps import Nominatim


class Database:
    """This database abstraction downloads the SQLite file from Brasil.IO and
    offersa wrapper to make queries easier. Data is complemented with
    economic activities (CNAE) description that comes from a separate file from
    the Federal Revenue, and with geo-coordinates from Open Street Maps."""

    DEFAULT_FILENAME = "socios-brasil.sqlite"

    def __init__(self, path="data"):
        self.compressed = Path(path) / f"{self.DEFAULT_FILENAME}.gz"
        self.decompressed = Path(path) / self.DEFAULT_FILENAME

        if not self.compressed.exists():
            GoogleDriveFile(self.compressed).download()

        if not self.decompressed.exists():
            self.decompress()

        self.cnae = Cnae()
        self.nominatim = Nominatim()

        self._to_close = []  # objects to close on self.close()
        self._cursor = None  # cache

    def decompress(self):
        log.info(f"Decompressing {self.compressed} to {self.decompressed}…")
        with GzipFile(self.compressed, mode="rb") as compressed:
            with self.decompressed.open("wb") as decompressed:
                chunck = compressed.read(self.CHUNK)
                while chunck:
                    decompressed.write(chunck)
                    chunck = compressed.read(self.CHUNK)

    @property
    def cursor(self):
        if self._cursor:
            return self._cursor

        conn = sqlite3.connect(str(self.decompressed))
        self._to_close.append(conn)
        self._cursor = conn.cursor()
        self.assure_indexes()
        return self._cursor

    def assure_indexes(self):
        log.debug("Creating database indexes (if needed)…")
        tables = ("empresa", "socio", "cnae_secundaria")
        for table in tables:
            sql = f"""
                CREATE INDEX IF NOT EXISTS idx_{table}_cnpj
                ON {table} (cnpj);
            """
            self.cursor.execute(sql)

    @staticmethod
    def _row_to_dict(keys, row, include_cnpj=False):
        obj = dict(zip(keys, row))
        if include_cnpj:
            return obj
        return {k: v for k, v in obj.items() if k != "cnpj"}

    def _get_by_cnpj(self, cnpj, table, unique=False):
        cnpj = re.sub(r"\D", "", cnpj)
        self.cursor.execute(f"SELECT * FROM {table} WHERE cnpj = '{cnpj}'")
        result = self.cursor.fetchone() if unique else self.cursor.fetchall()
        if not result:
            return

        keys = tuple(obj[0] for obj in self.cursor.description)
        if unique:
            return self._row_to_dict(keys, result, include_cnpj=True)

        return tuple(self._row_to_dict(keys, row) for row in result)

    async def get_company(self, session, cnpj):
        get = partial(self._get_by_cnpj, cnpj)
        company = get("empresa", unique=True)
        if not company:
            return

        company["partners"] = get("socio")
        company["secondary_activities"] = get("cnae_secundaria")

        # add secondary activities descriptions
        if company["secondary_activities"]:
            for activity in company["secondary_activities"]:
                activity["code"] = activity.pop("cnae", None)
                activity["name"] = self.cnae(activity["code"])

        # add latitude/longitude
        street = (
            company["numero"],
            company["descricao_tipo_logradouro"],
            company["logradouro"],
        )
        cep = str(company["cep"])
        params = {
            "street": " ".join(street),
            "city": company["municipio"],
            "state": company["uf"],
            "postalcode": "-".join((cep[:5], cep[5:])),
        }
        log.debug(f"Getting {company['cnpj']} coordinates…")
        coordinates = await self.nominatim.coordinates(session, **params)
        company.update(coordinates)
        return company

    def close(self):
        for obj in self._to_close[::-1]:
            obj.close()
