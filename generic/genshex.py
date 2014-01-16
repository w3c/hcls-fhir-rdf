import json
defs = json.loads(open("definitions.json").read())

def shexProperty(v, p):
    pName =  v + ":" + p.replace(".", "_")
    if 'primitiveType' in defs[v]['properties'][p]:
        return "%s LITERAL %%{GenX %s/@value %%}"%(pName, p)
    else:
        return "%s @<%s>  %%{GenX %s = %%}"%(pName, defs[v]['properties'][p]['type'], p)

for v in defs:
    shapeName = v.replace(".", "_")
    print "<%s> {"%(shapeName)
    print "a (:%s)?,"%(shapeName)
    print ",\n".join([shexProperty(v, p) for p in defs[v]['properties']])
    print "}\n"
