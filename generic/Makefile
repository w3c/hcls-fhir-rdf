xslt_defs.xml: generate_xslt_defs.py
	python generate_xslt_defs.py > xslt_defs.xml

transform.xsl: head.xml tail.xml xslt_defs.xml
	cat head.xml xslt_defs.xml tail.xml  > transform.xsl

order-generated.ttl: transform.xsl ../order.xml
	xsltproc transform.xsl ../order.xml

test: transform.xsl
	(cd tests && make test)

