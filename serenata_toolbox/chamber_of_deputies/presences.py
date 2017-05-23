import pandas as pd
import xml.etree.ElementTree as ET
import urllib

from datetime import datetime

def extract_text(node, xpath):
    return node.find(xpath).text.strip()

def extract_date(node, xpath):
    return datetime.strptime(extract_text(node, xpath), "%d/%m/%Y")

def extract_datetime(node, xpath):
    return datetime.strptime(extract_text(node, xpath), "%d/%m/%Y %H:%M:%S")

###############################################################################
## Deputies dataset

url = 'http://www.camara.leg.br/SitCamaraWS/deputados.asmx/ObterDeputados'
file=urllib.request.urlopen(url)
t = ET.ElementTree(file=file)

def parse_deputies(deputies):
    for deputy in deputies:
        budget_id = deputy.find('codOrcamento').text
        if budget_id != None:
            budget_id = budget_id.strip()
        condition = extract_text(deputy, 'condicao')
        if condition == 'Titular':
            condition = 'Holder'
        else:
            condition = 'Substitute'
        yield [
            extract_text(deputy, 'ideCadastro'),
            budget_id,
            extract_text(deputy, 'matricula'),
            condition,
            extract_text(deputy, 'nome'),
            extract_text(deputy, 'nomeParlamentar'),
            extract_text(deputy, 'uf'),
            extract_text(deputy, 'partido'),
        ]

records = parse_deputies(t.getroot())
deputies = pd.DataFrame(records, columns=[
    'congressperson_id',
    'budget_id',
    'registration',
    'condition',
    'civil_name',
    'name',
    'state',
    'party'
])
print("Total deputies:", deputies.shape[0])
print("Holder deputies:", deputies[deputies['condition'] == 'Holder'].shape[0])
print("Substitute deputies:", deputies[deputies['condition'] == 'Substitute'].shape[0])

###############################################################################
## Presence in sessions

url = (
    'http://www.camara.leg.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasParlamentar'
    '?dataIni=01/02/2015'
    '&dataFim=31/12/2016'
    '&numMatriculaParlamentar={0}'
)

def fetch_presences(filtered_deputies):
    print("Fetching data for", filtered_deputies.shape[0], "deputies")
    for i, deputy in filtered_deputies.iterrows():
        print(i, deputy['name'])
        file = urllib.request.urlopen(url.format(deputy['registration']))
        t = ET.ElementTree(file=file)
        congressperson_name = extract_text(t.getroot(), 'nomeParlamentar')
        for day in t.getroot().findall('.//dia'):
            date = extract_datetime(day, 'data')
            for session in day.findall('.//sessao'):
                yield [
                    date,
                    deputy['registration'],
                    congressperson_name,
                    extract_text(session, 'descricao'),
                    extract_text(session, 'frequencia')
                ]

records = fetch_presences(deputies[(deputies['condition'] == 'Holder') & ~deputies['budget_id'].isnull()])
presences = pd.DataFrame(records, columns=[
    'date',
    'registration',
    'congressperson_name',
    'session',
    'presence'
])
print("Presence records:", presences.shape[0])
print("Records of deputies present on a session:", presences[presences['presence'] == 'Presença'].shape[0])

###############################################################################
## Session start times

session_dates = presences.copy()
session_dates['date'] = session_dates['date'].dt.date
session_dates = session_dates.drop_duplicates('date')['date']

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

sessions = pd.DataFrame(fetch_session_start_times(), columns=[
    'date',
    'description',
    'started_at'
])

###############################################################################
## Save the data!

CSV_PARAMS = {
    'compression': 'xz',
    'encoding': 'utf-8',
    'index': False
}
deputies.to_csv('../data/2016-12-21-deputies.xz', **CSV_PARAMS)
presences.to_csv('../data/2016-12-21-presences.xz', **CSV_PARAMS)
sessions.to_csv('../data/2016-12-21-sessions.xz', **CSV_PARAMS)
