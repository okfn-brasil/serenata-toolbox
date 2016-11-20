import os.path
import subprocess
import sys
from urllib.request import urlretrieve
from zipfile import ZipFile
import numpy as np
import pandas as pd
from .reimbursements import Reimbursements

class CEAPDataset:
    def __init__(self, path):
        self.path = path


    def fetch(self):
        urls = ['http://www.camara.gov.br/cotas/AnoAtual.zip',
                'http://www.camara.gov.br/cotas/AnoAnterior.zip',
                'http://www.camara.gov.br/cotas/AnosAnteriores.zip']
        filenames = map(lambda url: url.split('/')[-1], urls)

        for url, filename in zip(urls, filenames):
            zip_file_path = os.path.join(self.path, filename)
            urlretrieve(url, zip_file_path)
            zip_file = ZipFile(zip_file_path, 'r')
            zip_file.extractall(self.path)
            zip_file.close()
            os.remove(zip_file_path)

        urlretrieve('http://www2.camara.leg.br/transparencia/cota-para-exercicio-da-atividade-parlamentar/explicacoes-sobre-o-formato-dos-arquivos-xml',
                    os.path.join(self.path, 'datasets-format.html'))


    def convert_to_csv(self):
        for filename in ['AnoAtual', 'AnoAnterior', 'AnosAnteriores']:
            xml_path = os.path.join(self.path, '{}.xml'.format(filename))
            self.__convert_file_to_csv(xml_path)


    def translate(self):
        for filename in ['AnoAtual', 'AnoAnterior', 'AnosAnteriores']:
            csv_path = os.path.join(self.path, '{}.csv'.format(filename))
            self.__translate_file(csv_path)


    def clean(self):
        reimbursements = Reimbursements(self.path)
        dataset = reimbursements.group(reimbursements.receipts)
        reimbursements.write_reimbursement_file(dataset)


    def __convert_file_to_csv(self, xml_path):
        script_path = os.path.join(os.path.dirname(__file__), 'xml2csv.py')
        csv_path = xml_path.replace('.xml', '.csv')
        subprocess.call(['python', script_path, xml_path, csv_path])


    def __translate_file(self, csv_path):
        output_file_path = csv_path \
            .replace('AnoAtual', 'current-year') \
            .replace('AnoAnterior', 'last-year') \
            .replace('AnosAnteriores', 'previous-years') \
            .replace('.csv', '.xz')

        data = pd.read_csv(csv_path,
                           dtype={'ideDocumento': np.str,
                                  'ideCadastro': np.str,
                                  'nuCarteiraParlamentar': np.str,
                                  'codLegislatura': np.str,
                                  'txtCNPJCPF': np.str,
                                  'numRessarcimento': np.str})
        data.rename(columns={
            'ideDocumento': 'document_id',
            'txNomeParlamentar': 'congressperson_name',
            'ideCadastro': 'congressperson_id',
            'nuCarteiraParlamentar': 'congressperson_document',
            'nuLegislatura': 'term',
            'sgUF': 'state',
            'sgPartido': 'party',
            'codLegislatura': 'term_id',
            'numSubCota': 'subquota_number',
            'txtDescricao': 'subquota_description',
            'numEspecificacaoSubCota': 'subquota_group_id',
            'txtDescricaoEspecificacao': 'subquota_group_description',
            'txtFornecedor': 'supplier',
            'txtCNPJCPF': 'cnpj_cpf',
            'txtNumero': 'document_number',
            'indTipoDocumento': 'document_type',
            'datEmissao': 'issue_date',
            'vlrDocumento': 'document_value',
            'vlrGlosa': 'remark_value',
            'vlrLiquido': 'net_value',
            'numMes': 'month',
            'numAno': 'year',
            'numParcela': 'installment',
            'txtPassageiro': 'passenger',
            'txtTrecho': 'leg_of_the_trip',
            'numLote': 'batch_number',
            'numRessarcimento': 'reimbursement_number',
            'vlrRestituicao': 'reimbursement_value',
            'nuDeputadoId': 'applicant_id',
        }, inplace=True)

        data['subquota_description'] = \
            data['subquota_description'].astype('category')

        keys = data['subquota_description'].cat.categories
        categories = {
            'ASSINATURA DE PUBLICAÇÕES':
                'Publication subscriptions',
            'COMBUSTÍVEIS E LUBRIFICANTES.':
                'Fuels and lubricants',
            'CONSULTORIAS, PESQUISAS E TRABALHOS TÉCNICOS.':
                'Consultancy, research and technical work',
            'DIVULGAÇÃO DA ATIVIDADE PARLAMENTAR.':
                'Publicity of parliamentary activity',
            'Emissão Bilhete Aéreo':
                'Flight ticket issue',
            'FORNECIMENTO DE ALIMENTAÇÃO DO PARLAMENTAR':
                'Congressperson meal',
            'HOSPEDAGEM ,EXCETO DO PARLAMENTAR NO DISTRITO FEDERAL.':
                'Lodging, except for congressperson from Distrito Federal',
            'LOCAÇÃO OU FRETAMENTO DE AERONAVES':
                'Aircraft renting or charter of aircraft',
            'LOCAÇÃO OU FRETAMENTO DE EMBARCAÇÕES':
                'Watercraft renting or charter',
            'LOCAÇÃO OU FRETAMENTO DE VEÍCULOS AUTOMOTORES':
                'Automotive vehicle renting or charter',
            'MANUTENÇÃO DE ESCRITÓRIO DE APOIO À ATIVIDADE PARLAMENTAR':
                'Maintenance of office supporting parliamentary activity',
            'PARTICIPAÇÃO EM CURSO, PALESTRA OU EVENTO SIMILAR':
                'Participation in course, talk or similar event',
            'PASSAGENS AÉREAS':
                'Flight tickets',
            'PASSAGENS TERRESTRES, MARÍTIMAS OU FLUVIAIS':
                'Terrestrial, maritime and fluvial tickets',
            'SERVIÇO DE SEGURANÇA PRESTADO POR EMPRESA ESPECIALIZADA.':
                'Security service provided by specialized company',
            'SERVIÇO DE TÁXI, PEDÁGIO E ESTACIONAMENTO':
                'Taxi, toll and parking',
            'SERVIÇOS POSTAIS':
                'Postal services',
            'TELEFONIA':
                'Telecommunication',
            'AQUISIÇÃO DE MATERIAL DE ESCRITÓRIO.':
                'Purchase of office supplies',
            'AQUISIÇÃO OU LOC. DE SOFTWARE; SERV. POSTAIS; ASS.':
                'Software purchase or renting; Postal services; Subscriptions',
            'LOCAÇÃO DE VEÍCULOS AUTOMOTORES OU FRETAMENTO DE EMBARCAÇÕES ':
                'Automotive vehicle renting or watercraft charter',
            'LOCOMOÇÃO, ALIMENTAÇÃO E  HOSPEDAGEM':
                'Locomotion, meal and lodging',
        }
        categories = [categories[cat]
                      for cat in data['subquota_description'].cat.categories]
        data['subquota_description'].cat.rename_categories(categories,
                                                           inplace=True)
        data.to_csv(output_file_path, compression='xz', index=False)

        return output_file_path
