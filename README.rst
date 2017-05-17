.. image:: https://travis-ci.org/datasciencebr/serenata-toolbox.svg?branch=master
   :target: https://travis-ci.org/datasciencebr/serenata-toolbox
   :alt: Travis CI build status (Linux)

.. image:: https://readthedocs.org/projects/serenata-toolbox/badge/?version=latest
   :target: http://serenata-toolbox.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://landscape.io/github/datasciencebr/serenata-toolbox/master/landscape.svg?style=flat
   :target: https://landscape.io/github/datasciencebr/serenata-toolbox/master
   :alt: Code Health

Serenata de Amor Toolbox
========================

`pip <https://pip.pypa.io/en/stable/>`_  installable package to support `Serenata de Amor <https://github.com/datasciencebr/serenata-de-amor>`_
and `Rosie <https://github.com/datasciencebr/rosie>`_ development.

Serenata_toolbox is compatible with Python 3+

Installation
------------

::

    $ pip install git+https://github.com/datasciencebr/serenata-toolbox.git#egg=serenata-toolbox 

Development
------------

Clone the repo and use it within your virtualenv.

::

  $ git clone https://github.com/datasciencebr/serenata-toolbox.git
  $ python setup.py develop

We use `Elm's philosophy <https://github.com/elm-lang/elm-package#version-rules>`_ for version bumping:

* MICRO: the API is the same, no risk of breaking code
* MINOR: values have been added, existing values are unchanged
* MAJOR: existing values have been changed or removed

Usage
-----

Copy `config.ini.example` as `config.ini` and edit it with your own credentials. If you don't plan to upload anything to S3 please don't bother about keys and secrets in this file.

Example 1: How do I download the datasets?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We have `plenty of them <https://github.com/datasciencebr/serenata-de-amor/blob/master/CONTRIBUTING.md#datasets-data>`_ ready for you to download from our servers. And this toolbox helps you get them. Let's say you want your datasets at `/tmp/serenata-data/`:

.. code:: python

  from serenata_toolbox.datasets import Datasets
  datasets = Datasets('/tmp/serenata-data/')

  # now lets see what datasets are available
  for dataset in datasets.remote.all:
      print(dataset)  # and you'll see a long list of datasets!

  # now let's download one of them
  datasets.downloader.download('2016-12-06-reibursements.xz')  # yay, you've just downloaded this dataset to /tmp/serenata-data/

  # You can also get themostrecent version of all datasets:
  latest = list(dataset.downloader.LATEST)
  datasets.downloader.download(latest)

Example 2: Using shortcuts
^^^^^^^^^^^^^^^^^^^^^^^^^^

If the last example doesn't look that simple, there are some fancy shortcuts available:

.. code:: python

  from serenata_toolbox.datasets import fetch, fetch_latest_backup
  fetch('2016-12-06-reibursements.xz', '/tmp/serenata-data')
  fetch_latest_backup( '/tmp/serenata-data')  # yep, we've just did exactly the same thing

Example 3: Generating datasets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you ever wonder how did we generated these datasets, this toolbox can help you too (at least with the more used ones — the other are generates `in our main repo <https://github.com/datasciencebr/serenata-de-amor/blob/master/CONTRIBUTING.md#the-toolbox-and-our-the-source-files-src>`_):

.. code:: python

    from serenata_toolbox.federal_senate.federal_senate_dataset import FederalSenateDataset
    from serenata_toolbox.chamber_of_deputies.chamber_of_deputies_dataset import ChamberOfDeputiesDataset

    senate = FederalSenateDataset('/tmp/serenata-data/')
    senate.fetch()
    senate.translate()
    senate.clean()

    chamber = ChamberOfDeputiesDataset('/tmp/serenata-data/')
    chamber.fetch()
    chamber.translate()
    chamber.clean()

Documentation (WIP)
-------------------

The `full documentation <https://serenata_toolbox.readthedocs.io>`_ is still a work in progress. If you wanna give us a hand you will need `Sphinx <http://www.sphinx-doc.org/>`_:

::

  $ cd docs
  $ make clean;make rst;rm source/modules.rst;make html
  
Run Unit Test suite
-------------------

::

  $ python -m unittest discover tests

Source Code
-----------

Feel free to fork, evaluate and contribute to this project.

Source: https://github.com/datasciencebr/serenata-toolbox/
