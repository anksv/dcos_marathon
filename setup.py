"""A module to deploy apps to Marathon using DCOS authentication.
See:
https://github.com/cpdevws/dcos_marathon
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dcos_marathon',
    version='1.0.2',
    description='A DCOS Marathon API Client',
    long_description=long_description,
    url='https://github.com/cpdevws/dcos_marathon',
    author='Chaitanya Namburi, Kaushik C',
    author_email='cpdevws@gmail.com, kaushik.chand@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=['marathon', 'jsonschema']
)
