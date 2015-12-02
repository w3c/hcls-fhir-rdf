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

import argparse
import os
import sys
import logging
import json
from zipfile import ZipFile
from dirlistproc import DirectoryListProcessor

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.join(os.getcwd(), os.path.dirname(__file__)), '..'))

from hcls_fhir_rdf.download_fhir_spec import download_spec
from hcls_fhir_rdf.generate_paths import Elements

DEFAULT_SPEC_URL = "http://www.hl7.org/implement/standards/fhir/2015May/fhir-spec.zip"
DEFAULT_TARGET_FILE = "fhir-spec.zip"
DEFAULT_INPUT_DIRECTORY = os.path.join('..', 'data')
DEFAULT_LOG_FILE = "extract.log"

elements = Elements()


def proc_profiles(input_fn: str, _, opts: argparse.Namespace) -> bool:
    """ Process a FHIR profile file (json format)
    :param input_fn: name of the file to process
    :param opts: process options
    :return: True if file was processed, false if it was skipped
    """
    logging.info("Processing %s" % input_fn)
    return elements.add_file(input_fn, opts.differential)


def inp_filtr(input_fn: str) -> bool:
    """ Determine which files should be processed
    :param input_fn: file name to test
    :return: True if it should be processed, False if it is to be skipped
    """
    reason = None
    if '-' in input_fn:
        reason = "name contains a hyphen (-)"
    elif input_fn.endswith(".xml.profile.json"):
        reason = "ends with .xml.profile.json"
    if reason:
        logging.info("\t%s skipped %s" % (input_fn, reason))
    return reason is None


def addargs(args: argparse.ArgumentParser) -> None:
    """ Add local args to the dirlistproc set
    :param args: dirlistproc arguments
    """
    args.add_argument("-url", "--url", help="URL of FHIR specification to download", default=DEFAULT_SPEC_URL)
    args.add_argument("-r", "--refresh", help="Re-download the FHIR specification even if it already exists ",
                      action="store_true")
    args.add_argument("--unzip", help="(Re)-unzip the specification", action="store_true")
    args.add_argument("-df", "--download_file", help="Target download file", default=DEFAULT_TARGET_FILE)
    args.add_argument("--logfile", help="Logging file. Default is <inpdir>/extract.log")
    args.add_argument("--differential", help="Process differential definitions. (default: snapshot)",
                      action="store_true")
    args.add_argument("-of", "--output_format", help="Output format", choices=['xml', 'json'], default='json')
    args.add_argument("-ex", "--exampledir", help="Unzip examples into this directory")
    # TODO: provide an option to clear out the site directory if re-unziping


def procargs(opts: argparse.Namespace) -> None:
    """ Evaluate the return arguments
    :param opts: argument parser output
    """
    if not opts.indir:
        opts.indir = DEFAULT_INPUT_DIRECTORY
    download_target = os.path.join(opts.indir, opts.download_file)
    if not opts.logfile:
        opts.logfile = os.path.join(opts.indir, DEFAULT_LOG_FILE)
    logging.basicConfig(filename=opts.logfile, level=logging.INFO, filemode='w')
    success, need_unzip = download_spec(opts.url, download_target, opts.refresh)
    if opts.unzip or need_unzip:
        logging.info("Unzipping %s into %s" % (download_target, opts.indir))
        zf = ZipFile(download_target)
        file_names = [n for n in zf.namelist() if n.endswith(".profile.json")]
        zf.extractall(opts.indir, members=file_names)
        if opts.exampledir:
            logging.info("Unzipping examples into %s" % opts.exampledir)
            file_names = [n for n in zf.namelist() if n.endswith("-example.xml")]
            zf.extractall(opts.exampledir, members=file_names)




def main():
    dlp = DirectoryListProcessor(None, "Generate XSLT definitions for FHIR", ".profile.json", None, addargs, procargs)
    nfiles, nsuccess = dlp.run(proc_profiles, inp_filtr)
    if dlp.opts.output_format == 'json':
        output = json.dumps(elements.as_dict, indent=4, sort_keys=True)
    else:
        output = elements.as_xml
    print(output, file=open(dlp.opts.outfile[0], 'w') if dlp.opts.outfile else sys.stdout)
    logging.info("Total=%d Successful=%d" % (nfiles, nsuccess))


if __name__ == '__main__':
    main()
