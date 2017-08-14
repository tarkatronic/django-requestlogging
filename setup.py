#!/usr/bin/env python
import os

from setuptools import find_packages, setup


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open('README.rst', 'r') as f:
    README = f.read()

with open('VERSION', 'r') as vfile:
    VERSION = vfile.read().strip()


setup(
    name='django-requestlogging-redux',
    version=VERSION,
    description='Adds information about requests to logging records.',
    long_description=README,
    author='TrustCentric',
    author_email='admin@trustcentric.com',
    maintainer='Joey Wilhelm',
    maintainer_email='tarkatronic@gmail.com',
    url='https://github.com/tarkatronic/django-requestlogging',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['Django>=1.8'],
    test_suite='runtests.runtests'
)
