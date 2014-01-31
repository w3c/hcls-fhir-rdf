from xml.etree import ElementTree
from xml.dom.minidom import parseString
import glob, json, re, os, sys
from huTools.structured import dict2xml, dict2et

#FHIR_DIR = "/home/jmandel/smart/fhir"
# the directory with e.g. alert.profile.json and a bazillion others in it
PROFILE_DIR = os.environ.get('PROFILE_DIR')
if PROFILE_DIR == None:
    FHIR_DIR = os.environ.get('FHIR_DIR')
    if FHIR_DIR == None:
        FHIR_DIR = "/home/jmandel/smart/fhir"
    PROFILE_DIR = FHIR_DIR + "/build/publish"

def tree(FILES):
    paths = {}
    def process(file):

        if file.endswith("-extensions.profile.json"): return
        if file.endswith("extensions-spreadsheet.profile.json"): return
        if file.endswith(".xml.profile.json"): return
        if file.endswith("iso-21090.profile.json"): return
        f = json.load(open(file))
        if 'structure' not in f:
            print >> sys.stderr, "NOT IN", file
            return
        for v in f['structure'][0]['element']:

            #split a given property into multiple strands when it's like:
            # value[X] (dateTime|String)
            propertyName = v['path']
            if 'definition' in v and 'type' in v['definition']: types = v['definition']['type']
            else: types = [None]

            for possibleValue in types:
                valueType = possibleValue['code']  if possibleValue else ""
                valueType = valueType.replace("*", "").replace("@", "")
                if (valueType.startswith("Resource(")): valueType = "ResourceReference"
                p = propertyName.replace("[x]", valueType.capitalize())
                parent = ".".join(p.split(".")[:-1])
                paths[p] = {
                    'properties': {},
                    'order': []
                }

                if parent in paths:
                    step =  p.replace(parent+".", "")
                    if step not in paths[parent]['order']: # why did I get e.g. "DiagnosticReport": { "order": [ "extension", "extension", "modifierExtension", "modifierExtension", "text", "contained", "modifierExtension", "text"?
                        paths[parent]['order'].append(step)
                    paths[parent]['properties'][step] = edge = {}
                    if len(valueType) and valueType[0] == valueType[0].lower(): edge['primitiveType'] = valueType
                    elif valueType != "":  edge['type'] = valueType
                    else:  edge['type'] = p
                    if 'definition' in v:
                        edge['min'] = v['definition']['min']
                        edge['max'] = v['definition']['max']

    for f in FILES: process(f)
    oldpaths = paths
    paths = {}
    for k,v in oldpaths.iteritems():
        if len(v['properties'].keys()) >  0: paths[k]=v
    return paths

#t = tree(glob.glob(FHIR_DIR + "/build/publish/*.profile.json"))
t = tree(glob.glob(PROFILE_DIR + "/*.profile.json"))
print json.dumps(t, sort_keys=True,indent=2)
