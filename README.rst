.. image:: https://readthedocs.org/projects/serenata-toolbox/badge/?version=latest
   :target: http://serenata-toolbox.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://landscape.io/github/jonDel/serenata-toolbox/master/landscape.svg?style=flat
   :target: https://landscape.io/github/jonDel/serenata-toolbox/master
   :alt: Code Health

.. image:: https://img.shields.io/pypi/v/serenata_toolbox.svg
   :target: https://pypi.python.org/pypi/serenata_toolbox/
   :alt: Latest PyPI version



Serenata de Amor Toolbox
========================

`PyPI <https://pypi.python.org/>`_  package to support `Serenata de Amor <https://github.com/datasciencebr/serenata-de-amor>`_
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

Source Code
-----------

Feel free to fork, evaluate and contribute to this project.

Source: https://github.com/datasciencebr/serenata-toolbox/

License
-------

MIT licensed.
