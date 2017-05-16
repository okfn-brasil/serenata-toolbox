.. image:: https://travis-ci.org/datasciencebr/serenata-toolbox.svg?branch=master
   :target: https://travis-ci.org/datasciencebr/serenata-toolbox
   :alt: Travis CI build status (Linux)

.. image:: https://readthedocs.org/projects/serenata-toolbox/badge/?version=latest
   :target: http://serenata-toolbox.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://landscape.io/github/datasciencebr/serenata-toolbox/master/landscape.svg?style=flat
   :target: https://landscape.io/github/datasciencebr/serenata-toolbox/master
   :alt: Code Health

.. image:: https://coveralls.io/repos/github/datasciencebr/serenata-toolbox/badge.svg?branch=master
   :target: https://coveralls.io/github/datasciencebr/serenata-toolbox?branch=master
   :alt: Coveralls

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

Example:

.. code:: python

  $ python3
  >>> from serenata_toolbox.datasets import Dataset
  >>> dataset = Dataset('/tmp/serenata-data')
  >>> tuple(dataset.local.all)

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
