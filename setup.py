#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='django-requestlogging-redux',
    version='1.2.0',
    description='Adds information about requests to logging records.',
    long_description=open('README.rst', 'r').read(),
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
    tests_require=['tox']
)
