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
from typing import Optional

import jsonasobj

DEFAULT_SPEC_URL = "http://hl7.org/fhir"
DEFAULT_TARGET_DIRECTORY = "data"
DEFAULT_TARGET_FILE = "fhir-spec.zip"
DEFAULT_EXAMPLE_DIRECTORY = os.path.join(DEFAULT_TARGET_DIRECTORY, "examples")
DEFAULT_RDF_DIRECTORY = "rdf"
DEFAULT_XML_DEFINITIONS = "definitions.xml"
DEFAULT_SHEX_DEFINITIONS = "definitions.shex"

DEFAULT_LOG_DIRECTORY = "logs"
DEFAULT_LOGGING_LEVEL = logging.getLevelName(logging.WARNING)

DOWNLOAD_CHUNK_SIZE = 8192       # streaming download chunk size


logNames = [logging.getLevelName(l) for l in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]]


def add_default_args(args: argparse.ArgumentParser, main_file_name: str) -> None:
    default_log_file = os.path.join(DEFAULT_LOG_DIRECTORY, os.path.basename(main_file_name) + '.log')
    args.add_argument("--logfile", help="Logging file. Default is '%s'" % default_log_file, default=default_log_file)
    args.add_argument("--loglevel", help="Logging level. Default is %s" % DEFAULT_LOGGING_LEVEL,
                      default=DEFAULT_LOGGING_LEVEL,
                      choices=logNames)


def _fmt(message: str, fname: Optional[str]) -> str:
    return (" (%s) %s" % (fname, message)) if fname else message


def log_info(message: str, fname: Optional[str] = None) -> None:
    logging.info(_fmt(message, fname))


def log_warning(message: str, fname: Optional[str] = None) -> None:
    logging.warning(_fmt(message, fname))


def log_error(message: str, fname: Optional[str] = None) -> None:
    logging.error(_fmt(message, fname))


def log_debug(message: str, fname: Optional[str] = None) -> None:
    logging.debug(_fmt(message, fname))


def start_logger(opts: argparse.Namespace) -> None:
    logging.basicConfig(filename=opts.logfile, level=opts.loglevel, filemode='w',
                        format='%(asctime)s  %(levelname)s - %(message)s')


def fill_defaults(opts: argparse.Namespace) -> None:
    if '//' not in opts.url:
        opts.url = 'http://' + opts.url
    opts.url = opts.url + '/' + opts.file
    opts.file = os.path.join(opts.dir, opts.file)
    return opts
