#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='django-requestlogging',
    version='1.0',
    description=('Adds information about requests to logging records.'),
    long_description=open('README.rst', 'r').read(),
    author='TrustCentric',
    author_email='admin@trustcentric.com',
    url='http://bitbucket.org/trustcentric/django-requestlogging/',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['django_requestlogging'],
    zip_safe=True,
    install_requires=['Django>=1.3']
)
