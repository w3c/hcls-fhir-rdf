# hcls-fhir-rdf
Sketching out an RDF representation for FHIR 

## State of affairs
The ShEx and RDF generation functions have been implemented directly within the [FHIR publishing process](http://gforge.hl7.org/gf/project/fhir).   

Code for the RDF generator can be found in [TurtleParser.java](http://gforge.hl7.org/gf/project/fhir/scmsvn/?action=browse&path=%2Ftrunk%2Fbuild%2Ftools%2Fjava%2Forg.hl7.fhir.dstu3%2Fsrc%2Forg%2Fhl7%2Ffhir%2Fdstu3%2Felementmodel%2FTurtleParser.java&) and [RdfBaseParser.java](http://gforge.hl7.org/gf/project/fhir/scmsvn/?action=browse&path=%2Ftrunk%2Fbuild%2Ftools%2Fjava%2Forg.hl7.fhir.dstu3%2Fsrc%2Forg%2Fhl7%2Ffhir%2Fdstu3%2Fformats%2FRdfParserBase.java)

Code for the ShEx generation can be found in [ShExGenerator.java](http://gforge.hl7.org/gf/project/fhir/scmsvn/?action=browse&path=%2Ftrunk%2Fbuild%2Ftools%2Fjava%2Forg.hl7.fhir.dstu3%2Fsrc%2Forg%2Fhl7%2Ffhir%2Fdstu3%2Fconformance%2FShExGenerator.java)

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

