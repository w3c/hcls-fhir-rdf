# hcls-fhir-rdf
Sketching out an RDF representation for FHIR

## Installation
This revised package is just being installed. Expect serious instability for a week or so...

Currently requires python 3 -- may be adjusted later on.  Most systems already have python 3 on them, which
is invoked via the command "python3".  Note that the scripts below assume that 'python' direcly invokes 'python3'.

### If python 3 is the default python on your system:

```bash
git clone https://github.com/w3c/hcls-fhir-rdf.git
cd hcls-fhir-rdf
python setup.py install
download_fhir_spec
generate_xml_definitions
generate_shex
```

### If python defaults to an earlier version:
```bash
git clone https://github.com/w3c/hcls-fhir-rdf.git
cd hcls-fhir-rdf
python3 setup.py install
python3 scripts/download_fhir_spec
python3 scripts/generate_xml_definitions > data/definitions.xml
python3 scripts/generate_shex > data/definitions.shex
```

## Notes

The above scripts don't actually generate the example turtle file.  We'll get that in in the next day or so... in the mean time the example below shows how one might generate bits of RDF:

```bash
xsltproc -stringparam fhirdefs data/definitions.xml xsl/transform.xsl ../data/examples/site/allergyintolerance-example.xml > examples/allergyintolerance-example.ttl
```