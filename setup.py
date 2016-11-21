from setuptools import setup

REPO_URL = 'http://github.com/datasciencebr/serenata-toolbox'


setup(
    author='Serenata de Amor',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
    description='Toolbox for Serenata de Amor project',
    install_requires=[
        'numpy>=1.11',
        'pandas>=0.18',
    ],
    keywords='serenata de amor, data science, brazil, corruption',
    license='MIT',
    long_description='Check `Serenata Toolbox at GitHub <{}>`_.'.format(REPO_URL),
    name='serenata-toolbox',
    packages=['serenata_toolbox'],
    url=REPO_URL,
    version='0.0.1'
)
