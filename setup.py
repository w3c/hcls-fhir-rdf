# -*- coding: utf-8 -*-
"""
hcls_fhir_rdf
====

Tools for RDF representations for FHIR
"""

from distutils.core import setup
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'hcls_fhir_rdf'))
import hcls_fhir_rdf

long_description = """Tools for RDF representations for FHIR"""

setup(
    name='hcls_fhir_rdf',
    provides=['hcls_fhir_rdf'],
    install_requires=['dirlistproc', 'jsonasobj'],
    version=hcls_fhir_rdf.__version__,
    description='FHIR to RDF conversion tools',
    long_description=long_description,
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    url='http://github.com/w3c/hcls-fhir-rdf',
    packages=['hcls_fhir_rdf'],
    scripts=['scripts/generate_fhir_definitions'],
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3'
    ],
)

