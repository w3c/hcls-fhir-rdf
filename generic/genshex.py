import sys, json
defs = json.loads(open("definitions.json").read())

def shexProperty(v, p, dfn):
    pName =  "fhir:" + v + "." + p#.replace(".", "_")
    min = dfn['min']
    max = dfn['max']
    if   min == 1 and max == "1":   card = ""
    elif min == 0 and max == "1":   card = "?"
    elif min == 0 and max == "*":   card = "*"
    elif min == 1 and max == "*": card = "+"
    elif max == "*":              card = "{%s,}"%(min)
    else:                         card = "{%s,%s}"%(min, max)
    if 'primitiveType' in dfn:
        # return "  %s LITERAL %%{GenX %s/@value %%}%s"%(pName, p, card)
        return "  %s @<LitShape>%s %%GenX{ %s = %%}"%(pName, card, p)
    elif dfn['type'] == "Extension.value":
        # from http://hl7-fhir.github.io/extensibility.html#json-inner
        return """  (   fhir:valueInteger xsd:integer,
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
    else:
        return "  %s @<%s>%s  %%GenX{ %s = %%}"%(pName, dfn['type']+"Shape", card, p)

print "PREFIX fhir: <http://hl7/org/fhir/>"
print "PREFIX xhtml: <http://www.w3.org/1999/xhtml>"
print "PREFIX xsd: <http://www.w3.org/2001/XMLSchema>"
print ""

for shapeName in defs:
    print "<%s> {"%(shapeName+"Shape")
    print "  a (fhir:%s)?,"%(shapeName)
    # print >> sys.stderr, shapeName
    if "properties" in defs[shapeName]:
        print ",\n".join([
            shexProperty(shapeName, p, defs[shapeName]['properties'][p])
            for p in defs[shapeName]['properties']
        ])
    if "constraints" in defs[shapeName]:
        print ",\n".join([
            shexProperty(f, p, defs[shapeName]['constraints'][f][p])
            for f in defs[shapeName]['constraints']
            for p in defs[shapeName]['constraints'][f]
        ])
    print "}\n"

print """<LitShape> {
  fhir:value LITERAL %GenX{ @value %},
  fhir:id LITERAL? %GenX{ @id %}
}"""
