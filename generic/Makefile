transform.xsl: head.xml tail.xml xml_defs.xml
	cat head.xml xslt_defs.xml tail.xml  > transform.xsl

xml_defs.xml: generate_xslt_defs.py
	python generate_xslt_defs.py > xslt_defs.xml

order-generated.ttl: transform.xsl ../order.xml
	xsltproc transform.xsl ../order.xml
