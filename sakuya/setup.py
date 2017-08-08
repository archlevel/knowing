# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='sakuya',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'PyYAML==3.10',
        'bottle==0.11.3',
        'SQLAlchemy==0.7.9',
        'bottle-sqlalchemy==0.3.1',
        'MySQL-python==1.2.3',
        'matplotlib==1.1.1',
        'numpy==1.6.2',            # numpy must be installed first
        'kazoo==0.5',
        'msgpack-python==0.2.2',
        'pyzmq==2.1.7',
        'TurboMail==3.0.3',
        'pycrypto==2.6',
        'pyasn1==0.1.6',
        'pysnmp==4.2.4',
        'pysnmp-mibs==0.1.4'
    ]
)
