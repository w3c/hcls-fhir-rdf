# sample invocation if you don't want a timestamp:
# NOW='' LD_LIBRARY_PATH=/usr/local/instantclient_11_2/:~/checkouts/libbooost.inst/lib/:~/checkouts/SWObjects/boost-log-1.46/stage/lib PATH=$PATH:~/checkouts/SWObjects/bin/ make test -W fhir-xml-to-turtle.xslt

NOW ?= -stringparam now `date +%Y-%02m-%02dT%02H:%02M:%02S%:z`

fhir-xml-to-turtle-text.xslt: fhir-xml-to-turtle.xslt
	cp $< $@
	perl -pi -e "s{<xsl:param name=\"output\" select=\"'html'\"/>}{<xsl:param name=\"output\" select=\"'text'\"/>};s{xsl:output method=\"html\"}{xsl:output method=\"text\"}" $@

diagnostic-report-generated.ttl: fhir-xml-to-turtle-text.xslt diagnostic-report.xml
	xsltproc ${NOW} $^ > $@


t_diag: diagnostic-report-generated.ttl
	sparql -d $< -q

order-generated.ttl: fhir-xml-to-turtle-text.xslt order.xml
	xsltproc ${NOW} $^ > $@


t_order: order-generated.ttl
	sparql -d $< -q

test: t_diag t_order

