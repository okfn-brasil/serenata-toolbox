import os
import urllib
import xml.etree.ElementTree as ET
import socket
import time

import pandas as pd

from serenata_toolbox import log
from serenata_toolbox.datasets.helpers import (
    save_to_csv,
    translate_column,
    xml_extract_datetime,
    xml_extract_text,
)


class PresencesDataset:

    URL = (
        'http://www.camara.leg.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasParlamentar'
        '?dataIni={}'
        '&dataFim={}'
        '&numMatriculaParlamentar={}'
    )

    """
    :param sleep_interval: (integer) the amount of seconds to sleep between requests
    """
    def __init__(self, sleep_interval=2):
        self.sleep_interval = sleep_interval

    def fetch(self, deputies, start_date, end_date):
        """
        :param deputies: (pandas.DataFrame) a dataframe with deputies data
        :param date_start: (str) date in the format dd/mm/yyyy
        :param date_end: (str) date in the format dd/mm/yyyy
        """
        log.debug("Fetching data for {} deputies from {} -> {}".format(len(deputies), start_date, end_date))

        records = self._all_presences(deputies, start_date, end_date)

        df = pd.DataFrame(records, columns=(
            'term',
            'congressperson_document',
            'congressperson_name',
            'party',
            'state',
            'date',
            'present_on_day',
            'justification',
            'session',
            'presence'
        ))
        return self._translate(df)

    def _all_presences(self, deputies, start_date, end_date):
        error_count = 0
        for i, deputy in deputies.iterrows():
            log.debug(i, deputy.congressperson_name, deputy.congressperson_document)
            url = self.URL.format(start_date, end_date, deputy.congressperson_document)
            xml = self._try_fetch_xml(10, url)

            if xml is None:
                error_count += 1
            else:
                root = ET.ElementTree(file=xml).getroot()
                for presence in self._parse_deputy_presences(root):
                    yield presence

            time.sleep(self.sleep_interval)

        log.debug("\nErrored fetching", error_count, "deputy presences")

    def _try_fetch_xml(self, attempts, url):
        while attempts > 0:
            try:
                return urllib.request.urlopen(url, data=None, timeout=10)
            except urllib.error.HTTPError as err:
                log.error("HTTP Error", err.code, "when loading URL", url)
                # 500 seems to be the error code for "no data found for the
                # params provided"
                if err.code == 500:
                    log.info("Skipping [HTTP Status 500] {}".format(url))
                    return None
                time.sleep(self.sleep_interval / 2)
                attempts -= 1
                if attempts > 0:
                    log.info("Trying again", attempts)
                else:
                    log.error("FAIL {}".format(url))
            except socket.error as socketerror:
                log.error("Socket error:", socketerror)
                time.sleep(self.sleep_interval * 10)
                attempts -= 1
                if attempts > 0:
                    log.info("Trying again", attempts)
                else:
                    log.error("FAIL {}".format(url))

    @staticmethod
    def _parse_deputy_presences(root):
        term = xml_extract_text(root, 'legislatura')
        congressperson_document = xml_extract_text(root, 'carteiraParlamentar')
        # Please note that this name contains the party and state
        congressperson_name = xml_extract_text(root, 'nomeParlamentar')
        party = xml_extract_text(root, 'siglaPartido')
        state = xml_extract_text(root, 'siglaUF')

        for day in root.findall('.//dia'):
            date = xml_extract_datetime(day, 'data')
            present_on_day = xml_extract_text(day, 'frequencianoDia')
            justification = xml_extract_text(day, 'justificativa')
            for session in day.findall('.//sessao'):
                yield (
                    term,
                    congressperson_document,
                    congressperson_name,
                    party,
                    state,
                    date,
                    present_on_day,
                    justification,
                    xml_extract_text(session, 'descricao'),
                    xml_extract_text(session, 'frequencia')
                )

    @staticmethod
    def _translate(df):
        translate_column(df, 'presence', {
            'Presença': 'Present',
            'Ausência': 'Absent',
        })

        translate_column(df, 'present_on_day', {
            'Presença (~)': 'Present (~)',
            'Presença': 'Present',
            'Ausência': 'Absent',
            'Ausência justificada': 'Justified absence',
        })

        translate_column(df, 'justification', {
            '': '',
            'Atendimento a Obrigação Político-Partidária':
                'Attending to Political-Party Obligation',
            'Ausência Justificada':
                'Justified absence',
            'Decisão da Mesa':
                'Board decision',
            'Licença para Tratamento de Saúde':
                'Health Care Leave',
            'Missão Autorizada':
                'Authorized Mission',
            'Presença Eletrônica Aferida no Painel':
                'Electronic Presence Measured on the Panel'
        })

        return df


def fetch_presences(data_dir, deputies, date_start, date_end):
    """
    :param data_dir: (str) directory in which the output file will be saved
    :param deputies: (pandas.DataFrame) a dataframe with deputies data
    :param date_start: (str) a date in the format dd/mm/yyyy
    :param date_end: (str) a date in the format dd/mm/yyyy
    """
    presences = PresencesDataset()
    df = presences.fetch(deputies, date_start, date_end)
    save_to_csv(df, data_dir, "presences")

    log.info("Presence records:", len(df))
    log.info("Records of deputies present on a session:", len(df[df.presence == 'Present']))
    log.info("Records of deputies absent from a session:", len(df[df.presence == 'Absent']))

    return df
