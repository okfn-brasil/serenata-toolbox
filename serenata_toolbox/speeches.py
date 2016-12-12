import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import urllib

from datetime import datetime

class Speeches:

    URL = 'http://www.camara.leg.br/SitCamaraWS/SessoesReunioes.asmx/ListarDiscursosPlenario?dataIni={dataIni}&dataFim={dataFim}&codigoSessao=&parteNomeParlamentar=&siglaPartido=&siglaUF='
    FILE_BASE_NAME = 'speeches.xz'

    CSV_PARAMS = {
        'compression': 'xz',
        'encoding': 'utf-8',
        'index': False
    }

    def fetch(self, range_start, range_end):
        range = {'dataIni': range_start, 'dataFim': range_end}
        url = self.URL.format(**range)
        file=urllib.request.urlopen(url)

        t = ET.ElementTree(file=file)
        records = []
        root = t.getroot()
        for i, session in enumerate(root):
            session_code = session.find('codigo').text.strip()
            session_date = datetime.strptime(session.find('data').text.strip(), "%d/%m/%Y")
            session_num  = session.find('numero').text.strip()
            for phase in session.find('fasesSessao').getchildren():
                phase_code = phase.find('codigo').text.strip()
                phase_desc = phase.find('descricao').text.strip()
                for speech in phase.find('discursos').getchildren():
                    speech_speaker_num   = speech.find('orador/numero').text.strip()
                    speech_speaker_name  = speech.find('orador/nome').text.strip()
                    speech_speaker_party = speech.find('orador/partido').text.strip()
                    speech_speaker_state = speech.find('orador/uf').text.strip()
                    speech_started_at    = datetime.strptime(speech.find('horaInicioDiscurso').text.strip(), "%d/%m/%Y %H:%M:%S")
                    speech_room_num      = speech.find('numeroQuarto').text.strip()
                    speech_insertion_num = speech.find('numeroInsercao').text.strip()
                    records.append([
                        session_code,
                        session_date,
                        session_num,
                        phase_code,
                        phase_desc,
                        speech_speaker_num,
                        speech_speaker_name,
                        speech_speaker_party,
                        speech_speaker_state,
                        speech_started_at,
                        speech_room_num,
                        speech_insertion_num
                    ])

        return pd.DataFrame(records, columns=[
            'session_code',
            'session_date',
            'session_num',
            'phase_code',
            'phase_desc',
            'speech_speaker_num',
            'speech_speaker_name',
            'speech_speaker_party',
            'speech_speaker_state',
            'speech_started_at',
            'speech_room_num',
            'speech_insertion_num'
        ])

    def write_file(self, path, df):
        print('Writing it to file…')
        filepath = os.path.join(path, self.FILE_BASE_NAME)
        df.to_csv(filepath, **self.CSV_PARAMS)

        print('Done.')

# TODO: Read date range and output path from user input
range_start = '01/11/2016'
range_end = '30/11/2016'
output = '.'

if __name__ == '__main__':
    speeches = Speeches()
    df = speeches.fetch(range_start, range_end)
    speeches.write_file(output, df)
