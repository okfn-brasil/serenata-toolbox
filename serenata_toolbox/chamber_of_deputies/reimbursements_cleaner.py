import csv
import os.path

import numpy as np
import pandas as pd


COLUMNS = {
    'txNomeParlamentar': 'congressperson_name',
    'idecadastro': 'congressperson_id',
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
    'ideDocumento': 'document_id',
}
SUBQUOTAS = (
    ('1', 'Maintenance of office supporting parliamentary activity'),
    ('2', 'Locomotion, meal and lodging'),
    ('3', 'Fuels and lubricants'),
    ('4', 'Consultancy, research and technical work'),
    ('5', 'Publicity of parliamentary activity'),
    ('6', 'Purchase of office supplies'),
    ('7', 'Software purchase or renting; Postal services; Subscriptions'),
    ('8', 'Security service provided by specialized company'),
    ('9', 'Flight tickets'),
    ('10', 'Telecommunication'),
    ('11', 'Postal services'),
    ('12', 'Publication subscriptions'),
    ('13', 'Congressperson meal'),
    ('14', 'Lodging, except for congressperson from Distrito Federal'),
    ('15', 'Automotive vehicle renting or watercraft charter'),
    ('119', 'Aircraft renting or charter of aircraft'),
    ('120', 'Automotive vehicle renting or charter'),
    ('121', 'Watercraft renting or charter'),
    ('122', 'Taxi, toll and parking'),
    ('123', 'Terrestrial, maritime and fluvial tickets'),
    ('137', 'Participation in course, talk or similar event'),
    ('999', 'Flight ticket issue')
)
DTYPE = {
    'txNomeParlamentar': np.str,
    'idecadastro': np.str,
    'nuCarteiraParlamentar': np.str,
    'nuLegislatura': np.str,
    'sgUF': np.str,
    'sgPartido': np.str,
    'codLegislatura': np.str,
    'numSubCota': np.str,
    'txtDescricao': np.str,
    'numEspecificacaoSubCota': np.str,
    'txtDescricaoEspecificacao': np.str,
    'txtFornecedor': np.str,
    'txtCNPJCPF': np.str,
    'txtNumero': np.str,
    'indTipoDocumento': np.str,
    'datEmissao': np.str,
    'vlrDocumento': np.float,
    'vlrGlosa': np.str,
    'vlrLiquido': np.float,
    'numMes': np.str,
    'numAno': np.str,
    'numParcela': np.str,
    'txtPassageiro': np.str,
    'txtTrecho': np.str,
    'numLote': np.str,
    'numRessarcimento': np.str,
    'nuDeputadoId': np.str,
    'ideDocumento': np.str,
}


def parse_float(value):
    return float(value.replace(',', '.'))


CONVERTERS = {
    'vlrRestituicao': parse_float,
}
KEY = 'document_id'
AGGREGATED_COLS = {
    'reimbursement_number': 'numbers',
    'net_value': 'total_net_value',
    'reimbursement_value': 'total_value',
}


class ReimbursementsCleaner:
    """
    Perform data cleaning tasks over a reimbursements CSV file.
    """

    def __init__(self, year, path):
        self.year = year
        self.path = path
        self.data = None

    def __call__(self):
        self.load_source_file()
        self.translate()
        self.aggregate_multiple_payments()
        self.save()

    def load_source_file(self):
        file_path = os.path.join(self.path, f'Ano-{self.year}.csv')
        self.data = pd.read_csv(file_path,
                                delimiter=';',
                                quoting=csv.QUOTE_NONE,
                                decimal=',',
                                dtype=DTYPE,
                                low_memory=False)

    def translate(self):
        self.data.rename(columns=COLUMNS, inplace=True)
        for code, name in SUBQUOTAS:
            rows = self.data['subquota_number'] == code
            self.data.loc[rows, 'subquota_description'] = name

    def aggregate_multiple_payments(self):
        self.data = pd.concat([
            self._house_payments(),
            self._non_house_payments(),
        ])

    def save(self):
        file_path = os.path.join(self.path, f'reimbursements-{self.year}.csv')
        self.data.to_csv(file_path, index=False)

    def _house_payments(self):
        data = self.data[self.data['reimbursement_number'] == '0'].copy()
        data.rename(columns=AGGREGATED_COLS, inplace=True)
        data['numbers'] = data['numbers'].apply(lambda val: [val])
        return data

    def _non_house_payments(self):
        def aggregate_attributes(df):
            reimbursement_numbers = df['reimbursement_number'].tolist()
            total_net_value = df['net_value'].sum()
            total_reimbursement_value = df['reimbursement_value'].sum()
            attributes = pd.Series({
                'numbers': reimbursement_numbers,
                'total_net_value': total_net_value,
                'total_value': total_reimbursement_value,
            })
            attributes = pd.concat([df.iloc[0], attributes])
            attributes.drop(AGGREGATED_COLS.keys(), inplace=True)
            return attributes

        data = self.data[self.data['reimbursement_number'] != '0']
        return data.groupby(KEY).apply(aggregate_attributes)
