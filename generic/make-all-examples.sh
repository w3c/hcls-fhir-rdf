cp -r ~/smart/fhir/build/publish/*-example*.xml .
for i in *.xml; do  xsltproc ../generic/transform.xsl xds-example.xml >  xds-example.ttl; done
