import os
from urllib.request import urlretrieve


def fetch(filename, destination_path,
          aws_bucket='serenata-de-amor-data',
          aws_region='s3-sa-east-1'):
    url = 'https://{}.amazonaws.com/{}/{}'.format(aws_region,
                                                  aws_bucket,
                                                  filename)
    filepath = os.path.join(destination_path, filename)
    if not os.path.exists(filepath):
        urlretrieve(url, filepath)


def fetch_latest_backup(destination_path,
                        aws_bucket='serenata-de-amor-data',
                        aws_region='s3-sa-east-1'):
    files = (
        '2016-08-08-ceap-datasets.md',
        '2016-08-08-current-year.xz',
        '2016-08-08-datasets-format.html',
        '2016-08-08-last-year.xz',
        '2016-08-08-previous-years.xz',
        '2016-09-03-companies.xz',
        '2016-11-11-congressperson-relatives.xz',
        '2016-11-19-current-year.xz',
        '2016-11-19-last-year.xz',
        '2016-11-19-previous-years.xz',
        '2016-11-19-reimbursements.xz',
        '2016-11-28-congressperson-civil-names.xz',
        '2016-11-29-yelp-companies.xz',
        '2016-12-02-foursquare-companies.xz',
        '2016-12-15-speeches.xz',
        '2016-12-20-impeded-non-profit-entities.xz',
        '2016-12-21-deputies.xz',
        '2016-12-21-inident-and-suspended-companies.xz',
        '2016-12-21-national-register-punished-companies.xz',
        '2016-12-21-presences.xz',
        '2016-12-21-sessions.xz',
        '2016-12-21-speeches.xz',
        '2016-12-22-agreements.xz',
        '2016-12-22-amendments.xz'
    )
    for filename in files:
        fetch(filename, destination_path, aws_bucket, aws_region)
