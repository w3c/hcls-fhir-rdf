from xml.etree import ElementTree
from xml.dom.minidom import parseString
import glob, json, re
from huTools.structured import dict2xml, dict2et

FHIR_DIR = "/home/jmandel/smart/fhir"

def tree(FILES):
    paths = {}
    def process(file):
        f = json.load(open(file))
        for v in f['Profile']['structure'][0]['element']:
            #split a given property into multiple strands if it has multiple types like value[X] (dateTime|String)
            praw = v['path']['value']
            count = 0
            if 'type' in v['definition']: types = v['definition']['type']
            else: types = [None]
            for possibleValue in types:
                count += 1
                v = possibleValue['code']['value']  if possibleValue else None
                p = praw.replace("[x]", v or "" )
                if v: 
                    v =  re.sub("\(.*\)", "", v).replace("@", "").replace("*", "")
                if len(p.split(".")) == 1: v = p
                parent = ".".join(p.split(".")[:-1])
                predicate =  p.replace(".", ":", 1).replace(".","_")
                paths[p] = {
                    'fhir_path': p,
                    'type': v,
                    'subs': []
                }
                if parent in paths:
                    paths[parent]['subs'].append({
                        'predicate': predicate,
                        'fhir_path': p,
                        'relative_xpath': "/".join(['f:'+x for x in p.replace(paths[parent]['fhir_path']+".", "").split(".")]),
                        'type': v
                        })
    for f in FILES: process(f)
    return {'fhirdefs': paths.values()}

t = tree(glob.glob(FHIR_DIR + "/build/publish/*.profile.json"))
#print json.dumps(t, sort_keys=True,indent=2)
v = ElementTree.tostring(dict2et(t, None, listnames = {'fhirdefs': 'path', 'subs': 'sub'}))
import pprint
#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(t)
dom = parseString(v)
print("\n".join(dom.toprettyxml().split("\n")[1:])).replace("fhirdefs", "l:fhirdefs")
