# -*- coding: utf-8 -*-
"""
hcls_fhir_rdf
====

Tools for RDF representations for FHIR
"""
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# typing library was introduced as a core module in version 3.5.0
if sys.version_info < (3, 5):
    v34_requires = ["typing"]
else:
    v34_requires = []

sys.path.append(os.path.join(os.path.dirname(__file__), 'hcls_fhir_rdf'))
import hcls_fhir_rdf

long_description = """Tools for RDF representations for FHIR"""

setup(
    name='hcls_fhir_rdf',
    provides=['hcls_fhir_rdf'],
    version=hcls_fhir_rdf.__version__,
    description='FHIR to RDF conversion tools',
    long_description=long_description,
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    url='http://github.com/w3c/hcls-fhir-rdf',
    packages=['hcls_fhir_rdf'],
    scripts=['scripts/download_fhir_spec', 'scripts/generate_shex', 'scripts/generate_xml_definitions',
             'scripts/generate_rdf'],
    data_files=[('share/xsl', ['share/xsl/transform.xsl'])],
    license='BSD 3-Clause license',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=['dirlistproc', 'requests', 'jsonasobj', 'rdflib', 'rdflib_jsonld', 'pyjxslt'] + v34_requires,
)
