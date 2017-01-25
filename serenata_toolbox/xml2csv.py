import json
import os
import sys
from csv import DictWriter
from datetime import datetime
from io import StringIO

from bs4 import BeautifulSoup
from lxml.etree import iterparse


def output(*args, **kwargs):
    """Helper to print messages with a date/time marker"""
    now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
    return print(now, *args, **kwargs)


def xml_parser(xml_path, tag='DESPESA'):
    """
    Generator that parses the XML yielding a StringIO object for each record
    found. The StringIO holds the data in JSON format.
    """
    for _, node in iterparse(xml_path, tag=tag):

        # get data
        fields = {c.tag.lower(): c.text for c in node.iter() if c.tag != tag}
        node.clear()

        # export in JSON format
        yield StringIO(json.dumps(fields))


def csv_header(html_path):
    """
    Generator that yields the CSV headers reading them from a HTML file (e.g.
    datasets-format.html).
    """
    yield 'idedocumento'  # this field is missing from the reference
    with open(html_path, 'rb') as file_handler:
        parsed = BeautifulSoup(file_handler.read(), 'lxml')
        for row in parsed.select('.tabela-2 tr'):
            try:
                yield row.select('td')[0].text.strip().lower()
            except IndexError:
                pass


def create_csv(csv_path, headers):
    """Creates the CSV file with the headers (must be a list)"""
    with open(csv_path, 'w') as csv_file:
        writer = DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()


def convert_xml_to_csv(xml_file_path, csv_file_path):
    """Converts the xml file to a file in CSV format"""
    if os.stat(xml_file_path).st_size < 2 ** 10:
        output(xml_file_path, " is empty, so let's skip it!")
        return

    data_dir = os.path.dirname(xml_file_path)
    html_file_path = os.path.join(data_dir, 'datasets-format.html')

    output('Creating the CSV file')
    headers = list(csv_header(html_file_path))
    create_csv(csv_file_path, headers)

    count = 1
    output('Reading the XML file')
    for json_io in xml_parser(xml_file_path):
        csv_io = StringIO()
        writer = DictWriter(csv_io, fieldnames=headers)
        writer.writerow(json.loads(json_io.getvalue()))

        output('Writing record #{:,} to the CSV'.format(count), end='\r')
        with open(csv_file_path, 'a') as csv_file:
            print(csv_io.getvalue(), file=csv_file)

        json_io.close()
        csv_io.close()
        count += 1

    print('')  # clean the last output (the one with end='\r')
    output('Done!')


if __name__ == "__main__":
    XML_FILE_PATH = sys.argv[1]
    CSV_FILE_PATH = sys.argv[2]
    convert_xml_to_csv(XML_FILE_PATH, CSV_FILE_PATH)
