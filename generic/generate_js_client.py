from xml.etree import ElementTree
from xml.dom.minidom import parseString
import glob, json, re, sys
from huTools.structured import dict2xml, dict2et

FHIR_DIR = "site"

def tree(FILES):
    paths = {}
    def process(file):

        if file.find('-') != -1: return # strip out specialised profiles
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
            if 'name' in v:
                name = v['name']
                if name not in paths:
                    paths[name] = {
                        'sources': [file],
                        'constraints': {}
                    }
                elif "constraints" not in paths[name]:
                    paths[name]['constraints'] = {}
                    paths[name]['sources'].append(file)
                else:
                    print >> sys.stderr, file, " ", name, " restricts ", v['path']
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
                if p not in paths:
                    paths[p] = {
                        'sources': [file],
                        'properties': {}
                    }
                elif "properties" not in paths[p]:
                    paths[p]['properties'] = {}
                    paths[p]['sources'].append(file)
                elif file not in paths[p]['sources'] and f['type'] != "constraint":
                    print >> sys.stderr, file, " ", p, " already in paths from ", paths[p]['sources']

                if parent in paths:
                    step =  p.replace(parent+".", "")
                    if f['type'] == "constraint":
                        try:
                            if (parent not in paths[name]['constraints']):
                                paths[name]['constraints'][parent] = {}
                            paths[name]['constraints'][parent][step] = edge = {}
                        except NameError:
                            edge = {} # throw it away
                        except:
                            print >> sys.stderr, "Error in "+file+" \""+name+"\" not in paths:"
                            raise
                    else:
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
        if 'constraints' in v and len(v['constraints'].keys()) >  0: paths[k]=v
    return paths

t = tree(glob.glob(FHIR_DIR + "/*.profile.json"))
print json.dumps(t, sort_keys=True,indent=2)
