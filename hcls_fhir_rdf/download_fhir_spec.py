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

import requests
import os
from datetime import datetime
from typing import Tuple
import logging

chunk_size = 8192       # streaming download chunk size


def download_spec(url: str, target_file: str, force_download: bool) -> Tuple[bool, bool]:
    """ Download the fhir specification in URL into target_file if necessary
    :param url: URL to download zipped fhir specification from
    :param target_file: destination zip file
    :param force_download: if True, force the download. If False, only download if file date > current mod time
    :return: (success, unzip needed)
    """
    try:
        target_file_modtime = datetime.fromtimestamp(os.path.getmtime(target_file))
    except FileNotFoundError:
        logging.info("%s does not currently exist" % target_file)
        force_download = True
        target_file_modtime = None

    if not force_download:
        r = requests.head(url)
        if r.status_code == 200:
            file_date = datetime.strptime(r.headers['Last-Modified'], '%a, %d %b %Y %H:%M:%S GMT')
            force_download = file_date > target_file_modtime
            if force_download:
                logging.info("%s is newer than %s: downloading newer copy" % (url, target_file))
        else:
            logging.error("Error: %d on %s" % (r.status_code, url))
            return False, False

    if force_download:
        logging.info("Downloading %s:" % url)
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(target_file, 'wb') as tf:
                for chunk in r.iter_content(chunk_size):
                    tf.write(chunk)
            return True, True
        else:
            logger.error("Error: %d downloading %s" % (r.status_code, url))
            return False, False

    return True, False



