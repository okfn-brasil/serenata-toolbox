# Serenata de Amor Toolbox

[PyPI](https://pypi.python.org/) package to support [Serenata de Amor](https://github.com/datasciencebr/serenata-de-amor) and [Rosie](https://github.com/datasciencebr/rosie) development.

## Install

As this is a _work in progress_ clone the repo and use `$ python setup.py develop` within your virtualenv.

## Usage

### Output

```console
$ python3
>>> from serenata_toolbox import xml2csv
>>> xml2csv.output('Spam and eggs')
2016-12-01 18:14:26 Spam and eggs
```

## Test suite

```console
$ python -m unittest discover tests
```
