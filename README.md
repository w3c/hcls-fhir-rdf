# hcls-fhir-rdf
Sketching out an RDF representation for FHIR

## Installation
This revised package is just being installed. Expect serious instability for a week or so...

Currently requires python 3 -- may be adjusted later on

git clone https://github.com/w3c/hcls-fhir-rdf.git

pip install dirlistproc

pip install jsonasobj

cd scripts

python generate_fhir_definitions -h


## Sample use

mkdir data

python bin/generate_fhir_definitions -id data -o data/definitions.xml -of xml -ex examples

The above will download the FHIR DST2 2 definitions, installing them in the data/site directory, and will place
the examples in the examples directory.  It will then process the definitions creating a the definitions descriptor.

xsltproc -stringparam fhirdefs data/definitions.xml xsl/transform.xsl examples/site/allergyintolerance-example.xml > examples/allergyintolerance-example.ttl