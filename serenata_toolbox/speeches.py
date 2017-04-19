import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import urllib

from datetime import datetime

from serenata_toolbox import datasets
from serenata_toolbox.cleanup import (
    xml_extract_text,
    xml_extract_datetime,
    xml_extract_date
)

class Speeches:

    URL = (
        'http://www.camara.leg.br/SitCamaraWS/SessoesReunioes.asmx/ListarDiscursosPlenario'
        '?dataIni={dataIni}'
        '&dataFim={dataFim}'
        '&codigoSessao=&parteNomeParlamentar=&siglaPartido=&siglaUF='
    )

    CSV_PARAMS = {
        'compression': 'xz',
        'encoding': 'utf-8',
        'index': False
    }

    def fetch(self, range_start, range_end):
        """
        Fetches speeches from the ListarDiscursosPlenario endpoint of the
        SessoesReunioes (SessionsReunions) API.

        The date range provided should be specified as a string using the
        format supported by the API (%d/%m/%Y)
        """
        range = {'dataIni': range_start, 'dataFim': range_end}
        url = self.URL.format(**range)
        xml = urllib.request.urlopen(url)

        tree = ET.ElementTree(file=xml)
        records = self.__parse_speeches(tree.getroot())

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

    def __parse_speeches(self, root):
        for session in root:
            session_code = xml_extract_text(session, 'codigo')
            session_date = xml_extract_date(session, 'data')
            session_num  = xml_extract_text(session, 'numero')
            for phase in session.find('fasesSessao'):
                phase_code = xml_extract_text(phase, 'codigo')
                phase_desc = xml_extract_text(phase, 'descricao')
                for speech in phase.find('discursos'):
                    speech_speaker_num   = xml_extract_text(speech, 'orador/numero')
                    speech_speaker_name  = xml_extract_text(speech, 'orador/nome')
                    speech_speaker_party = xml_extract_text(speech, 'orador/partido')
                    speech_speaker_state = xml_extract_text(speech, 'orador/uf')
                    speech_started_at    = xml_extract_datetime(speech, 'horaInicioDiscurso')
                    speech_room_num      = xml_extract_text(speech, 'numeroQuarto')
                    speech_insertion_num = xml_extract_text(speech, 'numeroInsercao')

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

def fetch_speeches(data_dir, range_start, range_end):
    """
    :param data_dir: (str) directory in which the output file will be saved
    :param range_start: (str) date in the format dd/mm/yyyy
    :param range_end: (str) date in the format dd/mm/yyyy
    """
    speeches = Speeches()
    df = speeches.fetch(range_start, range_end)
    datasets.save(df, data_dir, "speeches")
