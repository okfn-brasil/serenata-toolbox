import asyncio
import os
from concurrent.futures import TimeoutError
from unittest import TestCase
from unittest.mock import Mock, patch

from aiohttp import ClientSession
from serenata_toolbox.datasets.downloader import Downloader


class TestDownloader(TestCase):

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_init(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        downloader = Downloader('test', bucket='bucket', region_name='south', timeout=1)
        self.assertEqual('bucket', downloader.bucket)
        self.assertEqual('south', downloader.region)
        self.assertEqual(os.path.abspath('test'), downloader.target)
        self.assertEqual(0, downloader.total)
        self.assertEqual(1, downloader.timeout)

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_init_no_timeout(self, exists, isdir):
        downloader = Downloader('test', bucket='bucket', region_name='south')
        self.assertEqual(None, downloader.timeout)

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_init_no_bucket(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        with self.assertRaises(RuntimeError):
            Downloader('test', region_name='south')

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_init_no_region(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        with self.assertRaises(RuntimeError):
            Downloader('test', bucket='bucket')

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_init_no_region_no_bucket(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        with self.assertRaises(RuntimeError):
            Downloader('test')

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_init_no_existing_target(self, exists, isdir):
        exists.return_value = False
        isdir.return_value = True
        with self.assertRaises(FileNotFoundError):
            Downloader('test', bucket='bucket', region_name='south')

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_init_file_target(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = False
        with self.assertRaises(FileNotFoundError):
            Downloader('test', bucket='bucket', region_name='south')

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_download_no_file(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        downloader = Downloader('test', bucket='bucket', region_name='south')
        self.assertIsNone(downloader.download(''))
        self.assertIsNone(downloader.download([]))

    @patch.object(Downloader, 'main')
    @patch('serenata_toolbox.datasets.downloader.asyncio')
    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_download_single_file(self, exists, isdir, asyncio_, main):
        exists.return_value = True
        isdir.return_value = True
        downloader = Downloader('test', bucket='bucket', region_name='south')
        downloader.download('test.xz')
        asyncio_.get_event_loop.assert_called_with()
        loop = asyncio_.get_event_loop.return_value
        self.assertTrue(loop.run_until_complete.called)
        main.assert_called_once_with(loop, ('test.xz',))

    @patch.object(Downloader, 'main')
    @patch('serenata_toolbox.datasets.downloader.asyncio')
    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_download_multiple_files(self, exists, isdir, asyncio_, main):
        exists.return_value = True
        isdir.return_value = True
        downloader = Downloader('test', bucket='bucket', region_name='south')
        downloader.download(range(3))
        asyncio_.get_event_loop.assert_called_with()
        loop = asyncio_.get_event_loop.return_value
        self.assertTrue(loop.run_until_complete.called)
        main.assert_called_once_with(loop, (1, 2))

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_download_no_file(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        downloader = Downloader('test', bucket='bucket', region_name='south')
        self.assertIsNone(downloader.download(''))
        self.assertIsNone(downloader.download([]))

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    def test_url(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        downloader = Downloader('test', bucket='bucket', region_name='south')
        expected = 'https://s3-south.amazonaws.com/bucket/test.xz'
        self.assertEqual(expected, downloader.url('test.xz'))

    def async_test(f):
        def wrapper(*args, **kwargs):
            coro = asyncio.coroutine(f)
            future = coro(*args, **kwargs)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(future)
        return wrapper

    @patch('serenata_toolbox.datasets.downloader.os.path.isdir')
    @patch('serenata_toolbox.datasets.downloader.os.path.exists')
    @async_test
    def test_download_timeout(self, exists, isdir):
        exists.return_value = True
        isdir.return_value = True
        with self.assertRaises(TimeoutError):
            downloader = Downloader('test', bucket='serenata-de-amor-data', region_name='a-east-1', timeout=0.001)
            downloader.url = Mock(return_value="http://www.google.com:81/")
            loop = asyncio.get_event_loop()

            async with ClientSession(loop=loop) as client:
                yield from downloader.fetch_file(client, '2016-12-06-reibursements.xz')
