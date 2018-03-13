from decouple import config


AMAZON_ACCESS_KEY = config('AMAZON_ACCESS_KEY', default=None)
AMAZON_SECRET_KEY = config('AMAZON_SECRET_KEY', default=None)
AMAZON_REGION = config('AMAZON_REGION', default='sa-east-1')
AMAZON_BUCKET = config('AMAZON_BUCKET', default='serenata-de-amor-data')
