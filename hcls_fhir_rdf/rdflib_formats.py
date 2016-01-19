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
from rdflib import plugin
from rdflib.parser import Parser as rdf_Parser
from rdflib.serializer import Serializer as rdf_Serializer
from typing import List, Union

Parser = rdf_Parser
Serializer = rdf_Serializer

SUFFIX_FORMAT_MAP = {
    'xml': 'rdf',
    'turtle': 'ttl',
    'rdfa': 'html',
    'nquads': 'nq'
}


def known_formats(use: Union[Serializer, Parser]=Serializer, include_mime_types: bool = False) -> List[str]:
    """ Return a list of available formats in rdflib for the required task
    :param use: task (typically Serializer or Parser)
    :param include_mime_types: whether mime types are included in the return list
    :return: list of formats
    """
    return sorted([name for name, kind in plugin._plugins.keys()
                   if kind == use and (include_mime_types or '/' not in name)])


def suffix_for(fmt: str) -> str:
    return SUFFIX_FORMAT_MAP.get(fmt, fmt)
