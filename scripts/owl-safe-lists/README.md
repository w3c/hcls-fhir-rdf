# Scripts to hide RDF Collections in FHIR from OWL

## Background: the problem
FHIR RDF R5 uses RDF lists (a/k/a RDF Collections) to capture the order of items, when multiple items can be specified.  For example, a patient can have multiple phone numbers.  These lists use the standard rdf:first, rdf:rest and rdf:nil vocabulary.   OWL uses RDF lists for its own expressive purposes and prohibits the use of vocabulary in the RDF namespace for non-OWL purposes.  This means that OWL processors may reject or fail to properly utilize FHIR RDF R5 data that contains RDF lists.  

## Workaround
To work around this problem and allow OWL reasoners to properly process your data, the rdf:first, rdf:rest and rdf:nil URIs can be changed to alternate URIs:
* rdf:first --> fhir:rdfFirst (an owl:ObjectProperty), if its object is an owl:Object, i.e., not a literal
* rdf:first --> fhir:rdfFirstLiteral (an owl:DatatypeProperty), if its object is a literal
* rdf:rest --> fhir:rdfRest (an owl:ObjectProperty)
* rdf:nil --> fhir:rdfNil

The scripts below perform such conversions.

## Scripts
* SPARQL
  * [convert-data-lists-to-fhir-namespace-fhir-only.ru](https://github.com/w3c/hcls-fhir-rdf/blob/gh-pages/scripts/owl-safe-lists/convert-data-lists-to-fhir-namespace-fhir-only.ru) -- This version only transforms lists that are objects of predicates that are in the fhir: namespace.  Other lists are not touched, even if they are not OWL lists.
  * [owl-safe-lists/convert-data-lists-to-fhir-namespace.ru](https://github.com/w3c/hcls-fhir-rdf/blob/gh-pages/scripts/owl-safe-lists/convert-data-lists-to-fhir-namespace.ru) -- This version transforms all non-OWL lists, regardless of whether they are FHIR lists. 
* python - TODO
* javascript - TODO
* java - TODO
