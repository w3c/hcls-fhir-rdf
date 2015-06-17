from xml.etree import ElementTree
from xml.dom.minidom import parseString
import glob, json, re, sys
from huTools.structured import dict2xml, dict2et

FHIR_DIR = "site"

def tree(FILES):
    paths = {}
    def process(file):

        if file.endswith("-extensions.profile.json"): return
        if file.endswith("extensions-spreadsheet.profile.json"): return
        if file.endswith(".xml.profile.json"): return
        if file.endswith("iso-21090.profile.json"): return
        f = json.load(open(file))
        if 'snapshot' not in f:
            print >> sys.stderr, "didn't find snapshot in", file
            return
        if f['type'] == "constraint":
            print >> sys.stderr, file, " ", f['id'], " extends ", f['base']
        for v in f['snapshot']['element']:

            #split a given property into multiple strands when it's like:
            # value[X] (dateTime|String)
            propertyName = v['path']
            if 'type' in v: types = v['type']
            else: types = [None]
            min = v['min']
            max = v['max']

            for possibleValue in types:
                valueType = possibleValue['code']  if possibleValue else ""
                valueType = valueType.replace("*", "").replace("@", "")
                if (valueType.startswith("Resource(")): valueType = "ResourceReference"
                p = propertyName.replace("[x]", valueType.capitalize())
                parent = ".".join(p.split(".")[:-1])
                paths[p] = {
                    'source': file,
                    'properties': {}
                }

                if parent in paths:
                    step =  p.replace(parent+".", "")
                    paths[parent]['properties'][step] = edge = {}
                    if len(valueType) and valueType[0] == valueType[0].lower(): edge['primitiveType'] = valueType
                    elif valueType != "":  edge['type'] = valueType
                    else:  edge['type'] = p
                    edge['min'] = min
                    edge['max'] = max

    for f in FILES: process(f)
    oldpaths = paths
    paths = {}
    for k,v in oldpaths.iteritems():
        if 'properties' in v and len(v['properties'].keys()) >  0: paths[k]=v
        ### if 'constraints' in v and len(v['constraints'].keys()) >  0: paths[k]=v
    return paths

t = tree(glob.glob(FHIR_DIR + "/*.profile.json"))
print json.dumps(t, sort_keys=True,indent=2)
