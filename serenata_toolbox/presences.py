import os
import urllib
import xml.etree.ElementTree as ET
import time
import socket
from datetime import datetime

import numpy as np
import pandas as pd


CSV_PARAMS = {
    'compression': 'xz',
    'encoding': 'utf-8',
    'index': False
}

TODAY = datetime.strftime(datetime.now(), '%Y-%m-%d')


def extract_text(node, xpath):
    text = node.find(xpath).text
    if text != None:
        text = text.strip()
    return text

def extract_date(node, xpath):
    return datetime.strptime(extract_text(node, xpath), "%d/%m/%Y")

def extract_datetime(node, xpath):
    return datetime.strptime(extract_text(node, xpath), "%d/%m/%Y %H:%M:%S")

def translate_column(df, column, translations):
    df[column] = df[column].astype('category')
    translations = [translations[cat]
                   for cat in df[column].cat.categories]

    df[column].cat.rename_categories(translations,
                                     inplace=True)


###############################################################################
## Deputies dataset


class Deputies:

    URL = 'http://www.camara.leg.br/SitCamaraWS/deputados.asmx/ObterDeputados'

    def fetch(self):
        """
        Fetches the list of deputies for the current term.
        """
        xml = urllib.request.urlopen(self.URL)

        tree = ET.ElementTree(file=xml)
        records = self.__parse_deputies(tree.getroot())

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
        return self.__translate(df)

    def __parse_deputies(self, root):
        for deputy in root:
            yield (
                extract_text(deputy, 'ideCadastro'),
                extract_text(deputy, 'codOrcamento'),
                extract_text(deputy, 'condicao'),
                extract_text(deputy, 'matricula'),
                extract_text(deputy, 'nome'),
                extract_text(deputy, 'nomeParlamentar'),
                extract_text(deputy, 'urlFoto'),
                extract_text(deputy, 'sexo'),
                extract_text(deputy, 'uf'),
                extract_text(deputy, 'partido'),
                extract_text(deputy, 'fone'),
                extract_text(deputy, 'email'),
            )

    def __translate(self, df):
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
    file_path = os.path.join(data_dir, '{}-deputies.xz'.format(TODAY))

    deputies = Deputies()
    df = deputies.fetch()
    df.to_csv(file_path, **CSV_PARAMS)

    holders = df.condition == 'Holder'
    substitutes = df.condition == 'Substitute'
    print("Total deputies:", len(df))
    print("Holder deputies:", len(df[holders]))
    print("Substitute deputies:", len(df[substitutes]))
    return df


###############################################################################
## Presence in sessions


class Presences:

    URL = (
        'http://www.camara.leg.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasParlamentar'
        '?dataIni={}'
        '&dataFim={}'
        '&numMatriculaParlamentar={}'
    )

    def fetch(self, deputies, start_date, end_date):
        """
        :param deputies: (pandas.DataFrame) a dataframe with deputies data
        :param date_start: (str) date in the format dd/mm/yyyy
        :param date_end: (str) date in the format dd/mm/yyyy
        """
        print("Fetching data for {} deputies from {} -> {}".format(len(deputies), start_date, end_date))

        records = self.__all_presences(deputies, start_date, end_date)

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
        return self.__translate(df)

    def __all_presences(self, deputies, start_date, end_date):
        error_count = 0
        for i, deputy in deputies.iterrows():
            print(i, deputy.congressperson_name, deputy.congressperson_document)
            url = self.URL.format(start_date, end_date, deputy.congressperson_document)
            xml = self.__try_fetch_xml(10, url)

            if xml == None:
                error_count += 1
            else:
                root = ET.ElementTree(file=xml).getroot()
                for presence in self.__parse_deputy_presences(root):
                    yield presence

            time.sleep(2)

        print("\nErrored fetching", error_count, "deputy presences")

    def __try_fetch_xml(self, attempts, url):
        while attempts > 0:
            try:
                return urllib.request.urlopen(url, data=None, timeout=10)
            except urllib.error.HTTPError as err:
                print("HTTP Error", err.code, "when loading URL", url)
                # 500 seems to be the error code for "no data found for the
                # params provided"
                if err.code == 500:
                    print("SKIP")
                    return None
                time.sleep(2)
                attempts -= 1
                if attempts > 0:
                    print("Trying again", attempts)
                else:
                    print("FAIL")
            except socket.error as socketerror:
                print("Socket error:", socketerror)
                time.sleep(20)
                attempts -= 1
                if attempts > 0:
                    print("Trying again", attempts)
                else:
                    print("FAIL")


    def __parse_deputy_presences(self, root):
        term = extract_text(root, 'legislatura')
        congressperson_document = extract_text(root, 'carteiraParlamentar')
        # Please note that this name contains the party and state
        congressperson_name = extract_text(root, 'nomeParlamentar')
        party = extract_text(root, 'siglaPartido')
        state = extract_text(root, 'siglaUF')

        for day in root.findall('.//dia'):
            date = extract_datetime(day, 'data')
            present_on_day = extract_text(day, 'frequencianoDia')
            justification = extract_text(day, 'justificativa')
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
                    extract_text(session, 'descricao'),
                    extract_text(session, 'frequencia')
                )

    def __translate(self, df):
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
    file_path = os.path.join(data_dir, '{}-presences.xz'.format(TODAY))

    presences = Presences()
    df = presences.fetch(deputies, date_start, date_end)
    df.to_csv(file_path, **CSV_PARAMS)

    print("Presence records:", len(df))
    print("Records of deputies present on a session:", len(df[df.presence == 'Present']))
    print("Records of deputies absent from a session:", len(df[df.presence == 'Absent']))

    return df


###############################################################################
## Session start times


class SessionStartTimes:
    URL = (
        'http://www.camara.leg.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasDia'
        '?siglaPartido=&siglaUF='
        '&data={0}'
        '&numMatriculaParlamentar={1}'
    )

    def fetch(self, pivot, session_dates):
        """
        :param pivot: (int) a congressperson document to use as a pivot for scraping the data
        :param session_dates: (str) a list of datetime objects to fetch the start times for
        """

        records = self.__all_start_times(pivot, session_dates)
        return pd.DataFrame(records, columns=(
            'date',
            'session',
            'started_at'
        ))

    def __all_start_times(self, pivot, session_dates):
        for date in session_dates:
            print(date.strftime("%d/%m/%Y"))
            file = urllib.request.urlopen(self.URL.format(date.strftime("%d/%m/%Y"), pivot))
            t = ET.ElementTree(file=file)
            for session in t.getroot().findall('.//sessaoDia'):
                yield (
                    date,
                    extract_text(session, 'descricao'),
                    extract_datetime(session, 'inicio')
                )

def fetch_session_start_times(data_dir, pivot, session_dates):
    """
    :param data_dir: (str) directory in which the output file will be saved
    :param pivot: (int) a congressperson document to use as a pivot for scraping the data
    :param session_dates: (str) a list of datetime objects to fetch the start times for
    """
    file_path = os.path.join(data_dir, '{}-session-start-times.xz'.format(TODAY))

    session_start_times = SessionStartTimes()
    df = session_start_times.fetch(pivot, session_dates)
    df.to_csv(file_path, **CSV_PARAMS)

    print("Dates requested:", len(session_dates))
    found = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S").dt.date.unique()
    print("Dates found:", len(found))
    return df
