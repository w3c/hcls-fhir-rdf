---
name: Turtle
about: Bug report for FHIR specification's Turtle examples
title: ''
labels: Turtle
assignees: ''

---

**Turtle filename**
Any FHIR Turtle example that exhibits this issue, e.g. [observation-example-bloodpressure.ttl](https://build.fhir.org/observation-example-bloodpressure.ttl.html)

**FHIR Resource**
URL of corresponding attribute on build.fhir.org, e.g. https://build.fhir.org/observation.html#a26.b

**ShEx shape**
Name of corresponding Shape Expression and predicate in ShapePath form, e.g. [`@<Observation.component>~fhir:value`](https://build.fhir.org/observation.shex.html)

**Description**
What the Turtle should be. Can express as diff à la:
``` diff
- fhir:value [ a fhir:unsingedInt
+ fhir:value [ a fhir:unsignedInt
```
