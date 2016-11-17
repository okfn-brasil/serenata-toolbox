import os
from urllib.request import urlretrieve
from zipfile import ZipFile

def fetch_ceap(destination_path):
    urls = ['http://www.camara.gov.br/cotas/AnoAtual.zip',
            'http://www.camara.gov.br/cotas/AnoAnterior.zip',
            'http://www.camara.gov.br/cotas/AnosAnteriores.zip']
    filenames = map(lambda url: url.split('/')[-1], urls)

    for url, filename in zip(urls, filenames):
        zip_file_path = os.path.join(destination_path, filename)
        urlretrieve(url, zip_file_path)
        zip_file = ZipFile(zip_file_path, 'r')
        zip_file.extractall(destination_path)
        zip_file.close()
        os.remove(zip_file_path)

def fetch_latest_backup(destination_path,
                        aws_bucket='serenata-de-amor-data',
                        aws_region='s3-sa-east-1'):
    files = ['2016-08-08-current-year.xz',
             '2016-08-08-last-year.xz',
             '2016-08-08-previous-years.xz',
             '2016-08-08-ceap-datasets.md',
             '2016-08-08-datasets-format.html',
             '2016-09-03-companies.xz',
             '2016-11-11-congressperson-relatives.xz']
    for filename in files:
        url = 'https://{}.amazonaws.com/{}/{}'.format(aws_region,
                                                      aws_bucket,
                                                      filename)
        filepath = os.path.join(destination_path, filename)
        if not os.path.exists(filepath):
            urlretrieve(url, filepath)
