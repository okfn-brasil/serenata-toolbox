import urllib
import xml.etree.ElementTree as ET

import pandas as pd

from serenata_toolbox import log
from serenata_toolbox.datasets.helpers import (
    save_to_csv,
    translate_column,
    xml_extract_text,
)


class DeputiesDataset:

    URL = 'http://www.camara.leg.br/SitCamaraWS/deputados.asmx/ObterDeputados'

    def fetch(self):
        """
        Fetches the list of deputies for the current term.
        """
        xml = urllib.request.urlopen(self.URL)

        tree = ET.ElementTree(file=xml)
        records = self._parse_deputies(tree.getroot())

        df = pd.DataFrame(records, columns=(
            'congressperson_id',
            'budget_id',
            'condition',
            'congressperson_document',
            'civil_name',
            'congressperson_name',
            'picture_url',
            'gender',
            'state',
            'party',
            'phone_number',
            'email'
        ))
        return self._translate(df)

    @staticmethod
    def _parse_deputies(root):
        for deputy in root:
            yield (
                xml_extract_text(deputy, 'ideCadastro'),
                xml_extract_text(deputy, 'codOrcamento'),
                xml_extract_text(deputy, 'condicao'),
                xml_extract_text(deputy, 'matricula'),
                xml_extract_text(deputy, 'nome'),
                xml_extract_text(deputy, 'nomeParlamentar'),
                xml_extract_text(deputy, 'urlFoto'),
                xml_extract_text(deputy, 'sexo'),
                xml_extract_text(deputy, 'uf'),
                xml_extract_text(deputy, 'partido'),
                xml_extract_text(deputy, 'fone'),
                xml_extract_text(deputy, 'email'),
            )

    @staticmethod
    def _translate(df):
        translate_column(df, 'gender', {
            'masculino': 'male',
            'feminino': 'female',
        })

        translate_column(df, 'condition', {
            'Titular': 'Holder',
            'Suplente': 'Substitute',
        })

        return df


def fetch_deputies(data_dir):
    """
    :param data_dir: (str) directory in which the output file will be saved
    """
    deputies = DeputiesDataset()
    df = deputies.fetch()
    save_to_csv(df, data_dir, "deputies")

    holders = df.condition == 'Holder'
    substitutes = df.condition == 'Substitute'
    log.info("Total deputies:", len(df))
    log.info("Holder deputies:", len(df[holders]))
    log.info("Substitute deputies:", len(df[substitutes]))
    return df
