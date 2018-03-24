from decouple import config


AMAZON_REGION = config('AMAZON_REGION', default='nyc3')
AMAZON_BUCKET = config('AMAZON_BUCKET', default='serenata-de-amor-data')
AMAZON_ENDPOINT = config('AMAZON_ENDPOINT', default='https://nyc3.digitaloceanspaces.com')
