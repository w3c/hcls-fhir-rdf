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

import unittest

from hcls_fhir_rdf.rdflib_formats import *

# Note that the list of formats will probably evolve as versions of rdflib change.


class RdflibFormatTestCase(unittest.TestCase):
    def test_defaults(self):
        self.assertEqual(['json-ld', 'n3', 'nquads', 'nt', 'pretty-xml', 'trig', 'trix', 'turtle', 'xml'],
                         known_formats(Serializer))
        self.assertEqual(['html', 'hturtle', 'json-ld', 'mdata', 'microdata', 'n3', 'nquads', 'nt', 'rdfa',
                          'rdfa1.0', 'rdfa1.1', 'trig', 'trix', 'turtle', 'xml'], known_formats(Parser))

    def test_mime_types(self):
        self.assertEqual(['application/n-quads', 'application/n-triples', 'application/rdf+xml',
                          'application/trix', 'json-ld', 'n3', 'nquads', 'nt', 'pretty-xml', 'text/n3', 'text/turtle',
                          'trig', 'trix', 'turtle', 'xml'], known_formats(Serializer, True))


class SuffixTestCase(unittest.TestCase):
    def test_suffix(self):
        self.assertEqual('ttl', suffix_for('turtle'))
        self.assertEqual('html', suffix_for('rdfa'))
        self.assertEqual('nq', suffix_for('nquads'))
        self.assertEqual('foo', suffix_for('foo'))

if __name__ == '__main__':
    unittest.main()
