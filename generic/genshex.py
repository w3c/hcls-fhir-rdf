import json, sys
skip = ["extension", "modifierExtension"]

def shexProperty(name, el, p):
    pName =  ':' + name + "\\#" + p.replace(".", "_")
    if el['min'] == '0':
        if el['max'] == '1': card = '?'
        elif el['max'] == '*': card = '*'
        else: card = '{0,'+el['max']+'}'
    elif el['min'] == '1' and el['max'] == '1':  card = ''
    else:
        if el['max'] == '*': card = '+'
        else: card = '{'+el['min']+','+el['max']+'}'
    if 'primitiveType' in el:
        return ",\n  %s LITERAL%s %%GenX{ %s/@value %%}"%(pName, card, p)
    elif el['type'].replace(".", "_") == 'ResourceReference':
        return ",\n  %s IRI%s %%GenX{ %s/@value %%}"%(pName, card, p)
    else:
        return ",\n  %s @<%s>%s  %%GenX{ %s = %%}"%(pName, el['type'].replace(".", "_"), card, p)

def minus(l1, l2):
    for el in l2:
        if (el in l1):
            l1.remove(el)
    return l1

defs = json.loads(open("definitions.json").read())
print ("PREFIX : <http://hl7/org/fhir/>\n"
       "%GenX{ DeviceObservation $http://hl7.org/fhir %}\n"
       "start=<DeviceObservationReport>\n")

t = (v
     for v
     in map(lambda i:
                [i[0], minus(i[1]["order"], skip), i[1]["properties"]]
            , defs.items())
     if (v[0]!="Profile.extensionDefn" and len(v[1])!=0))
for v in t: # was defs
    shapeName = v[0].replace(".", "_")
    print "<%s> {"%(shapeName)
    sys.stdout.write("  a (:%s\\#)"%(shapeName))
    pz = (p for p in v[1])
    print "".join([shexProperty(v[0], v[2][p], p) for p in pz])
    print "}\n"
