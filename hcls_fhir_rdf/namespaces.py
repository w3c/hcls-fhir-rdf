# Copyright (c) 2016, Mayo Clinic
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
from functools import reduce
from typing import Tuple, Optional
from collections import OrderedDict

ShExC = str

nsmap = {'xhtml': "http://www.w3.org/1999/xhtml",
         'GenX': 'http://shex.io/extensions/GenX/',
         '': 'http://hl7.org/fhir/'}

nsmap2 = {'fhir': "http://hl7.org/fhir/",
          ' ': "http://hl7.org/fhir/"}

# Taken from http://www.w3.org/2013/json-ld-context/rdfa11
rdfa_nsmap = {
    "cat": "http://www.w3.org/ns/dcat#",
    "qb": "http://purl.org/linked-data/cube#",
    "grddl": "http://www.w3.org/2003/g/data-view#",
    "ma": "http://www.w3.org/ns/ma-ont#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfa": "http://www.w3.org/ns/rdfa#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "rif": "http://www.w3.org/2007/rif#",
    "rr": "http://www.w3.org/ns/r2rml#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "skosxl": "http://www.w3.org/2008/05/skos-xl#",
    "wdr": "http://www.w3.org/2007/05/powder#",
    "void": "http://rdfs.org/ns/void#",
    "wdrs": "http://www.w3.org/2007/05/powder-s#",
    "xhv": "http://www.w3.org/1999/xhtml/vocab#",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "prov": "http://www.w3.org/ns/prov#",
    "sd": "http://www.w3.org/ns/sparql-service-description#",
    "org": "http://www.w3.org/ns/org#",
    "gldp": "http://www.w3.org/ns/people#",
    "cnt": "http://www.w3.org/2008/content#",
    "dcat": "http://www.w3.org/ns/dcat#",
    "earl": "http://www.w3.org/ns/earl#",
    "ht": "http://www.w3.org/2006/http#",
    "ptr": "http://www.w3.org/2009/pointers#",
    "cc": "http://creativecommons.org/ns#",
    "ctag": "http://commontag.org/ns#",
    "dc": "http://purl.org/dc/terms/",
    "dc11": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "gr": "http://purl.org/goodrelations/v1#",
    "ical": "http://www.w3.org/2002/12/cal/icaltzd#",
    "og": "http://ogp.me/ns#",
    "rev": "http://purl.org/stuff/rev#",
    "sioc": "http://rdfs.org/sioc/ns#",
    "v": "http://rdf.data-vocabulary.org/#",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "schema": "http://schema.org/",
    "describedby": "http://www.w3.org/2007/05/powder-s#describedby",
    "license": "http://www.w3.org/1999/xhtml/vocab#license",
    "role": "http://www.w3.org/1999/xhtml/vocab#role"
}

nsmaps = [nsmap, nsmap2, rdfa_nsmap]


class Namespaces:
    def __init__(self, base: Optional[str] = None) -> None:
        self.used_namespaces = OrderedDict()
        self.base = base

    def nsname(self, uri: str) -> Tuple[str, str]:
        """
        Map a URI to a nsname
        :param uri: uri to map
        :return: ns/name tuple

        >>> n = Namespaces('http://hl7.org/fhir/StructureDefinition/')
        >>> n.nsname("http://hl7.org/fhir/simple")
        ('', 'simple')

        >>> n.nsname("http://hl7.org/fhir/StructureDefinition/longer")
        (None, 'longer')

        >>> n.nsname("http://hl7.org/fhir/Extension/something")
        ('', 'Extension/something')

        >>> n.nsname("http://www.w3.org/2001/XMLSchema#Integer")
        ('xsd', 'Integer')

        >>> n.nsname("http://www.w3.org/2001/XMLSchema#")
        ('xsd', '')

        >>> n.nsname("http://example.org/2001/XMLSchema#Integer")
        (None, 'http://example.org/2001/XMLSchema#Integer')

        >>> n.as_shexc()
        'PREFIX : <http://hl7.org/fhir/>\\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>'
        >>> n.reference_ns('fhir')
        True
        >>> n.as_shexc()
        'PREFIX : <http://hl7.org/fhir/>\\nPREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\\nPREFIX fhir: <http://hl7.org/fhir/>'

        >>> n.nsname('http://hl7.org/fhir/StructureDefinition/BodySite')
        (None, 'BodySite')

        """
        if self.base and uri.startswith(self.base):
            return None, uri.replace(self.base, '')

        def _do_maps(self) -> Tuple[Optional[str], str]:
            for e in nsmaps:
                km, vm = self.nsname_map(uri, e)
                if km is not None:
                    return km, vm
            return None, uri
        return _do_maps(self)

    def ncname(self, uri: str) -> str:
        """ Convert uri to ncname
        :param uri: uri to convert
        :return: ncname
        """
        k, v = self.nsname(uri)
        return v if not k else (k + ':' + v)

    def nsname_map(self, uri: str, map_: dict) -> Tuple[Optional[str], str]:
        """
        Interpret uri against the supplied ns/name map
        :param uri: uri to transform
        :param map_: map to transform against
        :return: ns, name
        """
        k, v = reduce(lambda e1, e2: e1 if len(e1[1]) > len(e2[1]) else e2,
                      [e for e in map_.items() if uri.startswith(e[1])], ('', ''))
        if v:
            self.used_namespaces[k] = v
        return (k, uri.replace(v, '')) if v else (None, uri)

    def reference_ns(self, ns: str) -> bool:
        """ Add a reference to the supplied namespace
        :param ns: namespace prefix
        :return: True if added, False if unknown
        """
        for e in nsmaps:
            if ns in e:
                self.used_namespaces[ns] = e[ns]
                return True
        return False

    @staticmethod
    def touri(ns: str, name: str) -> str:
        """
        Convert a ns/name to an absolute URI
        :param ns:
        :param name:
        :return:
        """

        return nsmap[ns] + name if ns in nsmap else ns + name

    def as_shexc(self) -> ShExC:
        return '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in self.used_namespaces.items()])

