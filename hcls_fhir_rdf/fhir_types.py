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
from json import dumps
import jsonasobj
from defaults import log_error
from typing import Optional


# Checked against http://hl7-fhir.github.io/extensibility.html#json-inner  12/04/2015
from namespaces import Namespaces

value_extension = """ (fhir:valueInteger xsd:integer,
    | fhir:valueDecimal xsd:decimal,
    | fhir:valueDateTime xsd:dateTime,
    | fhir:valueDate xsd:date,
    | fhir:valueInstant xsd:dateTime, #"<instant>"
    | fhir:valueString LITERAL, #"<string>"
    | fhir:valueUri IRI, #"<uri>"
    | fhir:valueBoolean xsd:boolean,
    | fhir:valueCode LITERAL, #"<code>"
    | fhir:valueBase64Binary xsd:base64Binary,
    | fhir:valueCoding @<Coding>,
    | fhir:valueCodeableConcept @<CodeableConcept>,
    | fhir:valueAttachment @<Attachment>,
    | fhir:valueIdentifier @<Identifier>,
    | fhir:valueQuantity @<Quantity>,
    | fhir:valueRange @<Range>,
    | fhir:valuePeriod @<Period>,
    | fhir:valueRatio @<Ratio>,
    | fhir:valueHumanName @<HumanName>,
    | fhir:valueAddress @<Address>,
    | fhir:valueContactPoint @<ContactPoint>,
    | fhir:valueSchedule @<Schedule>,
    | fhir:valueReference @<Reference>)"""


def fhir_type_for(typ: Optional[jsonasobj.JsonObj], path: str, ns: Namespaces):
    """ Fhir Type factory
    :param typ: type entry in FHIR json object
    :param path: containing path
    :param ns: Namespaces object for managing namespaces
    :return: corresponding typ

    Examples:
    >>> ns = Namespaces()
    >>> path = "MedicationOrder.identifier"
    >>> fhir_type_for(jsonasobj.loads('{"code": "Timing"}'), path, ns).as_shexc()
    '@<Timing>'

    >>> fhir_type_for(jsonasobj.loads('{"code": "Reference", "profile": ["http://hl7.org/fhir/StructureDefinition/BodySite"]}'), path, ns).as_shexc()
    '{ fhir:reference @<BodySite> }'

    >>> fhir_type_for(jsonasobj.loads('''{"code": "Reference", "profile":
    ...                                   ["http://hl7.org/fhir/StructureDefinition/BodySite",
    ...                                    "http://hl7.org/fhir/StructureDefinition/AnotherSite"]}'''), path, ns).as_shexc()
    '( { fhir:reference @<BodySite> } OR\\n\\t   { fhir:reference @<AnotherSite> }\\n\\t)'

    >>> fhir_type_for(jsonasobj.loads('{"code": "code"}'), path, ns).as_shexc()
    'fhir:code'

    >>> fhir_type_for(jsonasobj.loads('{"code": "dateTime"}'), path, ns).as_shexc()
    'fhir:dateTime'

    >>> fhir_type_for(jsonasobj.loads('{"code": "Extension"}'), path, ns).as_shexc()
    '{ fhir:extension . }'

    >>> t = jsonasobj.loads('{"code": "Extension", "profile": ["http://hl7.org/fhir/StructureDefinition/us-core-race"]}')
    >>> fhir_type_for(t, path, ns).as_shexc()
    '{ fhir:extension @<http://hl7.org/fhir/StructureDefinition/us-core-race> }'

    >>> t = jsonasobj.loads('''{"code": "Extension", "profile":
    ...                     ["http://hl7.org/fhir/StructureDefinition/us-core-race",
    ...                      "http://hl7.org/fhir/StructureDefinition/us-core-size"]}''')
    >>> fhir_type_for(t, path, ns).as_shexc()
    '( { fhir:extension @<http://hl7.org/fhir/StructureDefinition/us-core-race> } OR\\n\\t{ fhir:extension @<http://hl7.org/fhir/StructureDefinition/us-core-size> }\\n)'

    >>> t = jsonasobj.loads('''{"code": "Reference",
    ...         "profile": ["http://hl7.org/fhir/StructureDefinition/Medication"]}''')
    >>> fhir_type_for(t, path, ns).as_shexc()
    '{ fhir:reference @<Medication> }'

    >>> fhir_type_for(None, path, ns).as_shexc()
    '@<MedicationOrder.identifier>'

    >>> path = "Medication.product"
    >>> t = jsonasobj.loads('{"code": "BackboneElement"}')
    >>> fhir_type_for(t, path, ns).as_shexc()
    '@<Medication.product>'

    # >>> t = jsonasobj.loads('''{ "_code": { "extension": [
    # ...                        { "url": "http://hl7.org/fhir/StructureDefinition/structuredefinition-json-type",
    # ...                             "valueString": "string" },
    # ...                         { "url": "http://hl7.org/fhir/StructureDefinition/structuredefinition-xml-type",
    # ...                             "valueString": "base64Binary" } ] }''')


    """
    if not typ:
        return FhirPathType(path, ns)
    if 'code' in typ:
        if typ.code[0].isalpha() and typ.code[0].islower():
            return FhirPrimitiveType(typ, ns)
        elif typ.code == 'Reference':
            return FhirReferenceType(typ, ns)
        elif typ.code == "Extension":
            return FhirExtensionType(typ, ns)
        elif typ.code == "BackboneElement":
            return FhirBackboneType(path, ns)
        else:
            return FhirVanillaType(typ, ns)
    elif '_code' in typ:
        # TODO: we don't actually know all of the options here, so we're going to take them as they appear
        if 'extension' in typ._code:
            return FhirPrimitiveExtensionType(typ, ns)
    log_error("Unrecognized type entry: " + dumps(typ._as_json, indent='    '))
    return FhirUnknownType(ns)


class FhirType:
    def __init__(self, ns: Namespaces) -> None:
        self.ns = ns

    def as_xml(self) -> str:
        return "<type>%s</type>" % self.type_name

    @property
    def base_type(self):
        return self.type_name

    def as_shexc(self):
        return "@<UNKNOWN>"

    @property
    def type_name(self):
        return "UNKNOWN"


class FhirUnknownType(FhirType):
    pass


class FhirPrimitiveExtensionType(FhirUnknownType):
    def __init__(self, extension: jsonasobj.JsonObj, ns: Namespaces) -> None:
        super().__init__(ns)
        self.extension = extension


class FhirPathType(FhirType):
    """ A type derived from the path when a type isn't supplied

    >>> ns = Namespaces()
    >>> FhirPathType('MedicationOrder.modifierExtension', ns).as_shexc()
    '@<MedicationOrder.modifierExtension>'
    """
    def __init__(self, path: str, ns: Namespaces) -> None:
        super().__init__(ns)
        self.typ = path

    def as_shexc(self) -> str:
        return '@<%s>' % self.type_name

    @property
    def type_name(self):
        return self.typ


class FhirBackboneType(FhirPathType):
    """ A type that references a subtype in the same definition

    >>> ns = Namespaces()
    >>> FhirBackboneType('MedicationOrder.modifierExtension', ns).as_shexc()
    '@<MedicationOrder.modifierExtension>'
    """
    @property
    def type_name(self):
        return self.typ


class FhirVanillaType(FhirType):
    """
    >>> ns = Namespaces()
    >>> FhirVanillaType(jsonasobj.loads('{"code": "Timing"}'), ns).as_shexc()
    '@<Timing>'

    >>> FhirVanillaType(jsonasobj.loads('''{"code": "Quantity",
    ...                                     "profile": ["http://hl7.org/fhir/StructureDefinition/SimpleQuantity"]}'''), ns).as_shexc()
    '@<SimpleQuantity>'
    """
    def __init__(self, typ, ns: Namespaces):
        super().__init__(ns)
        self.type = typ

    def as_shexc(self) -> str:
        return '@<%s>' % self.ns.ncname(self.type_name)

    @property
    def type_name(self):
        return self.type.profile[0] if 'profile' in self.type else self.type.code

    @property
    def base_type(self):
        return self.type.code


class FhirReferenceType(FhirType):
    """ code: Reference, profile [ uri, uri, ...]

    >>> ns = Namespaces()
    >>> FhirReferenceType(jsonasobj.loads('{"code": "Reference", "profile": ["http://hl7.org/fhir/StructureDefinition/BodySite"]}'), ns).as_shexc()
    '{ fhir:reference @<BodySite> }'

    >>> FhirReferenceType(jsonasobj.loads('''{"code": "Reference", "profile":
    ...                                   ["http://hl7.org/fhir/StructureDefinition/BodySite",
    ...                                    "http://hl7.org/fhir/StructureDefinition/AnotherSite"]}'''), ns).as_shexc()
    '( { fhir:reference @<BodySite> } OR\\n\\t   { fhir:reference @<AnotherSite> }\\n\\t)'

    >>> FhirReferenceType(jsonasobj.loads('{"code": "Reference"}'), ns).as_shexc()


    """
    def __init__(self, typ: jsonasobj.JsonObj, ns: Namespaces) -> None:
        super().__init__(ns)
        if 'profile' not in typ or not typ.profile:
            log_error('"code": "Reference"  encountered with no profile')
            # TODO: map this to a shex '.'
            self.profile = []
        else:
            self.profile = typ.profile      # List[uri]

    def as_shexc(self) -> str:
        if not self.profile:
            return '.'
        elif len(self.profile) > 1:
            return '( ' + ' OR\n\t   '.join([self._shexc(p) for p in self.profile]) + '\n\t)'
        else:
            return self._shexc(self.profile[0])

    @property
    def type_name(self):
        return "Reference"

    def _shexc(self, p) -> str:
        return '{ fhir:reference @<%s> }' % self.ns.ncname(p)


class FhirPrimitiveType(FhirType):
    """ code: (any name that starts with a lower case string)

        >>> ns = Namespaces()
        >>> FhirPrimitiveType(jsonasobj.loads('{"code": "code"}'), ns).as_shexc()
        'fhir:code'

        >>> FhirPrimitiveType(jsonasobj.loads('{"code": "dateTime"}'), ns).as_shexc()
        'fhir:dateTime'
    """
    def __init__(self, typ: jsonasobj.JsonObj, ns: Namespaces) -> None:
        super().__init__(ns)
        self.code = typ.code

    def as_shexc(self) -> str:
        return self.type_name

    @property
    def type_name(self):
        return "fhir:" + self.code


class FhirExtensionType(FhirType):
    """
        Example use:
        >>> ns = Namespaces()
        >>> FhirExtensionType(jsonasobj.loads('{"code": "Extension"}'), ns).as_shexc()
        '{ fhir:extension . }'

        >>> t = jsonasobj.loads('{"code": "Extension", "profile": ["http://hl7.org/fhir/StructureDefinition/us-core-race"]}')
        >>> FhirExtensionType(t, ns).as_shexc()
        '{ fhir:extension @<http://hl7.org/fhir/StructureDefinition/us-core-race> }'

        >>> t = jsonasobj.loads('''{"code": "Extension", "profile":
        ...                     ["http://hl7.org/fhir/StructureDefinition/us-core-race",
        ...                      "http://hl7.org/fhir/StructureDefinition/us-core-size"]}''')
        >>> FhirExtensionType(t, ns).as_shexc()
        '( { fhir:extension @<http://hl7.org/fhir/StructureDefinition/us-core-race> } OR\\n\\t{ fhir:extension @<http://hl7.org/fhir/StructureDefinition/us-core-size> }\\n)'

    """
    def __init__(self, typ: jsonasobj.JsonObj, ns: Namespaces):
        super().__init__(ns)
        self.profile = [] if 'profile' not in typ else typ.profile

    def as_shexc(self) -> str:
        return "{ fhir:extension . }" if not self.profile else \
               "{ fhir:extension @<%s> }" % self.profile[0] if len(self.profile) == 1 else \
               "( " + " OR\n\t".join(["{ fhir:extension @<%s> }" % p for p in self.profile]) + "\n)"

    @property
    def type_name(self):
        return "Extension"
