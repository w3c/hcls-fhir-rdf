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
""" This package interprets the snapshot view of a FHIR StructuredDefinition resource.
"""
import argparse
import jsonasobj
from collections import OrderedDict
from typing import Optional
from .defaults import log_info, log_warning, log_error


backbone_element = jsonasobj.loads('{"code": "BackboneElement"}')
t1 = '\t'
t2 = '\t' * 2
t3 = '\t' * 3
t4 = '\t' * 4

# Typing aliases
ShExC = str
xml = str


class PathElements:
    """ A complete dictionary of defined elements
    """
    def __init__(self, file_name: Optional[str] = None):
        """ A complete dictionary of defined elements
        :param file_name: File that the elements are defined in (for logging)
        """
        self.entries = {}       # Dict[str, PathEntry]
        self.file_name = file_name

    def __iter__(self):
        return self.entries

    @staticmethod
    def addargs(parser: argparse.ArgumentParser) -> None:
        """ Add local args to the dirlistproc set
        :param parser: Argument parser
        """
        parser.add_argument("--differential", help="Process differential definitions. (default: snapshot)",
                            action="store_true")

    @staticmethod
    def inp_filtr(input_fn: str) -> bool:
        """ Vote on whether input_fn whould be processed
        :param input_fn: file name to test
        :return: True if it should be processed, False if it is to be skipped
        """
        reason = None
        if '-' in input_fn:
            reason = "name contains a hyphen (-)"
        elif input_fn.endswith(".xml.profile.json"):
            reason = "ends with .xml.profile.json"
        if reason:
            log_info("skipped %s" % reason, input_fn)
        return reason is None

    def proc_file(self, file_name: str, differential: bool) -> bool:
        """ Process the supplied file and add its definition to the list
        :param file_name: File to process
        :param differential: True means use 'differential' definition, False 'snapshot'
        :return: True if the file was processed, false if skipped
        """
        self.file_name = file_name
        f = jsonasobj.load(open(file_name))
        defn_type = 'differential' if differential else 'snapshot'
        if defn_type not in f:
            log_warning("'%s' not found" % defn_type, self.file_name)
            return False

        # If we are dealing with a constrained type:
        #  1) Record the fact that the base type is referenced from this file
        #  2) Create a map from the constrained elements back to the base
        constrained_type = {}                        # map from base type to constraint name
        if f.get('type') == 'constraint':
            for element in f.differential.element:
                if 'name' in element:
                    assert '[x]' not in element.path, "Renaming a parameterized type is too wierd"
                    path_name = PathElement.name_for(element, element.type[0])
                    self.entries.setdefault(path_name, PathElement(self.file_name)).add_file_ref(file_name)
                    constrained_type[path_name] = element.name

        # Iterate over the element constraints
        for element in f[defn_type].element:
            if 'name' in element:
                entry = self.entries.setdefault(element.name, PathElement(self.file_name))
                entry.defining_file(element.name, file_name)
                entry.constraints[element.path] = Properties(self.file_name)
            else:
                # Iterate over the list of types adding an element per type
                for possible_value in element.get('type', [backbone_element]):
                    prop_name = PathElement.name_for(element, possible_value)
                    if '.' in prop_name:
                        pname, prop = prop_name.rsplit('.', 1)
                        parent = constrained_type.get(pname, pname)
                        parent_element = self.get_entry(parent)
                        parent_element.defining_file(parent, file_name)
                        if f.get('type') == 'constraint':
                            parent_element.add_constraint(pname, prop, element, possible_value)
                        else:
                            parent_element.add_property(prop, element, possible_value)
        return len(f[defn_type].element) > 0

    def get_entry(self, entry_name):
        """ Return or create the a PathElement for entry_name
        :param entry_name: name of the entry
        :return: PathElement for entry_name
        """
        return self.entries.setdefault(entry_name, PathElement(self.file_name))

    @property
    def as_dict(self) -> dict:
        return {k: v.as_dict for k, v in self.entries.items()}

    @property
    def as_xml(self) -> xml:
        return '<l:fhirdefs xmlns:l="http://local-mods">\n' + \
               '\n'.join([t1 + '<path>\n' + t2 + '<fhir_path>' + k + '</fhir_path>\n' + v.as_xml(k) +
                          t1 + '</path>' for k, v in self.entries.items()]) + \
               '\n</l:fhirdefs>'

    @property
    def as_shexc(self) -> ShExC:
        return 'PREFIX fhir: <http://hl7/org/fhir/>\n' + \
               'PREFIX xhtml: <http://www.w3.org/1999/xhtml>\n' + \
               'PREFIX GenX: <http://shex.io/extensions/GenX/>\n' + \
               'PREFIX xsd: <http://www.w3.org/2001/XMLSchema>\n\n' + \
               '\n}\n\n'.join(['<%(k)sShape> {\n\ta (fhir:%(k)s)?' % {'k': k} +
                               (',\n\t' if self.entries.items else '\n') +
                               self.entries[k].as_shexc(k) for k in sorted(self.entries.keys())]) + \
               '\n}\n\n <LitShape> {\n' + \
               '\tfhir:value LITERAL %GenX:{ @value %},\n' + \
               '\tfhir:id LITERAL? %GenX:{ @id %}\n' + \
               '}'


class PathElement:
    """ An Element definition or reference in a json definition
    """
    def __init__(self, file_name: str) -> None:
        self.defined_in = ''
        self.referenced_in = set()
        self.file_name = file_name
        self.properties = Properties(file_name)
        self.constraints = {}           # Dict[str, Properties]

    def add_constraint(self, rootname: str, prop_name: str,
                       element_defn: jsonasobj.JsonObj, possible_value: jsonasobj.JsonObj) -> None:
        self.constraints.setdefault(rootname, Properties(self.file_name)).add_entry(prop_name,
                                                                                    self._new_prop(element_defn,
                                                                                                   possible_value))

    def add_property(self, prop_name: str, element_defn: jsonasobj.JsonObj, possible_value: jsonasobj.JsonObj) -> None:
        self.properties.add_entry(prop_name, self._new_prop(element_defn, possible_value))

    @staticmethod
    def name_for(element_defn: jsonasobj.JsonObj, type_defn: jsonasobj.JsonObj) -> str:
        """ Return the name for the supplied element definition
        :param element_defn: Element Definition
        :param type_defn: Element type definition. Needed if element path is parameterized
        :return: element name
        """
        return element_defn.path.replace('[x]', PathElement.type_name(type_defn))

    @staticmethod
    def type_name(type_defn: jsonasobj.JsonObj) -> str:
        """ Convert the code portion of a type definition into a string name
        :param type_defn: definition
        :return: name (if any)
        """
        rval = type_defn.get('code', '').replace('*', '').replace('@', '')
        return rval

    def add_file_ref(self, file_name: str) -> None:
        """ Add a file reference to the element
        :param file_name: file that references the element
        :return:
        """
        self.referenced_in.add(file_name)

    def defining_file(self, element_name, file_name: str) -> None:
        if self.defined_in and self.defined_in != file_name:
            log_error("Element %s was already defined in %s" % (element_name, self.defined_in), file_name)
            return
        self.defined_in = file_name
        self.add_file_ref(file_name)

    @staticmethod
    def _new_prop(element_defn: jsonasobj.JsonObj, type_defn: jsonasobj.JsonObj):
        return Property(element_defn.min, element_defn.max, type_defn.get('code'), element_defn.path,
                        type_defn.get('profile'))

    @property
    def as_dict(self):
        rval = dict(references=list(self.referenced_in))
        rval["definition"] = self.defined_in
        if self.constraints:
            rval["constraints"] = {k: v.as_dict for k, v in self.constraints.items()}
        if self.properties.entries:
            rval["properties"] = self.properties.as_dict
        return rval

    def as_xml(self, parent: str) -> str:
        rval = ''
        if self.constraints or self.properties.entries:
            rval += t2 + '<subs>\n'
            for k, v in self.properties.entries.items():
                rval += t3 + '<sub>\n'
                rval += t4 + '<fhir_path>' + parent + '.' + k + '</fhir_path>\n'
                rval += t4 + '<predicate>fhir:' + parent + '.' + k + '</predicate>\n'
                rval += v.as_xml
                rval += t3 + '</sub>\n'
            # TODO constraints
            rval += t2 + '</subs>\n'
        rval += t2 + '<type>' + parent + '</type>\n'
        return rval

    def as_shexc(self, name: str) -> ShExC:
        return self.properties.as_shexc(name) + ''.join([props.as_shexc(k) for k, props in self.constraints.items()])


class Properties:
    """ An ordered collection of named properties
    """
    def __init__(self, file_name: str) -> None:
        self.entries = OrderedDict()
        self.file_name = file_name

    def add_entry(self, target: str, prop):
        if target in self.entries:
            i = 1
            while target + '_' + str(i) in self.entries:
                i += 1
            renamed_target = target + '_' + str(i)
            log_warning("duplicate property %s - renamed to %s" % (target, renamed_target), self.file_name)
            target = renamed_target
        self.entries[target] = prop

    @property
    def as_dict(self) -> dict:
        return [{"id": k, "prop": v.as_dict} for k, v in self.entries.items()]

    def as_shexc(self, name: str) -> ShExC:
        return ',\n\t'.join([v.as_shexc(name + '.' + k) for k, v in self.entries.items()])

# Checked against http://hl7-fhir.github.io/extensibility.html#json-inner  12/04/2015
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
    | fhir:valueCoding @<CodingShape>,
    | fhir:valueCodeableConcept @<CodeableConceptShape>,
    | fhir:valueAttachment @<AttachmentShape>,
    | fhir:valueIdentifier @<IdentifierShape>,
    | fhir:valueQuantity @<QuantityShape>,
    | fhir:valueRange @<RangeShape>,
    | fhir:valuePeriod @<PeriodShape>,
    | fhir:valueRatio @<RatioShape>,
    | fhir:valueHumanName @<HumanNameShape>,
    | fhir:valueAddress @<AddressShape>,
    | fhir:valueContactPoint @<ContactPointShape>,
    | fhir:valueSchedule @<ScheduleShape>,
    | fhir:valueReference @<ReferenceShape>)"""

card_map = {(0, 1): "?",
            (1, 1): "",
            (0, "*"): "*",
            (1, "*"): "+"}


class Property:
    """ A property in a properties list. Carries a min, max and type
    """
    def __init__(self, min_, max_, type_, path, profile) -> None:
        self.min = min_
        self.path = path
        self.max = '*' if max_ == '*' else int(max_)
        if not type_:
            self.type = path
        elif type_[0].lower() == type_[0]:
            self.primitiveType = type_
        else:
            self.type = type_
        if profile:
            self.profile = profile

    @property
    def as_dict(self) -> dict:
        return self.__dict__

    @property
    def as_xml(self) -> xml:
        typ = self.__dict__.get('type') or self.__dict__.get('primitiveType')
        rel_path = self.path if '.' not in self.path else self.path.rsplit('.', 1)[1]
        rval = t4 + '<relative_xpath>f:' + rel_path + '</relative_xpath>\n'
        rval += t4 + '<type>' + typ + '</type>\n'
        return rval

    def as_shexc(self, name: str) -> ShExC:
        card = card_map.get((self.min, self.max), "{%d,%s}" % (self.min, self.max if self.max != '*' else ''))
        if 'primitiveType' in self.__dict__:
            return "fhir:%s @<LitShape>%s %%GenX:{ %s = %%}" % (name, card, name)
        elif self.type == "Extension.value":
            return value_extension
        else:
            return "fhir:%s @<%s>%s  %%GenX:{ %s = %%}" % (name, self.type + "Shape", card, self.type)
