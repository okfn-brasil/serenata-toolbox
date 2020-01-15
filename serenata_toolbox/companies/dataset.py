import asyncio
import json
import re
from datetime import date, datetime
from pathlib import Path

import aiohttp
import numpy as np
import pandas as pd
from tqdm import tqdm

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

    def __init__(self, path="data", header="cnpj_cpf"):
        """The `path` parameter expects directory with datasets (CSV or
        LZMA) containing the `header` column."""
        self.path = Path(path)
        if not self.path.exists():
            self.path.mkdir()

        self.output = self.path / f"{date.today()}-companies.csv.xz"
        self.header = header
        self.db = Database(path)
        self._datasets, self._documents = None, None  # cache

    @property
    def datasets(self):
        if self._datasets:
            return self._datasets

        data = Path(self.path)
        extensions = ("csv", "xz")
        self._datasets = tuple(
            str(dataset.resolve())
            for extension in extensions
            for dataset in data.glob(f"*.{extension}")
            if not dataset.name.endswith("-companies.csv.xz")
        )
        return self._datasets

    @property
    def documents(self):
        if self._documents:
            return self._documents

        numbers = set()
        for dataset in self.datasets:
            log.info(f"Reading {dataset}…")
            try:
                df = pd.read_csv(
                    dataset,
                    dtype={self.header: np.str},
                    encoding="utf-8",
                    low_memory=False,
                    usecols=(self.header,),
                )
            except ValueError:
                log.info(f"Skipping {dataset} (no `{self.header}` column)")
                continue

            log.info(f"Filtering unique CNPJs from {dataset}…")
            for num in df[self.header].unique():
                if isinstance(num, str) and len(re.sub(r"\D", "", num)) == 14:
                    numbers.add(num)

        log.info(f"Consolidating {len(numbers):,} different CNPJ numbers…")
        self._documents = tuple(numbers)  # tuple is way smaller than set
        return self._documents

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
            for cnpj in tqdm(self.documents, unit="companies"):
                company = await self.db.get_company(session, cnpj)
                if not company:
                    continue

                company = self.serialize(company)
                companies.append(company)

        return companies

    def __call__(self):
        companies = asyncio.run(self.companies())
        df = pd.DataFrame(companies)
        df.to_csv(self.output, index=False, compression="xz")
        log.info(f"Comanies dataset saved to {self.output}!")
