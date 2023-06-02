---
name: ShEx
about: Bug report for FHIR specification's ShEx schema
title: ''
labels: ShEx
assignees: ''

---

**ShEx shape**
Name of Shape Expression and predicate in ShapePath form, e.g. [`@<Observation.component>~fhir:value`](https://build.fhir.org/observation.shex.html)

**FHIR Resource**
URL of corresponding attribute on build.fhir.org, e.g. https://build.fhir.org/observation.html#a26.b

**Turtle filename**
Any FHIR Turtle example that exhibits this issue, e.g. [observation-example-bloodpressure.ttl](https://build.fhir.org/observation-example-bloodpressure.ttl.html)

**Description**
What the ShEx should be. Can express as diff à la:
``` diff
- a [fhir:unsingedInt]
+ a [fhir:unsignedInt]
```
