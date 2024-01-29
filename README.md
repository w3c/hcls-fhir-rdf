# hcls-fhir-rdf
This repo is maintained by the [RDF subgroup of the HL7 ITS group](https://confluence.hl7.org/pages/viewpage.action?pageId=66922543), and is mostly used for tracking FHIR RDF [issues](https://github.com/w3c/hcls-fhir-rdf/issues).

## State of affairs
The ShEx and RDF generation functions have been implemented directly within the [FHIR publishing process on github](https://github.com/HL7/fhir)   

HAPI is now used for parsing and generating FHIR RDF in the FHIR publication process.  See [RDFParser](https://github.com/hapifhir/hapi-fhir/blob/master/hapi-fhir-base/src/main/java/ca/uhn/fhir/parser/RDFParser.java)

Code for the ShEx generation can be found in [ShExGenerator.java](https://github.com/hapifhir/org.hl7.fhir.core/blob/master/org.hl7.fhir.r5/src/main/java/org/hl7/fhir/r5/conformance/ShExGenerator.java)

<span color="red">**The RDF and ShEx generation code in this repository is no longer maintained.**</span>

---------

## Directories
* <del>data - the current stable FHIR specification</del>
  * examples -- XML examples from specification
  * site -- FHIR definitions (we use the json format)
  * rdf -- RDF representation of examples
  * definitions.shex -- shex definitions of FHIR content
  * definitions.xml -- XML definitions used in xslt transformation
  * extract.log -- log of build for the data directory
* <del>hcls_fhir_rdf -- python 3 modules for building data directory</del>
* ontology -- (underway) work on modeling FHIR definitions in OWL
* <del>tests -- python unit tests (not a lot at the moment)</del>
* <del>xsl -- XSLT 2.0 transform for converting FHIR instances from XML to RDF</del>

