# Scripts to hide RDF lists / RDF Collections in FHIR from OWL

## Background
FHIR RDF R5 uses RDF lists (a/k/a RDF Collections) to capture the order of items, when multiple items can be specified.  For example, a patient can have multiple phone numbers, and the order of those numbers may be significant: the first one may be the preferred number, for example.  To retain order, these lists use the standard rdf:first, rdf:rest and rdf:nil vocabulary.   However, OWL uses RDF lists for its own expressive purposes and prohibits the use of vocabulary in the RDF namespace for non-OWL purposes.  This means that some OWL processors may not properly process FHIR RDF R5 data that contains RDF lists for non-OWL purposes.  

## Workaround
To work around this problem and allow OWL reasoners to properly process your data, one solution is to change FHIR RDF's use of the rdf:first, rdf:rest and rdf:nil URIs to use alternate URIs, as follows:
* rdf:first --> fhir:rdfFirst (an owl:ObjectProperty), if its object is an owl:Object, i.e., not a literal
* rdf:first --> fhir:rdfFirstLiteral (an owl:DatatypeProperty), if its object is a literal
* rdf:rest --> fhir:rdfRest (an owl:ObjectProperty)
* rdf:nil --> fhir:rdfNil

The scripts below perform such conversions, and are provided as a convenience.  Other workaround strategies are possible.  Additional contributions are welcomed if you have another means of working around this problem.

## Scripts
* SPARQL
  * [convert-data-lists-to-fhir-namespace-fhir-only.ru](https://github.com/w3c/hcls-fhir-rdf/blob/gh-pages/scripts/owl-safe-lists/convert-data-lists-to-fhir-namespace-fhir-only.ru) -- This version only transforms lists that are objects of predicates that are in the fhir: namespace.  Other lists are not touched, even if they are not OWL lists.
  * [owl-safe-lists/convert-data-lists-to-fhir-namespace.ru](https://github.com/w3c/hcls-fhir-rdf/blob/gh-pages/scripts/owl-safe-lists/convert-data-lists-to-fhir-namespace.ru) -- This version transforms all non-OWL lists, regardless of whether they are FHIR lists. 
* python - TODO -- Contributions would be welcomed!
* javascript - TODO -- Contributions would be welcomed!
* java - TODO -- Contributions would be welcomed!
