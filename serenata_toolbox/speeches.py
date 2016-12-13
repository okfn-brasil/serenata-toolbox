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
        root = t.getroot()
        records = self.parse_speeches(root)

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

    def parse_speeches(self, root):
        for session in root:
            session_code = self.__extract_text(session, 'codigo')
            session_date = self.__extract_date(session, 'data')
            session_num  = self.__extract_text(session, 'numero')
            for phase in session.find('fasesSessao'):
                phase_code = self.__extract_text(phase, 'codigo')
                phase_desc = self.__extract_text(phase, 'descricao')
                for speech in phase.find('discursos'):
                    speech_speaker_num   = self.__extract_text(speech, 'orador/numero')
                    speech_speaker_name  = self.__extract_text(speech, 'orador/nome')
                    speech_speaker_party = self.__extract_text(speech, 'orador/partido')
                    speech_speaker_state = self.__extract_text(speech, 'orador/uf')
                    speech_started_at    = self.__extract_datetime(speech, 'horaInicioDiscurso')
                    speech_room_num      = self.__extract_text(speech, 'numeroQuarto')
                    speech_insertion_num = self.__extract_text(speech, 'numeroInsercao')

                    yield [
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
                    ]

    @staticmethod
    def __extract_date(node, xpath):
        return datetime.strptime(Speeches.__extract_text(node, xpath), "%d/%m/%Y")

    @staticmethod
    def __extract_datetime(node, xpath):
        return datetime.strptime(Speeches.__extract_text(node, xpath), "%d/%m/%Y %H:%M:%S")

    @staticmethod
    def __extract_text(node, xpath):
        return node.find(xpath).text.strip()

# TODO: Read date range and output path from user input
range_start = '01/11/2016'
range_end = '30/11/2016'
output = '.'

if __name__ == '__main__':
    speeches = Speeches()
    df = speeches.fetch(range_start, range_end)
    speeches.write_file(output, df)
