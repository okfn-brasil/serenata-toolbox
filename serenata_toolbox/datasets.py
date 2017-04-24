import asyncio
import os

import aiofiles
import aiohttp
from tqdm import tqdm

AWS_BUCKET = 'serenata-de-amor-data'
AWS_REGION = 's3-sa-east-1'
MAX_REQUESTS = 4


class Downloader:

    LATEST = (
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
        '2016-12-22-amendments.xz',
        '2017-02-15-receipts-texts.xz',
        '2017-03-15-reimbursements.xz',
        '2017-03-20-purchase-suppliers.xz'
    )

    def __init__(self, target, aws_bucket=None, aws_region=None):
        self.aws_bucket = aws_bucket or AWS_BUCKET
        self.aws_region = aws_region or AWS_REGION
        self.target = os.path.abspath(target)
        self.semaphore = asyncio.Semaphore(MAX_REQUESTS)
        self.total = 0

        if not all((os.path.exists(self.target), os.path.isdir(self.target))):
            msg = '{} does not exist or is not a directory.'
            raise FileNotFoundError(msg.format(self.target))

    def download(self, files):
        files = list(files)  # generator wouldn't work, we loop through them 2x
        if not files:
            return

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main(loop, files))

    async def main(self, loop, files):
        if len(files) == 1:
            desc = 'Downloading {}'.format(files[0])
        else:
            desc = 'Downloading {} files'.format(len(files))

        async with aiohttp.ClientSession(loop=loop) as client:

            # fetch total size (all files)
            sizes = [self.fetch_size(client, filename) for filename in files]
            await asyncio.gather(*sizes)

            # download
            args = dict(total=self.total, desc=desc, unit='b', unit_scale=True)
            with tqdm(**args) as progress:
                self.progress = progress
                downloads = [self.fetch_file(client, f) for f in files]
                await asyncio.gather(*downloads)

            # cleanup
            del self.progress
            self.total = 0

    async def fetch_size(self, client, filename):
        url = self.url(filename)

        with (await self.semaphore):
            async with client.head(url) as response:
                size = response.headers.get('CONTENT-LENGTH', '0')

        self.total += int(size)

    async def fetch_file(self, client, filename):
        filepath = os.path.join(self.target, filename)
        url = self.url(filename)

        with (await self.semaphore):
            async with client.get(url, timeout=None) as response:
                contents = await response.read()

                async with aiofiles.open(filepath, 'wb') as fh:
                    await fh.write(contents)

                self.progress.update(len(contents))

    def url(self, filename):
        url = 'https://{}.amazonaws.com/{}/{}'
        return url.format(self.aws_region, self.aws_bucket, filename)


def fetch(filename, destination_path, aws_bucket=None, aws_region=None):
    downloader = Downloader(destination_path, aws_bucket, aws_region)
    return downloader.download([filename])


def fetch_latest_backup(destination_path, aws_bucket=None, aws_region=None):
    downloader = Downloader(destination_path, aws_bucket, aws_region)
    return downloader.download(downloader.LATEST)
