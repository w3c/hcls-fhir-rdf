fhir-xml-to-turtle-text.xsl: fhir-xml-to-turtle.xslt
	cp fhir-xml-to-turtle.xslt fhir-xml-to-turtle-text.xsl
	perl -pi -e "s{<xsl:param name=\"output\" select=\"'html'\"/>}{<xsl:param name=\"output\" select=\"'text'\"/>};s{xsl:output method=\"html\"}{xsl:output method=\"text\"}" fhir-xml-to-turtle-text.xsl

diagnostic-report-generated.ttl: fhir-xml-to-turtle-text.xsl diagnostic-report.xml
	xsltproc -stringparam now `date +%Y-%02m-%02dT%02H:%02M:%02S%:z` fhir-xml-to-turtle-text.xsl diagnostic-report.xml > diagnostic-report-generated.ttl


# e.g. LD_LIBRARY_PATH=/usr/local/instantclient_11_2/:/home/eric/checkouts/libbooost.inst/lib/:/home/eric/checkouts/SWObjects/boost-log-1.46/stage/lib PATH=$PATH:/home/eric/checkouts/SWObjects/bin/ make test
test: diagnostic-report-generated.ttl
	sparql -d diagnostic-report-generated.ttl

