import asyncio
import os

import aiofiles
import aiohttp
from tqdm import tqdm

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
        '2016-12-21-inident-and-suspended-companies.xz',
        '2016-12-21-national-register-punished-companies.xz',
        '2016-12-22-agreements.xz',
        '2016-12-22-amendments.xz',
        '2017-02-15-receipts-texts.xz',
        '2017-03-20-purchase-suppliers.xz',
        '2017-05-21-companies-no-geolocation.xz',
        '2017-05-22-brazilian-cities.csv',
        '2017-05-23-congressperson-details.xz',
        '2017-05-29-deputies.xz',
        '2017-05-29-presences.xz',
        '2017-05-29-sessions.xz',
        '2017-05-29-speeches.xz',
        '2017-06-17-official-missions.xz',
        '2017-07-04-reimbursements.xz',
        '2017-07-20-tse-candidates.xz',
        '2017-11-30-donations-candidates.xz',
        '2017-11-30-donations-committees.xz',
        '2017-11-30-donations-parties.xz',
        '2018-02-05-congresspeople-social-accounts.xz',
    )

    def __init__(self, target, **kwargs):
        self.bucket = kwargs.get('bucket')
        self.region = kwargs.get('region_name')
        if not all((self.bucket, self.region)):
            raise RuntimeError('No bucket and/or region_name kwargs provided')

        self.target = os.path.abspath(target)
        if not all((os.path.exists(self.target), os.path.isdir(self.target))):
            msg = '{} does not exist or is not a directory.'
            raise FileNotFoundError(msg.format(self.target))

        self.timeout = kwargs.get('timeout')
        self.semaphore = asyncio.Semaphore(MAX_REQUESTS)
        self.progress = 0
        self.total = 0

    def download(self, files):
        if isinstance(files, str):
            files = [files]

        files = tuple(filter(bool, files))
        if not files:
            return

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main(loop, files))

    async def main(self, loop, files):
        desc = 'Downloading {} files'.format(len(files))
        if len(files) == 1:
            first_file, *_ = files
            desc = 'Downloading {}'.format(first_file)

        async with aiohttp.ClientSession(loop=loop) as client:

            # fetch total size (all files)
            sizes = [self.fetch_size(client, f) for f in files]
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
        with (await self.semaphore):
            async with client.head(self.url(filename)) as resp:
                size = resp.headers.get('CONTENT-LENGTH', '0')

        self.total += int(size)

    async def fetch_file(self, client, filename):
        filepath = os.path.join(self.target, filename)
        with (await self.semaphore):
            async with client.get(self.url(filename), timeout=self.timeout) as resp:
                contents = await resp.read()

            async with aiofiles.open(filepath, 'wb') as fh:
                await fh.write(contents)

            self.progress.update(len(contents))

    def url(self, filename):
        url = 'https://s3-{}.amazonaws.com/{}/{}'
        return url.format(self.region, self.bucket, filename)
