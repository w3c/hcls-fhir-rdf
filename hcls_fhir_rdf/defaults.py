# -*- coding: utf-8 -*-
# Copyright (c) 2015, Mayo Clinic
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#     Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#     Neither the name of the <ORGANIZATION> nor the names of its contributors
#     may be used to endorse or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
import os
import argparse
import logging

DEFAULT_SPEC_URL = "http://www.hl7.org/implement/standards/fhir/2015May/"
DEFAULT_TARGET_DIRECTORY = "data"
DEFAULT_TARGET_FILE = "fhir-spec.zip"
DEFAULT_EXAMPLE_DIRECTORY = "examples"
DEFAULT_RDF_DIRECTORY = "rdf"
DEFAULT_XML_DEFINITIONS = "definitions.xml"
DEFAULT_SHEX_DEFINITIONS = "definitions.shex"

DEFAULT_LOG_FILE = "extract.log"
LOGGING_LEVEL = logging.INFO

DOWNLOAD_CHUNK_SIZE = 8192       # streaming download chunk size


def start_logger(opts: argparse.Namespace, file_name: str) -> None:
    logging.basicConfig(filename=opts.logfile, level=LOGGING_LEVEL, filemode='a',
                        format='%(asctime)s - ' + os.path.basename(file_name) + ' - %(levelname)s - %(message)s')
    logging.info("********** Start ***********")


def fill_defaults(opts: argparse.Namespace) -> None:
    opts.url = opts.url + '/' + opts.file
    opts.file = os.path.join(opts.dir, opts.file)
    opts.exampledir = os.path.join(opts.dir, opts.exampledir)
    opts.logfile = os.path.join(opts.dir, opts.logfile)
    return opts
