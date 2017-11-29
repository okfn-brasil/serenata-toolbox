import urllib

from datetime import timedelta

import pandas as pd

from bs4 import BeautifulSoup

from serenata_toolbox import log
from serenata_toolbox.datasets.helpers import (
    save_to_csv,
    translate_column,
)


class OfficialMissionsDataset:

    URL = (
        'http://www.camara.leg.br/missao-oficial/missao-pesquisa?'
        'deputado=1&'
        'nome-deputado=&'
        'nome-servidor=&'
        'dati={0}&'
        'datf={1}&'
        'nome-evento='
    )

    def fetch(self, start_date, end_date):
        """
        Fetches official missions within the given date range
        """

        records = []
        for two_months_range in self._generate_ranges(start_date, end_date):
            log.debug(two_months_range)
            for record in self._fetch_missions_for_range(two_months_range[0], two_months_range[1]):
                records.append(record)

        df = pd.DataFrame(records, columns=[
            'participant',
            'destination',
            'subject',
            'start',
            'end',
            'canceled',
            'report_status',
            'report_details_link'
        ])

        translate_column(df, 'report_status', {
            'Disponível': 'Available',
            'Pendente': 'Pending',
            'Em análise': 'Analysing',
            'Não se aplica': 'Does not apply'
        })
        translate_column(df, 'canceled', {
            'Não': 'No',
            'Sim': 'Yes'
        })

        return df.drop_duplicates()

    @staticmethod
    def _generate_ranges(start_date, end_date):
        """
        Generate a list of 2 month ranges for the range requested with an
        intersection between months. This is necessary because we can't search
        for ranges longer than 3 months and the period searched has to encompass
        the whole period of the mission.
        """
        range_start = start_date
        while range_start < end_date:
            range_end = range_start + timedelta(days=60)
            yield (
                range_start.strftime("%d/%m/%Y"),
                range_end.strftime("%d/%m/%Y")
            )
            range_start += timedelta(days=30)

    def _fetch_missions_for_range(self, range_start, range_end):
        url = self.URL.format(range_start, range_end)
        data = urllib.request.urlopen(url)
        soup = BeautifulSoup(data, 'html.parser')

        occurences = soup.findAll('tbody', attrs={'class': 'coresAlternadas'})
        if not occurences:
            return

        table = occurences[0]
        for row in table.find_all('tr', recursive=False):
            cells = row.findAll('td', recursive=False)
            start = cells[0].text.strip()
            end = cells[1].text.strip()
            subject = cells[2].text.strip()
            destination = cells[3].text.strip()
            participant = cells[4].find('span').text.strip()
            report_status = cells[4].find('a')
            report_details_link = None
            if report_status is None:
                report_status = cells[4].find_all('td')[1].text.strip()
            else:
                report_path = report_status['href'].strip().replace("\r\n", '').replace("\t", '')
                report_details_link = "http://www.camara.leg.br" + report_path
                report_status = report_status.text.strip()
            canceled = cells[5].text.strip()

            yield (
                participant,
                destination,
                subject,
                start,
                end,
                canceled,
                report_status,
                report_details_link
            )


def fetch_official_missions(data_dir, start_date, end_date):
    """
    :param data_dir: (str) directory in which the output file will be saved
    :param start_date: (datetime) first date of the range to be scraped
    :param end_date: (datetime) last date of the range to be scraped
    """
    official_missions = OfficialMissionsDataset()
    df = official_missions.fetch(start_date, end_date)
    save_to_csv(df, data_dir, "official-missions")

    return df
