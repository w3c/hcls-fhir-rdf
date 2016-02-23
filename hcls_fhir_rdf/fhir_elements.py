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
""" This package interprets the snapshot view of a FHIR StructuredDefinition resource.
"""
import jsonasobj
from collections import OrderedDict
from typing import Optional

from defaults import log_info, log_warning, log_error
from fhir_types import fhir_type_for
from utils import *
from namespaces import Namespaces

# Type aliases
ShExC = str
XML = str
JSON = jsonasobj.JsonObj


class PathElements:
    """ A complete dictionary of defined elements
    """
    def __init__(self, file_name: Optional[str] = None):
        """ A complete dictionary of defined elements
        :param file_name: File that the elements are defined in (for logging)
        """
        self.entries = OrderedDict()              # Dict[str, PathElement]
        self.file_name = file_name                # input file for logging
        self.jsonf = None                         # json image of input file
        self.namespaces = Namespaces('http://hl7.org/fhir/StructureDefinition/')
        self.path_map = {}                        # map from path to name (Dict[str, str])

    def __iter__(self):
        return self.entries

    @staticmethod
    def inp_filtr(input_fn: str) -> bool:
        """ Vote on whether the input file should be processed
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
        self.jsonf = jsonasobj.load(open(file_name))
        defn_type = 'differential' if differential else 'snapshot'
        if defn_type not in self.jsonf:
            log_warning("'%s' not found" % defn_type, self.file_name)
            return False

        # If we are dealing with a constrained type:
        #  1) Record the fact that the base type is referenced from this file
        #  2) Create a map from the constrained elements back to the base
        constrained_type = {}                        # map from base type to constraint name
        if self.jsonf.get('type') == 'constraint':
            for element in self.jsonf.differential.element:
                if 'name' in element:
                    assert '[x]' not in element.path, "Renaming a parameterized type is too wierd"
                    path_name = PathElement.name_for(element, element.type[0])
                    self.entries.setdefault(path_name,
                                            PathElement(self.file_name, self.namespaces)).add_file_ref(file_name)
                    constrained_type[path_name] = element.name

        # Iterate over the element constraints
        for element in [e for e in self.jsonf[defn_type].element if 'name' in e]:
            if element.name in self.entries:
                log_warning('Name %s is referenced multiple times' % element.name, self.file_name)
            self.entries[element.name] = PathElement(self.file_name, self.namespaces)
            self.entries[element.name].defining_file(element.name, file_name)
            self.entries[element.name].constraints[element.path] = Properties(self.file_name)
            if 'path' in element:
                self.path_map[element.path] = element.name

        for element in [e for e in self.jsonf[defn_type].element if 'name' not in e]:
            if 'type' in element and len(element.type) > 1:
                log_warning("%s has multiple types and is not a choice or reference union" % element.path)
            self.add_to_parent(element, constrained_type, file_name)
        return len(self.jsonf[defn_type].element) > 0

    def add_to_parent(self, element: JSON, constrained_type: dict, file_name: str) -> None:
        """ Add a path element for each type referenced in element
        :param element: element to add
        :param constrained_type: type being extended/constrained if any
        :param file_name: name of the file that the information is coming from
        """
        if 'type' not in element:
            if 'nameReference' in element:
                # TODO: follow and resolve nameReference
                pass
            else:
                log_error("Untyped element %s" % element.path)
            return
        # TODO: Check constraints -- do we need values here
        if self.jsonf.get('type') == 'constraint':
            for possible_value in element.type:
                prop_name = PathElement.name_for(element, possible_value)
                if '.' in prop_name:
                    pname, prop = prop_name.rsplit('.', 1)
                    parent = constrained_type.get(pname, pname)
                    parent_element = self.get_entry(parent)
                    parent_element.defining_file(parent, file_name)
                    parent_element.add_constraint(pname, prop, element)
        else:
            prop_name = element.path.replace('[x]', '')
            if '.' in element.path:
                pname, prop = prop_name.rsplit('.', 1)
            else:
                pname, prop = self.jsonf.id, prop_name
            if pname in self.path_map:
                pname = self.path_map[pname]
            parent = constrained_type.get(pname, pname)
            parent_element = self.get_entry(parent)
            parent_element.defining_file(parent, file_name)
            parent_element.add_property(prop, element)

    def get_entry(self, entry_name):
        """ Return or create the a PathElement for entry_name
        :param entry_name: name of the entry
        :return: PathElement for entry_name
        """
        if entry_name in self.entries:              # Don't invoke constructor if not needed
            return self.entries[entry_name]
        return self.entries.setdefault(entry_name, PathElement(self.file_name, self.namespaces))

    @property
    def as_dict(self) -> dict:
        return {k: v.as_dict for k, v in self.entries.items()}

    @property
    def as_xml(self) -> XML:
        return '<l:fhirdefs xmlns:l="http://local-mods">\n' + \
               '\n'.join([t1 + '<path>\n' + t2 + '<fhir_path>' + k + '</fhir_path>\n' + v.as_xml(k) +
                          t1 + '</path>' for k, v in self.entries.items()]) + \
               '\n</l:fhirdefs>'

    @property
    def as_shexc(self) -> ShExC:
        # Have to do this part first to get all the namespaces recoreded
        self.namespaces.reference_ns('fhir')
        self.namespaces.reference_ns(' ')
        definitions = '\n}\n\n'.join(['<%(k)s> {\n\ta [fhir:%(k)s]?' % {'k': k} +
                                      (',\n\t' if self.entries.items else '\n') +
                                      v.as_shexc() for k, v in self.entries.items()]) + '\n}'

        return self.namespaces.as_shexc() + '\nBASE <http://hl7.org/fhir/StructureDefinition/>\n\n' + definitions


class PathElement:
    """ An Element definition or reference in a json definition
    """
    def __init__(self, file_name: str, ns: Namespaces) -> None:
        self.defined_in = ''
        self.referenced_in = set()
        self.file_name = file_name
        self.properties = Properties(file_name)
        self.constraints = {}           # Dict[str, Properties]
        self.namespaces = ns

    def add_constraint(self, rootname: str, prop_name: str, element_defn: JSON) -> None:
        self.constraints.setdefault(rootname, Properties(self.file_name)).add_entry(prop_name,
                                                                                    self._new_prop(element_defn))

    def add_property(self, prop_name: str, element_defn: JSON) -> None:
        self.properties.add_entry(prop_name, self._new_prop(element_defn))

    @staticmethod
    def name_for(element_defn: JSON, type_defn: JSON) -> str:
        """ Return the name for the supplied element definition
        :param element_defn: Element Definition
        :param type_defn: Element type definition. Needed if element path is parameterized
        :return: element name
        """
        return element_defn.path.replace('[x]', PathElement.type_name(type_defn))

    @staticmethod
    def type_name(type_defn: JSON) -> str:
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

    def _new_prop(self, element_defn: JSON):
        return Property(element_defn, self.namespaces)

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

    def as_shexc(self) -> ShExC:
        return self.properties.as_shexc() + ''.join([props.as_shexc() for k, props in self.constraints.items()])


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

    def as_shexc(self) -> ShExC:
        return ',\n\t'.join([v.as_shexc() for k, v in self.entries.items()])


class Property:
    """ A typed property.  Represents FHIR type/min/max/path tuple

    >>> ns = Namespaces("http://hl7.org/fhir/StructureDefinition/")
    >>> t = '''{"type": [ {"code": "CodeableConcept"} ], "min": 0, "max": "*",
    ...     "path": "MedicationOrder.substitution.reason"}'''
    >>> Property(jsonasobj.loads(t), ns).as_shexc()
    ':MedicationOrder.substitution.reason @<CodeableConcept>*'

    >>> t = '''{"type": [ {"code": "CodeableConcept"}, {"code": "Reference",
    ...         "profile": ["http://hl7.org/fhir/StructureDefinition/Medication"]}], "min": 1, "max": "1",
    ...         "path": "MedicationOrder.medication[x]"}'''
    >>> Property(jsonasobj.loads(t), ns).as_shexc()
    '( :MedicationOrder.medicationCodeableConcept @<CodeableConcept> |\\n\\t  :MedicationOrder.medicationReference { fhir:reference @<Medication> }\\n\\t)'

    >>> t = '''{"type": [ {"code": "Identifier"} ], "min": 1, "max": "*",
    ...     "path": "MedicationOrder.identifier"}'''
    >>> Property(jsonasobj.loads(t), ns).as_shexc()
    ':MedicationOrder.identifier @<Identifier>+'

    >>> t = '''{"type": [ {"code": "dateTime"} ], "min": 0, "max": "1",
    ...     "path": "MedicationDispense.whenPrepared"}'''
    >>> Property(jsonasobj.loads(t), ns).as_shexc()
    ':MedicationDispense.whenPrepared fhir:dateTime?'

    >>> t = '''{"type": [ {"code": "Quantity", "profile": ["http://hl7.org/fhir/StructureDefinition/SimpleQuantity"]}],
    ...     "min": 0, "max": "1",
    ...     "path": "MedicationDispense.quantity"}'''
    >>> Property(jsonasobj.loads(t), ns).as_shexc()
    ':MedicationDispense.quantity @<SimpleQuantity>?'

    >>> t = '''{"type": [ { "code": "Range"},
    ...                   { "code": "Quantity", "profile": [ "http://hl7.org/fhir/StructureDefinition/SimpleQuantity"]}],
    ...      "min": 1, "max": "*", "path":"MedicationOrder.dosageInstruction.dose[x]"}'''
    >>> Property(jsonasobj.loads(t), ns).as_shexc()
    '( :MedicationOrder.dosageInstruction.doseRange @<Range> |\\n\\t  :MedicationOrder.dosageInstruction.doseQuantity @<SimpleQuantity>\\n\\t)+'

    """
    card_map = {(0, 1): "?",
                (1, 1): "",
                (0, "*"): "*",
                (1, "*"): "+"}

    def __init__(self, entry: JSON, ns: Namespaces) -> None:
        """ Add a new property
        :param entry: representation of a FHIR property entry (path, min, max, deifnition, type, etc.)
        """
        self.min = entry.min
        self.max = '*' if entry.max == '*' else int(entry.max)
        self.path = entry.path.replace('[x]', '')
        self.is_choice = '[x]' in entry.path
        self.types = [fhir_type_for(t, self.path, ns) for t in entry.type] if 'type' in entry \
            else [fhir_type_for(None, self.path, ns)]

    def as_dict(self) -> dict:
        return self.__dict__

    @property
    def as_xml(self) -> XML:
        rel_path = dotted_cdr(self.path)
        rval = t4 + '<relative_xpath>f:' + rel_path + '</relative_xpath>\n'
        rval += t4 + t4.join(['<type>%s</type>\n' % t.type_name for t in self.types]) + '\n'
        return rval

    def as_shexc(self) -> ShExC:
        card = self.card_map.get((self.min, self.max), "{%d,%s}" % (self.min, self.max if self.max != '*' else ''))
        # rel_path = rightmost(self.path)
        rel_path = self.path

        if len(self.types) > 1:
            if not self.is_choice:
                type_text = '( ' + ' OR\n\t  '.join([t.as_shexc() for t in self.types]) + '\n\t)'
            else:
                type_text = '( ' + \
                            ' |\n\t  '.join([':%s%s ' % (rel_path, t.base_type) + t.as_shexc() for t in self.types]) + \
                            '\n\t)'
        else:
            type_text = self.types[0].as_shexc()
        return ((':%s ' % rel_path) if not self.is_choice else '') + type_text + card
