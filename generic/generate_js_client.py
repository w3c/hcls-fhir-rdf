from xml.etree import ElementTree
from xml.dom.minidom import parseString
import glob, json, re
from huTools.structured import dict2xml, dict2et

FHIR_DIR = "/home/jmandel/smart/fhir"

jsonParsers = {
    'decimal': 'float',
    'integer': 'integer',
    'dateTime': 'date',
    'instant': 'date',
    'string': 'string',
    'id': 'string',
    'uri': 'string',
    'idref': 'string',
    'oid': 'string',
    'base64Binary': 'string',
    'xhtml': 'string',
    'boolean': 'boolean',
    'code': 'string'
}
def tree(FILES):
    paths = {}
    def process(file):
        f = json.load(open(file))
        for v in f['structure'][0]['element']:

            #split a given property into multiple strands when it's like:
            # value[X] (dateTime|String)
            propertyName = v['path']

            if 'type' in v['definition']: types = v['definition']['type']
            else: types = [None]

            for possibleValue in types:
                valueType = possibleValue['code']  if possibleValue else ""
                valueType = valueType.replace("*", "").replace("@", "")
                if (valueType.startswith("Resource(")): valueType = "ResourceReference"
                p = propertyName.replace("[x]", valueType)
                parent = ".".join(p.split(".")[:-1])
                paths[p] = {
                    'edges': {}
                }

                if parent in paths:
                    step =  p.replace(parent+".", "")
                    paths[parent]['edges'][step] = edge = {}
                    if valueType in jsonParsers:  edge['parser'] = jsonParsers[valueType]
                    elif valueType != "":  edge['next'] = valueType
                    else:  edge['next'] = p

    for f in FILES: process(f)
    oldpaths = paths
    paths = {}
    for k,v in oldpaths.iteritems():
        if len(v['edges'].keys()) >  0: paths[k]=v
    return paths

t = tree(glob.glob(FHIR_DIR + "/build/publish/*.profile.json"))
print json.dumps(t, sort_keys=True,indent=2)
