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


Installation
------------

As this is a work in progress, clone the repo and use it within your virtualenv.

::

  $ git clone https://github.com/datasciencebr/serenata-toolbox.git
  $ python setup.py develop

serenata_toolbox is compatible with Python 3+

Usage
-----

If you plan to upload data to a S3 server you should copy `config.ini.example` as `config.ini` and edit it with your own credentials.

.. code:: python

  $ python3
  >>> from serenata_toolbox import xml2csv
  >>> xml2csv.output('Spam and eggs')
  2016-12-01 18:14:26 Spam and eggs

Full Documentation
------------------

https://serenata_toolbox.readthedocs.io

Build documentation locally
---------------------------

You will need sphinx installed in your machine

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

License
-------

MIT licensed.
