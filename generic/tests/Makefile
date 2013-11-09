# sample invocation if you don't want a timestamp:
# NOW='' LD_LIBRARY_PATH=/usr/local/instantclient_11_2/:~/checkouts/libbooost.inst/lib/:~/checkouts/SWObjects/boost-log-1.46/stage/lib PATH=$PATH:~/checkouts/SWObjects/bin/ make test -W fhir-xml-to-turtle.xslt

NOW		?= -stringparam now `date +%Y-%02m-%02dT%02H:%02M:%02S%:z`
TESTNAMELIST	?=  $(patsubst %.xml,t_%,$(wildcard *.xml))
XSLT		?=  xsltproc # iirc, Batik uses args in the other order

# generate a Turtle version of a given XML file
%-generated.ttl: ../transform.xsl %.xml
	${XSLT} ${NOW} $^ > $@

# test the integrity of a generated Turtle file.
t_%: %-generated.ttl %.ttl
# 	sparql -d $< -q
	diff $^

# test the Turtle output for all the .xml files.
test: ${TESTNAMELIST}
	@echo tested ${TESTNAMELIST}

