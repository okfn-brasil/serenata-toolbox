import asyncio
import json
import os
import re
from datetime import date, datetime

import aiohttp
import numpy as np
import pandas as pd

from serenata_toolbox import log
from serenata_toolbox.companies.db import Database


class Dataset:
    TRANSLATION = {
        "abertura": "opening",
        "atividade_principal": "main_activity",
        "atividades_secundarias": "secondary_activities",
        "bairro": "neighborhood",
        "capital_social": "share_capital",
        "cep": "zip_code",
        "cnae_fiscal": "main_activity_code",
        "codigo_municipio": "city_code",
        "codigo_natureza_juridica": "judicial_nature_code",
        "complemento": "additional_address_details",
        "data_exclusao_do_simples": "removed_from_simples_since",
        "data_inicio_atividade": "opened_in",
        "data_opcao_pelo_simples": "opted_for_comples_in",
        "data_situacao_cadastral": "situation_date",
        "data_situacao_especial": "special_situation_date",
        "ddd_fax": "fax_area_code",
        "ddd_telefone_1": "phone1_area_code",
        "ddd_telefone_2": "phone2_area_code",
        "descricao_tipo_logradouro": "address_type",
        "efr": "responsible_federative_entity",
        "identificador_matriz_filial": "hq_or_subsidiary_code",
        "logradouro": "address",
        "motivo_situacao_cadastral": "situation_reason",
        "municipio": "city",
        "natureza_juridica": "legal_entity",
        "nome_cidade_exterior": "city_abroad_name",
        "nome_fantasia": "trade_name",
        "numero": "number",
        "opcao_pelo_mei": "mei",
        "opcao_pelo_simples": "simples",
        "porte": "size",
        "qualificacao_do_responsavel": "administrative_person_category",
        "razao_social": "name",
        "situacao_cadastral": "situation",
        "situacao_especial": "special_situation",
        "telefone": "phone",
        "tipo": "type",
        "uf": "state",
        "ultima_atualizacao": "last_updated",
    }
    TRANSLATION_PARTNER = {
        "identificador_de_socio": "id",
        "nome_socio": "name",
        "cnpj_cpf_do_socio": "cnpj_cpf",
        "codigo_qualificacao_socio": "type",
        "percentual_capital_social": "percent_shares",
        "data_entrada_sociedade": "partner_since",
        "cpf_representante_legal": "legal_representative_document",
        "nome_representante_legal": "legal_representative_name",
        "codigo_qualificacao_representante_legal": "legal_representative_code",
    }

    def __init__(self, datasets, path="data", db=None, header="cnpj_cpf"):
        """The `datasets` parameter expects a list of paths to datasets (CSV or
        LZMA) containing the `header` column."""
        if not os.path.isdir(path):
            os.mkdir(os.path.join(path))

        self.path = path
        self.header = header
        self.db = Database(db)
        self.datasets = (datasets,) if isinstance(datasets, str) else datasets

        self.last_count_at = datetime.now()
        self.count = 0

    @staticmethod
    def is_cnpj(number):
        return len(re.sub(r"\D", "", number)) == 14

    @property
    def documents(self):
        numbers = set()
        for dataset in self.datasets:
            log.info(f"Reading {dataset}…")
            df = pd.read_csv(
                dataset,
                dtype={self.header: np.str},
                encoding="utf-8",
                low_memory=False,
                usecols=(self.header,),
            )
            log.info(f"Filtering unique CNPJs from {dataset}…")
            for number in df[self.header].unique():
                if self.is_cnpj(number):
                    numbers.add(number)

        yield from numbers

    def translate_dict_keys(self, obj, translations=None):
        translations = translations or self.TRANSLATION
        for pt, en in translations.items():
            obj[en] = obj.pop(pt, None)
        return obj

    def serialize(self, company):
        if company["partners"]:
            company["partners"] = tuple(
                self.translate_dict_keys(partner, self.TRANSLATION_PARTNER)
                for partner in company["partners"]
            )

        to_json = ("partners", "secondary_activities")
        for key in to_json:
            company[key] = json.dumps(company[key])

        return self.translate_dict_keys(company)

    async def companies(self):
        companies = []
        semaphore = asyncio.Semaphore(2 ** 12)

        async with semaphore, aiohttp.ClientSession() as session:
            for cnpj in self.documents:
                company = await self.db.get_company(session, cnpj)
                if not company:
                    continue

                company = self.serialize(company)
                self.count += 1
                companies.append(company)

                if self.count % 100 == 0:
                    self.log_count()

        if self.count % 100 != 0:
            self.log_count()

        return companies

    def log_count(self):
        now = datetime.now()
        delta = now - self.last_count_at
        ratio = self.count / delta.total_seconds()

        msg = f"{self.count:,} companies fetched ({ratio:.2f} companies/s)"
        log.info(msg)

        self.last_count_at = now

    def __call__(self):
        timestamp = str(date.today())
        path = os.path.join(self.path, f"{timestamp}-companies.csv.gz")

        companies = asyncio.run(self.companies())
        df = pd.DataFrame(companies)
        df.to_csv(path, index=False, compression="xz")
        log.info("Comanies dataset saved to {path}!")
