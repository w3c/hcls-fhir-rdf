# hcls-fhir-rdf
Sketching out an RDF representation for FHIR
This was forked from jmandel/fhir-rdf because ericP needed admin privs.
<pre>
  git clone https://github.com/w3c/hcls-fhir-rdf.git
  cd hcls-fhir-rdf/generic
  # unix users:
    make site
    make test # admire the diffs that you shouldn't see
  # windows users:
    # download http://hl7.org/documentcenter/public/standards/FHIR/fhir-spec.zip into fhir-spec.zip
    # unzip -q fhir-spec.zip
    # download [http://saxon.sourceforge.net/ saxon]
    # java net.sf.saxon.Transform -s:deviceobservation-referencesToContained.xml -xsl:../transform.xsl -o:deviceobservation-referencesToContained-generated.ttl
</pre>
