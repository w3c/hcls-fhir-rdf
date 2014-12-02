site:
	wget http://hl7.org/documentcenter/public/standards/FHIR/fhir-spec.zip
	unzip -q fhir-spec.zip

xslt_defs.xml: generate_xslt_defs.py site
	python generate_xslt_defs.py > xslt_defs.xml

transform.xsl: head.xml tail.xml xslt_defs.xml
	cat head.xml xslt_defs.xml tail.xml  > transform.xsl

order-generated.ttl: transform.xsl ../order.xml
	xsltproc transform.xsl ../order.xml

test: transform.xsl
	(cd tests && make test)

jsdefs: generate_js_client.py site
	python generate_js_client.py > definitions.json

shex: jsdefs 
	python genshex.py > fhir-shapes.shex
