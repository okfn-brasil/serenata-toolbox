from setuptools import setup

REPO_URL = 'http://github.com/datasciencebr/serenata-toolbox'


setup(
    author='Serenata de Amor',
    author_email='contato@serenata.ai',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    description='Toolbox for Serenata de Amor project',
    zip_safe=False,
    install_requires=[
        'aiofiles',
        'aiohttp',
        'boto3',
        'beautifulsoup4>=4.4',
        'lxml>=3.6',
        'pandas>=0.18',
        'python-decouple>=3.1',
        'tqdm'
    ],
    keywords='serenata de amor, data science, brazil, corruption',
    license='MIT',
    long_description='Check `Serenata Toolbox at GitHub <{}>`_.'.format(REPO_URL),
    name='serenata-toolbox',
    packages=[
        'serenata_toolbox',
        'serenata_toolbox.federal_senate',
        'serenata_toolbox.chamber_of_deputies',
        'serenata_toolbox.datasets'
    ],
    url=REPO_URL,
    python_requires='>=3.6',
    version='14.0.2',
)
