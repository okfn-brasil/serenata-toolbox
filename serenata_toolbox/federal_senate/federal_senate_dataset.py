import os.path
from urllib.request import urlretrieve
import numpy as np
import pandas as pd

from datetime import date

class FederalSenateDataset:
    URL = 'http://www.senado.gov.br/transparencia/LAI/verba/{}.csv'
    FIRST_YEAR = 2008
    NEXT_YEAR = date.today().year + 1

    YEAR_RANGE = range(FIRST_YEAR, NEXT_YEAR)

    def __init__(self, path):
        self.path = path

    def fetch(self):
        for year in self.YEAR_RANGE:
            url = self.URL.format(year)
            file_path = os.path.join(self.path, 'federal-senate-{}.csv'.format(year))
            urlretrieve(url, file_path)

    def translate(self):
        filenames = ['federal-senate-{}.csv'.format(year) for year in self.YEAR_RANGE]
        for filename in filenames:
            csv_path = os.path.join(self.path, filename)
            self.__translate_file(csv_path)

    def clean(self):
        reimbursement_path = os.path.join(self.path, 'federal-senate-reimbursements.xz')

        filenames = ['federal-senate-{}.xz'.format(year) for year in self.YEAR_RANGE]
        dataset = pd.DataFrame()

        for filename in filenames:
            file_path = os.path.join(self.path, filename)
            data = pd.read_csv(file_path, encoding = "utf-8")
            dataset = pd.concat([dataset, data])

        dataset['date'] = pd.to_datetime(dataset['date'], errors='coerce')
        dataset['cnpj_cpf'] = dataset['cnpj_cpf'].str.replace(r'\D', '')

        dataset.to_csv(reimbursement_path, compression='xz', index=False, encoding='utf-8')

        return reimbursement_path

    def __translate_file(self, csv_path):
        output_file_path = csv_path.replace('.csv', '.xz')

        data = pd.read_csv(csv_path,
                           sep=';',
                           encoding = "ISO-8859-1",
                           skiprows=1)

        data.columns = map(str.lower, data.columns)

        data.rename(columns={
            'ano': 'year',
            'mes': 'month',
            'senador': 'congressperson_name',
            'tipo_despesa': 'expense_type',
            'cnpj_cpf': 'cnpj_cpf',
            'fornecedor': 'supplier',
            'documento': 'document_id',
            'data': 'date',
            'detalhamento': 'expense_details',
            'valor_reembolsado': 'reimbursement_value',
        }, inplace=True)

        data['expense_type'] = data['expense_type'].astype('category')

        data['expense_type'] = \
            data['expense_type'].astype('category')

        categories = {
            'Aluguel de imóveis para escritório político, compreendendo despesas concernentes a eles.':
                'Rent of real estate for political office, comprising expenses concerning them',
            'Aquisição de material de consumo para uso no escritório político, inclusive aquisição ou locação de software, despesas postais, aquisição de publicações, locação de móveis e de equipamentos. ':
                'Acquisition of consumables for use in the political office, including acquisition or leasing of software, postal expenses, acquisition of publications, rental of furniture and equipment',
            'Contratação de consultorias, assessorias, pesquisas, trabalhos técnicos e outros serviços de apoio ao exercício do mandato parlamentar':
                'Recruitment of consultancies, advisory services, research, technical work and other services in support of the exercise of the parliamentary mandate',
            'Divulgação da atividade parlamentar':
                'Publicity of parliamentary activity',
            'Locomoção, hospedagem, alimentação, combustíveis e lubrificantes':
                'Locomotion, lodging, food, fuels and lubricants',
            'Passagens aéreas, aquáticas e terrestres nacionais':
                'National air, water and land transport',
            'Serviços de Segurança Privada':
                'Private Security Services'
        }

        categories = [categories[cat] for cat in data['expense_type'].cat.categories]

        data['expense_type'].cat.rename_categories(categories, inplace=True)

        data.to_csv(output_file_path, compression='xz', index=False, encoding='utf-8')

        return output_file_path

