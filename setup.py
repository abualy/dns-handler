# Encoding: UTF-8
"""
dns handler setup
"""

from setuptools import setup, find_packages

setup(
    name='dnshandler',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[],
    package_data={'dnshandler': ['config/*.json']},
)
