import os
import urllib
import xml.etree.ElementTree as ET
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
    return node.find(xpath).text.strip()

def extract_date(node, xpath):
    return datetime.strptime(extract_text(node, xpath), "%d/%m/%Y")

def extract_datetime(node, xpath):
    return datetime.strptime(extract_text(node, xpath), "%d/%m/%Y %H:%M:%S")


###############################################################################
## Deputies dataset


class Deputies:

    URL = 'http://www.camara.leg.br/SitCamaraWS/deputados.asmx/ObterDeputados'

    def __init__(self):
        html = urllib.request.urlopen(self.URL)
        self.tree = ET.ElementTree(file=html)
        self.deputies = self.parse_deputies()
        self.data_frame = self.create_data_frame()

        holders = self.data_frame.condition == 'Holder'
        substitutes = self.data_frame.condition == 'Substitute'
        print("Total deputies:", len(self.data_frame))
        print("Holder deputies:", len(self.data_frame[holders]))
        print("Substitute deputies:", len(self.data_frame[substitutes]))

    def parse_deputies(self):
        for deputy in self.tree.getroot():
            budget_id = deputy.find('codOrcamento').text
            if budget_id != None:
                budget_id = budget_id.strip()

            condition = extract_text(deputy, 'condicao')
            if condition == 'Titular':
                condition = 'Holder'
            else:
                condition = 'Substitute'

            yield (
                extract_text(deputy, 'ideCadastro'),
                budget_id,
                extract_text(deputy, 'matricula'),
                condition,
                extract_text(deputy, 'nome'),
                extract_text(deputy, 'nomeParlamentar'),
                extract_text(deputy, 'uf'),
                extract_text(deputy, 'partido'),
            )

    def create_data_frame(self):
        columns = (
            'congressperson_id',
            'budget_id',
            'congressperson_document',
            'condition',
            'civil_name',
            'congressperson_name',
            'state',
            'party'
        )
        return pd.DataFrame(self.deputies, columns=columns)

    def write(self, data_dir):
        file_path = os.path.join(data_dir, '{}-deputies.xz'.format(TODAY))
        self.data_frame.to_csv(file_path, **CSV_PARAMS)


###############################################################################
## Presence in sessions

class Presences:

    URL = (
        'http://www.camara.leg.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasParlamentar'
        '?dataIni=01/02/2015'
        '&dataFim=31/12/2016'
        '&numMatriculaParlamentar={0}'
    )

    def __init__(self, deputies):
        self.deputies = self.filter(deputies)
        print("Fetching data for {} deputies".format(len(self.deputies)))

        self.presences = (self.deputy_presences(d) for d in self.all_presences)
        self.data_frame = self.create_data_frame()

        presences = self.data_frame[self.data_frame['presence'] == True]
        print("Presence records:", len(self.data_frame))
        print("Records of deputies present on a session:", len(presences))

    @staticmethod
    def filter(deputies):
        """Keep holders with budget id only."""
        return deputies[(deputies.condition == 'Holder') \
                        & ~deputies.budget_id.isnull()]

    @property
    def all_presences(self):
        for i, deputy in self.deputies.iterrows():
            print(i, deputy['congressperson_name'])
            url = self.URL.format(deputy['congressperson_document'])
            print(url)
            html = urllib.request.urlopen(url)
            yield {
                'congressperson_name': deputy['congressperson_name'],
                'congressperson_document': deputy['congressperson_document'],
                'tree': ET.ElementTree(file=html).getroot()
            }

    def deputy_presences(self, **kwargs):
        congressperson_name = kwargs.get('congressperson_name')
        congressperson_document = kwargs.get('congressperson_document')
        tree = kwargs.get('tree')

        for day in tree.findall('.//dia'):
            date = extract_datetime(day, 'data')
            for session in day.findall('.//sessao'):
                presence_str = extract_text(session, 'frequencia')
                presence = presence_str.lower() in ('presença', 'presenca')

                yield (
                    date,
                    congressperson_document,
                    congressperson_name,
                    extract_text(session, 'descricao'),
                    presence
                )

    def create_data_frame(self):
        columns = (
            'date',
            'congressperson_document',
            'congressperson_name',
            'session',
            'presence'
        )
        return pd.DataFrame(self.presences, columns=columns)

    def write(self, data_dir):
        file_path = os.path.join(data_dir, '{}-presences.xz'.format(TODAY))
        self.data_frame.to_csv(file_path, **CSV_PARAMS)


###############################################################################
## Session start times

class StartTimes:
    # session_dates = presences.copy()
    # session_dates['date'] = session_dates['date'].dt.date
    # session_dates = session_dates.drop_duplicates('date')['date']

    pivot = 361 # ANTONIO GOULART DOS REIS
    url = (
        'http://www.camara.leg.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasDia'
        '?siglaPartido=&siglaUF='
        '&data={0}'
        '&numMatriculaParlamentar={1}'
    )

    def fetch_session_start_times():
        for date in session_dates:
            print(date.strftime("%d/%m/%Y"))
            file = urllib.request.urlopen(url.format(date.strftime("%d/%m/%Y"), pivot))
            t = ET.ElementTree(file=file)
            for session in t.getroot().findall('.//sessaoDia'):
                yield [
                    date,
                    extract_text(session, 'descricao'),
                    extract_datetime(session, 'inicio')
                ]

    # sessions = pd.DataFrame(fetch_session_start_times(), columns=[
    #     'date',
    #     'description',
    #     'started_at'
    # ])

###############################################################################
## Save the data!


if __name__ == '__main__':
    deputies = Deputies()
    deputies.write('data/')

    presences = Presences(deputies.data_frame)
    presences.write('data/')

    # sessions.to_csv('../data/2016-12-21-sessions.xz', **CSV_PARAMS)
