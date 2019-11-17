.. image:: https://travis-ci.org/okfn-brasil/serenata-toolbox.svg?branch=master
   :target: https://travis-ci.org/okfn-brasil/serenata-toolbox
   :alt: Travis CI build status (Linux)

.. image:: https://coveralls.io/repos/github/okfn-brasil/serenata-toolbox/badge.svg?branch=master
   :target: https://coveralls.io/github/okfn-brasil/serenata-toolbox?branch=master
   :alt: Coveralls

.. image:: https://badge.fury.io/py/serenata-toolbox.svg
   :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/serenata_toolbox
   :alt: PyPI - Python Version

.. image:: https://img.shields.io/badge/donate-apoia.se-EB4A3B.svg
   :target: https://apoia.se/serenata
   :alt: Donation Page

Serenata de Amor Toolbox
========================

Python package to support `Serenata de Amor <https://github.com/okfn-brasil/serenata-de-amor>`_ development. ``serenata_toolbox`` is compatible with Python 3.6+.

Installation
------------

.. code-block:: bash

    $ pip install -U serenata-toolbox

Usage
-----

This toolbox helps you get datasets used in `Serenata de Amor services <https://github.com/okfn-brasil/serenata-de-amor>`_ and `notebooks <https://github.com/okfn-brasil/notebooks>`_.

Example 1: Using the CLI
^^^^^^^^^^^^^^^^^^^^^^^^

Without any arguments, it will download our pre-processed datasets and store into ``data`` folder:

.. code-block:: bash

    $ serenata-toolbox

But you can specify which datasets to download and where to save them. For example, to download ``chamber_of_deputies`` and ``federal_senate`` datasets to ``/tmp/serenata-data``:

.. code-block:: bash

    $ serenata-toolbox /tmp/serenata-data --module federal_senate chamber_of_deputies

Yet, you can specify a specific year:

.. code-block:: bash

    $ serenata-toolbox --module chamber_of_deputies --year 2009

Or use it all together:

.. code-block:: bash

    $ serenata-toolbox /tmp/serenata-data --module federal_senate --year 2017

Finally, you might want to get help:

.. code-block:: bash

    $ serenata-toolbox --help

Example 2: Using Python
^^^^^^^^^^^^^^^^^^^^^^^

Another option is creating your own Python scripts:

.. code-block:: python

  from serenata_toolbox.datasets import Datasets
  datasets = Datasets('data/')

  # now lets see what are the latest datasets available
  for dataset in datasets.downloader.LATEST:
      print(dataset)  # and you'll see a long list of datasets!

  # and let's download one of them
  datasets.downloader.download('2018-01-05-reimbursements.xz')  # yay, you've just downloaded this dataset to data/

  # you can also get the most recent version of all datasets:
  latest = list(datasets.downloader.LATEST)
  datasets.downloader.download(latest)

Example 3: Using shortcuts
^^^^^^^^^^^^^^^^^^^^^^^^^^

If the last example doesn't look that simple, there are some fancy shortcuts available:

.. code-block:: python

  from serenata_toolbox.datasets import fetch, fetch_latest_backup
  fetch('2018-01-05-reimbursements.xz', 'data/')
  fetch_latest_backup( 'data/')  # yep, we've just did exactly the same thing

Example 4: Generating datasets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you ever wonder how did we generated these datasets, this toolbox can help you too (at least with the most used used ones — the other ones are generated `in our main repo <https://github.com/okfn-brasil/serenata-de-amor/blob/51fad8c807cb353303c5f5a3f945693feeb82015/CONTRIBUTING.md#the-toolbox-and-our-the-source-files-researchsrc>`_):

.. code-block:: python

    from serenata_toolbox.chamber_of_deputies.reimbursements import Reimbursements as ChamberDataset
    from serenata_toolbox.companies.dataset import Dataset as CompaniesDataset
    from serenata_toolbox.federal_senate.dataset import Dataset as SenateDataset

    chamber = ChamberDataset('2018', 'data/')
    chamber()

    senate = SenateDataset('data/')
    senate.fetch()
    senate.translate()
    senate.clean()

    companies = CompaniesDataset('data/')
    companies()

Documentation (WIP)
-------------------

The `full documentation <https://serenata-toolbox.readthedocs.io>`_ is still a work in progress. If you wanna give us a hand you will need `Sphinx <http://www.sphinx-doc.org/>`_:

.. code-block:: bash

  $ cd docs
  $ make clean;make rst;rm source/modules.rst;make html

Contributing
------------

Firstly, you should create a development environment with Python's `venv <https://docs.python.org/3/library/venv.html#creating-virtual-environments>`_ module to isolate your development. Then clone the repository and build the package by running:

.. code-block:: bash

  $ git clone https://github.com/okfn-brasil/serenata-toolbox.git
  $ cd serenata-toolbox
  $ python setup.py develop

Always add tests to your contribution — if you want to test it locally before opening the PR:

.. code-block:: bash

  $ pip install tox
  $ tox

When the tests are passing, also check for coverage of the modules you edited or added — if you want to check it before opening the PR:

.. code-block:: bash

  $ tox
  $ open htmlcov/index.html

Follow `PEP8 <https://www.python.org/dev/peps/pep-0008/>`_ and its best practices implemented by `Landscape <https://landscape.io>`_ in the `veryhigh` strictness level — if you want to check them locally before opening the PR:

.. code-block:: bash

  $ pip install prospector
  $ prospector -s veryhigh serenata_toolbox

If this report includes issues related to `import` section of your files, `isort <https://github.com/timothycrosley/isort>`_ can help you:

.. code-block:: bash

  $ pip install isort
  $ isort **/*.py --diff

Always suggest a version bump. We use `Semantic Versioning <http://semver.org>`_ – or in `Elm community words <https://github.com/elm-lang/elm-package#version-rules>`_:

* MICRO: the API is the same, no risk of breaking code
* MINOR: values have been added, existing values are unchanged
* MAJOR: existing values have been changed or removed

This is really important because every new code merged to `master` triggers the CI and then the CI triggers a new release to PyPI. The attemp to roll out a new version of the toolbox will fail without a version bump. So we do encorouge to add a version bump even if all you have changed is the `README.rst` — this is the way to keep the `README.rst` updated in PyPI.

If you are not changing the API or `README.rst` in any sense and if you really do not want a version bump, you need to add `[skip ci]` to you commit message.

And finally take *The Zen of Python* into account:

.. code-block:: bash

  $ python -m this
