import os

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
