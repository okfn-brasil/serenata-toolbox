import os.path
from datetime import date
from urllib.request import urlretrieve

import pandas as pd


class FederalSenateDataset:
    URL = 'http://www.senado.gov.br/transparencia/LAI/verba/{}.csv'

    LAST_YEAR = date.today().year + 1

    def __init__(self, path, first_year=2008, last_year=LAST_YEAR):
        self.path = path
        self.first_year = first_year
        self.last_year = last_year
        self.year_range = range(first_year, last_year)

    def fetch(self):
        retrieved_files = []
        not_found_files = []

        for year in self.year_range:
            url = self.URL.format(year)
            file_path = os.path.join(self.path, 'federal-senate-{}.csv'.format(year))
            try:
                urlretrieve(url, file_path)
            except Exception as exception:
                print('While fetching Seranata Toolbox not found file: {} \n{}'.format(file_path, exception))
                not_found_files.append(file_path)
            else:
                retrieved_files.append(file_path)

        return (retrieved_files, not_found_files)

    def translate(self):
        filenames = self._filename_generator('csv')
        not_found_files = []
        translated_files = []

        for filename in filenames:
            csv_path = os.path.join(self.path, filename)
            try:
                self._translate_file(csv_path)
            except Exception as exception:
                print('While translating Seranata Toolbox not found file: {} \n{}'.format(csv_path, exception))
                not_found_files.append(csv_path)
            else:
                translated_files.append(csv_path)

        return (translated_files, not_found_files)

    def clean(self):
        filenames = self._filename_generator('xz')

        merged_dataset = self._merge_files(filenames)

        cleaned_merged_dataset = self._cleanup_dataset(merged_dataset)

        reimbursement_path = os.path.join(self.path, 'federal-senate-reimbursements.xz')
        cleaned_merged_dataset.to_csv(reimbursement_path,
                                      compression='xz',
                                      index=False,
                                      encoding='utf-8')

        return reimbursement_path

    def _filename_generator(self, extension):
        return ['federal-senate-{}.{}'.format(year, extension) for year in self.year_range]

    def _cleanup_dataset(self, dataset):
        dataset['date'] = pd.to_datetime(dataset['date'], errors='coerce')
        dataset['cnpj_cpf'] = dataset['cnpj_cpf'].str.replace(r'\D', '')

        return dataset

    def _merge_files(self, filenames):
        dataset = pd.DataFrame()

        for filename in filenames:
            file_path = os.path.join(self.path, filename)
            data = pd.read_csv(file_path, encoding='utf-8')
            dataset = pd.concat([dataset, data])

        return dataset

    def _translate_file(self, csv_path):
        output_file_path = csv_path.replace('.csv', '.xz')

        data = pd.read_csv(csv_path,
                           sep=';',
                           encoding="ISO-8859-1",
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
