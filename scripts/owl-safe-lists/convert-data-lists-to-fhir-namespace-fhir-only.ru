# This SPARQL Update can be used to transform RDF lists created by the FHIR data model
# into structures using the FHIR namespace. This allows compatibility with OWL, which
# reserves RDF lists for use in internal OWL constructs.
# Only lists that are the objects of predicates in the fhir: namespace are transformed.
# It can be applied to data in a triplestore, or via command line using the Jena `update` tool:
# `update --data=my-fhir-data.ttl --update=convert-data-lists-to-fhir-namespace.ru --dump >my-fhir-data-converted.ttl`

PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX fhir: <http://hl7.org/fhir/>

INSERT DATA {
  fhir:rdfFirst rdf:type owl:ObjectProperty .
  fhir:rdfFirstLiteral rdf:type owl:DatatypeProperty .
  fhir:rdfRest rdf:type owl:ObjectProperty .
  fhir:rdfNil rdf:type owl:NamedIndividual .
}
;
DELETE {
  ?list rdf:first ?item .
  ?list rdf:rest ?rest .
}
INSERT {
  ?list ?first_pred ?item .
  ?list fhir:rdfRest ?rest_obj .
}
WHERE {
  BIND(STR(fhir:) AS ?namespace)
  ?node ?p ?top_list .
  FILTER(STRSTARTS(STR(?p), ?namespace))
  ?top_list rdf:rest* ?list .
  ?list rdf:first ?item .
  ?list rdf:rest ?rest .
  BIND(IF(isLiteral(?item), fhir:rdfFirstLiteral, fhir:rdfFirst) AS ?first_pred)
  BIND(IF(?rest = rdf:nil, fhir:rdfNil, ?rest) AS ?rest_obj)
}
