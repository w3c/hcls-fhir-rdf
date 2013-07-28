<?xml version="1.0" encoding="UTF-8"?>
<!--
xsltproc - -stringparam now `date +%Y-%02m-%02dT%02H:%02M:%02S%:z` CDA_NG.xsl IJ.xml > IJ.ttl && sparql -d IJ.ttl

cp fhir-xml-to-turtle.xslt fhir-xml-to-turtle-text.xsl && perl -pi -e "s{<xsl:param name=\"output\" select=\"'html'\"/>}{<xsl:param name=\"output\" select=\"'text'\"/>};s{xsl:output method=\"html\"}{xsl:output method=\"text\"}" fhir-xml-to-turtle-text.xsl && xsltproc -stringparam now `date +%Y-%02m-%02dT%02H:%02M:%02S%:z` fhir-xml-to-turtle-text.xsl diagnostic-report.xml > diagnostic-report.ttl && LD_LIBRARY_PATH=/usr/local/instantclient_11_2/:/home/eric/checkouts/libbooost.inst/lib/:/home/eric/checkouts/SWObjects/boost-log-1.46/stage/lib /home/eric/checkouts/SWObjects/bin/sparql -d diagnostic-report.ttl

-->
<!-- LICENSE INFORMATION
Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at  http://www.apache.org/licenses/LICENSE-2.0 
-->
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns:n1="http://hl7.org/fhir"
		xmlns:xhtml="http://www.w3.org/1999/xhtml"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <!-- xsl:output method="xml" indent="yes" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" doctype-public="-//W3C//DTD XHTML 1.0 Transitional//EN" / -->
  <xsl:param name="now" select="''"/>
  <xsl:param name="output" select="'html'"/>
  <xsl:param name="newline">
    <xsl:choose>
      <xsl:when test="$output='text'"><xsl:value-of select="'&#x0a;'"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="'&#x0d;&#x0a;'"/></xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:output method="html" indent="yes" version="4.01" encoding="UTF-8" doctype-system="http://www.w3.org/TR/html4/strict.dtd" doctype-public="-//W3C//DTD HTML 4.01//EN"/>
  <!-- global variable title -->
  <xsl:variable name="title">
    <xsl:choose>
      <xsl:when test="string-length(/n1:ClinicalDocument/n1:title)  &gt;= 1">
	<xsl:value-of select="/n1:ClinicalDocument/n1:title"/>
      </xsl:when>
      <xsl:when test="/n1:ClinicalDocument/n1:code/@displayName">
	<xsl:value-of select="/n1:ClinicalDocument/n1:code/@displayName"/>
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>Clinical Document</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <!-- Main -->
  <xsl:template match="/">
    <xsl:apply-templates select="*"/>
  </xsl:template>
  <!-- produce browser rendered, human readable clinical document -->
  <xsl:template match="*">
    <xsl:choose>
      <xsl:when test="$output!='text'">
	<html>
	  <head>
	    <xsl:comment> Do NOT edit this HTML directly: it was generated via an XSLT transformation from a CDA Release 2 XML document. </xsl:comment>
	    <title>
	      <xsl:value-of select="$title"/>
	    </title>
	    <xsl:call-template name="addCSS"/>
	  </head>
	  <body>
	    <h1 class="h1center">
	      <xsl:value-of select="$title"/>
	    </h1>
	    <xsl:call-template name="body"/>
	    <br/>
	    <br/>
	  </body>
	</html>
      </xsl:when>
      <xsl:otherwise>
	<xsl:call-template name="body"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="body">
    <xsl:call-template name="addPrefixes"/>
    <xsl:call-template name="Resource"/>
  </xsl:template>

  <xsl:template name="Resource">
    <div>
      <xsl:apply-templates select="." mode="start" />
      <pre class="machine" style="font-size:small">
[] a fhir:<xsl:value-of select="name()"/>;</pre>
    <xsl:for-each select="n1:text">
      <xsl:apply-templates select="." mode="quote" />
      <xsl:call-template name="Text"/>
    </xsl:for-each>
    <xsl:if test="n1:status/@value">
      <xsl:apply-templates select="n1:status" mode="quote" />
      <pre class="machine" style="font-size:small">    :status [a fhir:Code; fhir:value "<xsl:value-of select="n1:status/@value"/>"];
</pre>
    </xsl:if>
    <xsl:apply-templates select="n1:issued" mode="quote" />
    <xsl:apply-templates select="n1:issued" mode="Date">
      <xsl:with-param name="predicate" select="'issued'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:date" mode="quote" />
    <xsl:apply-templates select="n1:date" mode="Date">
      <xsl:with-param name="predicate" select="'date'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:subject" mode="quote" />
    <xsl:apply-templates select="n1:subject" mode="Reference">
      <xsl:with-param name="predicate" select="'subject'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:source" mode="quote" />
    <xsl:apply-templates select="n1:source" mode="Reference">
      <xsl:with-param name="predicate" select="'source'"/>
    </xsl:apply-templates>
    <xsl:if test="n1:reason/@value">
      <xsl:apply-templates select="n1:reason" mode="quote" />
      <pre class="machine" style="font-size:small">    :reason [a fhir:String; fhir:value "<xsl:value-of select="n1:reason/@value"/>"];
</pre></xsl:if>
    <xsl:apply-templates select="n1:performer" mode="quote" />
    <xsl:apply-templates select="n1:performer" mode="Reference">
      <xsl:with-param name="predicate" select="'performer'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:reportId" mode="quote" />
    <xsl:apply-templates select="n1:reportId" mode="Identifier">
      <xsl:with-param name="predicate" select="'reportId'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:serviceCategory" mode="quote" />
    <xsl:apply-templates select="n1:serviceCategory" mode="Codable">
      <xsl:with-param name="predicate" select="'serviceCategory'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:diagnosticTime" mode="quote" />
    <xsl:apply-templates select="n1:diagnosticTime" mode="Date">
      <xsl:with-param name="predicate" select="'diagnosticTime'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:results" mode="Results">
      <xsl:with-param name="predicate" select="'results'"/>
    </xsl:apply-templates>
    <xsl:for-each select="n1:when">
      <xsl:apply-templates select="." mode="start" />
      <pre class="machine" style="font-size:small">    :when [
</pre>
<xsl:apply-templates select="n1:code" mode="quote" />
      <xsl:apply-templates select="n1:code" mode="Codable">
	<xsl:with-param name="predicate" select="'when_code'"/>
	<xsl:with-param name="padding" select="'        '"/>
      </xsl:apply-templates>
      <xsl:apply-templates select="." mode="end" />
      <pre class="machine" style="font-size:small">
    ] ;<xsl:text>
</xsl:text>
    </pre>
    </xsl:for-each>
    <xsl:apply-templates select="n1:detail" mode="quote" />
    <xsl:apply-templates select="n1:detail" mode="Reference">
      <xsl:with-param name="predicate" select="'detail'"/>
    </xsl:apply-templates>
<pre>.</pre>
    <xsl:apply-templates select="n1:contained/*" mode="Contained"/>
    <xsl:apply-templates select="." mode="end" />
    </div>
  </xsl:template>

  <!-- get rid of whitespace in Contained element -->
  <xsl:template name="Contained-text" match="text()" mode="Contained"/>

  <xsl:template name="Contained" match="*" mode="Contained">
    <xsl:param name="type" select="name()"/>
    <xsl:apply-templates select="." mode="start" />
    <pre class="machine" style="font-size:small">
&lt;<xsl:value-of select="@id"/>&gt; a fhir:<xsl:value-of select="$type"/>;</pre>
    <xsl:for-each select="n1:text">
    <xsl:apply-templates select="." mode="quote" />
    <xsl:call-template name="Text"/></xsl:for-each>
    <xsl:apply-templates select="n1:name" mode="quote" />
    <pre class="machine" style="font-size:small">    <xsl:value-of select="concat('    ', $type, ':name')"/>
    <xsl:for-each select="n1:name"><xsl:apply-templates select="n1:coding" mode="Coding-wrapper"/>
      <xsl:if test="following-sibling::n1:name">,</xsl:if>
      </xsl:for-each><xsl:text>;
</xsl:text>
    </pre>
    <xsl:apply-templates select="n1:valueQuantity" mode="quote" />
    <xsl:apply-templates select="n1:valueQuantity" mode="value">
      <xsl:with-param name="predicate" select="'results'"/>
      <xsl:with-param name="type" select="$type"/>
    </xsl:apply-templates>
    <xsl:if test="n1:status/@value">
      <xsl:apply-templates select="n1:status" mode="quote" />
      <pre class="machine" style="font-size:small">
      <xsl:value-of select="'    '"/><xsl:value-of select="$type"/>:status [a fhir:Code; fhir:value "<xsl:value-of select="n1:status/@value"/>"];
</pre>
    </xsl:if>
    <xsl:if test="n1:reliability/@value">
      <xsl:apply-templates select="n1:reliability" mode="quote" />
      <pre class="machine" style="font-size:small">
      <xsl:value-of select="'    '"/><xsl:value-of select="$type"/>:reliability [a fhir:Code; fhir:value "<xsl:value-of select="n1:reliability/@value"/>"];
</pre>
    </xsl:if>
    <xsl:for-each select="n1:referenceRange">
      <xsl:apply-templates select="." mode="start" />
      <pre class="machine" style="font-size:small">      <xsl:value-of select="'    '"/><xsl:value-of select="$type"/>:referenceRange [
</pre>
      <xsl:for-each select="n1:rangeRange">
	<xsl:apply-templates select="." mode="start" />
	<pre class="machine" style="font-size:small">
	  <xsl:value-of select="'        '"/><xsl:value-of select="$type"/>:referenceRange_rangeRange [
            a fhir:Range;
</pre>
	<xsl:apply-templates select="n1:low" mode="quote" />
	<xsl:apply-templates select="n1:low" mode="value">
	  <xsl:with-param name="padding" select="'            '"/>
	  <xsl:with-param name="predicate" select="'results'"/>
	  <xsl:with-param name="type" select="'Range'"/>
	</xsl:apply-templates>
	<xsl:apply-templates select="n1:high" mode="quote" />
	<xsl:apply-templates select="n1:high" mode="value">
	  <xsl:with-param name="padding" select="'            '"/>
	  <xsl:with-param name="predicate" select="'results'"/>
	  <xsl:with-param name="type" select="'Range'"/>
	</xsl:apply-templates>
	<pre class="machine" style="font-size:small">        ];</pre>
	<xsl:apply-templates select="." mode="end" />
	</xsl:for-each>
	<pre class="machine" style="font-size:small">
    ];
</pre>
	<xsl:apply-templates select="." mode="end" />
    </xsl:for-each>
.
<xsl:apply-templates select="." mode="end" />
  </xsl:template>

  <xsl:template name="value" match="*" mode="value">
    <xsl:param name="padding" select="'    '"/>
    <xsl:param name="type" select="'@@type'"/>
    <pre class="machine" style="font-size:small">
      <xsl:value-of select="$padding"/>
      <xsl:value-of select="$type"/>:<xsl:value-of select="name()"/> [
<xsl:value-of select="$padding"/>    a fhir:Quantity;<xsl:if test="n1:value/@value">;
<xsl:value-of select="$padding"/>    Quantity:value [a fhir:Decimal; fhir:value "<xsl:value-of select="n1:value/@value"/>"^^xsd:decimal]</xsl:if><xsl:if test="n1:units/@value">;
<xsl:value-of select="$padding"/>    Quantity:units [a fhir:String; fhir:value "<xsl:value-of select="n1:units/@value"/>"]</xsl:if><xsl:if test="n1:system/@value">;
<xsl:value-of select="$padding"/>    Quantity:system [a fhir:Uri; fhir:value &lt;<xsl:value-of select="n1:system/@value"/>&gt;]</xsl:if><xsl:if test="n1:code/@value">;
<xsl:value-of select="$padding"/>    Quantity:code [a fhir:Code; fhir:value "<xsl:value-of select="n1:code/@value"/>"]</xsl:if><xsl:text>
</xsl:text><xsl:value-of select="$padding"/>];
</pre>
  </xsl:template>

  <xsl:template name="Results" match="*" mode="Results">
    <xsl:param name="predicate"/>
    <div>
      <xsl:apply-templates select="." mode="start" />
      <pre class="machine" style="font-size:small">    :<xsl:value-of select="$predicate"/> [
</pre>
    <div>
    <xsl:apply-templates select="n1:name" mode="quote" />
    <xsl:apply-templates select="n1:name" mode="Codable">
      <xsl:with-param name="predicate" select="'results_name'"/>
      <xsl:with-param name="padding" select="'        '"/>
    </xsl:apply-templates>
    </div>
    <div>
      <xsl:apply-templates select="n1:result" mode="quote" />
      <xsl:apply-templates select="n1:result" mode="Reference">
	<xsl:with-param name="predicate" select="'results_result'"/>
	<xsl:with-param name="padding" select="'        '"/>
	</xsl:apply-templates>
    </div>
    <pre class="machine" style="font-size:small">
    ];
</pre>
    <xsl:apply-templates select="." mode="end" />
    </div>
  </xsl:template>

  <xsl:template name="Date" match="*" mode="Date">
    <xsl:param name="predicate"/>
    <pre class="machine" style="font-size:small">    :<xsl:value-of select="$predicate"/> [a fhir:DateTime; fhir:value "<xsl:value-of select="@value"/>"^^xsd:dateTime];
</pre>
  </xsl:template>

  <xsl:template name="Reference" match="*" mode="Reference">
    <xsl:param name="predicate"/>
    <xsl:param name="padding" select="'    '"/>
    <pre class="machine" style="font-size:small">
      <xsl:value-of select="$padding"/>:<xsl:value-of select="$predicate"/> [
<xsl:value-of select="$padding"/>    a fhir:Reference; a fhir:<xsl:value-of select="n1:type/@value"/>Reference;
<xsl:value-of select="$padding"/>    Reference:reference &lt;<xsl:value-of select="n1:reference/@value"/>&gt;<xsl:if test="n1:display/@value">;
<xsl:value-of select="$padding"/>    Reference:display [a fhir:String; fhir:value "<xsl:value-of select="n1:display/@value"/>"]</xsl:if>
<xsl:text>
</xsl:text>
<xsl:value-of select="$padding"/>];<xsl:text>
</xsl:text>
    </pre>
  </xsl:template>

  <xsl:template name="Identifier" match="*" mode="Identifier">
    <xsl:param name="predicate"/>
    <pre class="machine" style="font-size:small">    :<xsl:value-of select="$predicate"/> [
        a fhir:Identifier;<xsl:if test="n1:system/@value">;
        :system [a fhir:Uri; fhir:value &lt;<xsl:value-of select="n1:system/@value"/>&gt;]</xsl:if><xsl:if test="n1:coding/@value">;
        :coding [a fhir:String; fhir:value "<xsl:value-of select="n1:coding/@value"/>"]</xsl:if><xsl:if test="n1:code/@value">;
        :code [a fhir:String; fhir:value "<xsl:value-of select="n1:code/@value"/>"]</xsl:if><xsl:if test="n1:key/@value">;
        :key [a fhir:String; fhir:value "<xsl:value-of select="n1:key/@value"/>"]</xsl:if><xsl:if test="n1:display/@value">;
        :display [a fhir:String; fhir:value "<xsl:value-of select="n1:display/@value"/>"]</xsl:if>
    ];
</pre>
  </xsl:template>

  <xsl:template name="Codable" match="*" mode="Codable">
    <xsl:param name="predicate"/>
    <xsl:param name="padding" select="'    '"/>
    <pre class="machine" style="font-size:small">
      <xsl:value-of select="$padding"/>:<xsl:value-of select="$predicate"/> [
<xsl:value-of select="$padding"/>    a fhir:Codable;
<xsl:value-of select="$padding"/>    Codeable:coding<xsl:apply-templates select="n1:coding" mode="Coding-wrapper" >
<xsl:with-param name="padding" select="concat($padding, '    ')"/></xsl:apply-templates>
<xsl:text>
</xsl:text><xsl:value-of select="$padding"/>];
</pre>
  </xsl:template>

<xsl:template name="Coding-wrapper" match="n1:coding" mode="Coding-wrapper">
  <xsl:param name="padding" select="'    '"/><xsl:apply-templates select="." mode="Coding">
        <xsl:with-param name="padding" select="$padding"/>
      </xsl:apply-templates>
      <xsl:if test="following-sibling::n1:coding">,</xsl:if>
</xsl:template>

  <xsl:template name="Coding" match="*" mode="Coding">
    <xsl:param name="padding" select="'        '"/> [
<xsl:value-of select="$padding"/>    a fhir:Coding;<xsl:if test="n1:system/@value">;
<xsl:value-of select="$padding"/>    Coding:system [a fhir:Uri; fhir:value &lt;<xsl:value-of select="n1:system/@value"/>&gt;]</xsl:if><xsl:if test="n1:code/@value">;
<xsl:value-of select="$padding"/>    Coding:code [a fhir:String; fhir:value "<xsl:value-of select="n1:code/@value"/>"]</xsl:if><xsl:if test="n1:display/@value">;
<xsl:value-of select="$padding"/>    Coding:display [a fhir:String; fhir:value "<xsl:value-of select="n1:display/@value"/>"]</xsl:if><xsl:text>
</xsl:text><xsl:value-of select="$padding"/>]</xsl:template>

  <xsl:template name="Text">
    <div>
      <pre class="machine" style="font-size:small">
    Resource:text [
        a fhir:Narrative;
<xsl:if test="n1:status[@value]">        Narrative:status [a fhir:Code; fhir:value "<xsl:value-of select="n1:status/@value"/>"];
</xsl:if>
        <xsl:apply-templates select="xhtml:div"/>    ];
</pre>
    </div>
  </xsl:template>

  <xsl:template match="xhtml:div">        xhtml:div """<xsl:apply-templates select="*|text()" mode="copy" />"""
</xsl:template>

  <xsl:template name="addPrefixes">
    <div>
      <pre class="machine" style="font-size:small">
<span class="comment"># generated by fhir-xml-to-turtle.xslt</span> <!-- xsl:value-of select="$now"/ -->
@prefix : &lt;http://hl7/org/fhir/<xsl:value-of select="name()"/>#&gt; .
@prefix fhir: &lt;http://hl7/org/fhir/&gt; .
@prefix Narrative: &lt;http://hl7/org/fhir/Narrative#&gt; .
@prefix Observation: &lt;http://hl7/org/fhir/Observation#&gt; .
@prefix Quantity: &lt;http://hl7/org/fhir/Quantity#&gt; .
@prefix Resource: &lt;http://hl7/org/fhir/Resource#&gt; .
@prefix Reference: &lt;http://hl7/org/fhir/Reference#&gt; .
@prefix Range: &lt;http://hl7/org/fhir/Range#&gt; .
@prefix Codeable: &lt;http://hl7/org/fhir/Codeable#&gt; .
@prefix Coding: &lt;http://hl7/org/fhir/Coding#&gt; .
@prefix xhtml: &lt;http://www.w3.org/1999/xhtml&gt; .
@prefix xsd: &lt;http://www.w3.org/2001/XMLSchema&gt; .
@base &lt;http://this-fhir-server/fhir/&gt; .
</pre>
    </div>
  </xsl:template>

  <xsl:template name="addCSS">
    <style type="text/css">
      <xsl:text>
	body {
	background-color: #FFFFFF;
	font-family: Verdana, Tahoma, sans-serif;
	font-size: 11px;
	}

	h1 {
	font-size: 12pt;
	font-weight: bold;
	}

	h2 {
	font-size: 11pt;
	font-weight: bold;
	}

	h3 {
	font-size: 10pt;
	font-weight: bold;
	}

	h4 {
	font-size: 8pt;
	font-weight: bold;
	}

	div {
	width: 80%;
	}

	table {
	line-height: 10pt;
	width: 80%;
	}

	tr {
	background-color: #ccccff;
	}

	td {
	padding: 0.1cm 0.2cm;
	vertical-align: top;
	}

	.h1center {
	font-size: 12pt;
	font-weight: bold;
	text-align: center;
	width: 80%;
	}

	.header_table{
	border: 1pt inset #00008b;
	}

	.narr_table {
	width: 100%;
	}

	.narr_tr {
	background-color: #ffffcc;
	}

	.narr_th {
	background-color: #ffd700;
	}

	.td_label{
	font-weight: bold;
	color: white;
	}
	div {
	border: .5ex solid #aaaaff;
	}
	.error {
	background-color: red;
	}
	.orig {
	display:table;
	border: .5ex solid #00ccc6;
	background-color: #00ddd7;
	}

	/* eye-popping RMIM colors */
	.Act                       { background-color: #ff7f7f }
	.ActRelationship           { background-color: #ffbaba }
	.ActRelationship a:visited { background-color: #efaaaa; }
	.ActRelationship a:hover   { background-color: #ffcaca; }
	.Entity                    { background-color: #7fff7f }
	.Role                      { background-color: #ffff7f }
	.Role            a:visited { background-color: #eeee6f; }
	.Role            a:hover   { background-color: #ffffbf; }
	.Participation             { background-color: #7fffff }
	.Participation   a:visited { background-color: #6fefef; }
	.Participation   a:hover   { background-color: #afffff; }
	.anchor { font-weight:bold; }

	.comment { color: #f43; }
      </xsl:text>
    </style>
  </xsl:template>

  <xsl:template name="copy-element" match="*" mode="copy">
    <xsl:text>&lt;</xsl:text><xsl:value-of select="name()"/>
    <xsl:apply-templates select="@*" mode="copy-attr"/>
    <xsl:choose>
      <xsl:when test="count(node()) > 0">
	<xsl:text>&gt;</xsl:text>
	<xsl:apply-templates select="node()" mode="copy" />
	<xsl:text>&lt;/</xsl:text><xsl:value-of select="name()"/><xsl:text>&gt;</xsl:text>
      </xsl:when>
      <xsl:otherwise>
	<xsl:text>/&gt;</xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  <xsl:template name="quote-element" match="*" mode="quote">
    <xsl:if test="$output!='text'">
      <pre class="orig">
	<xsl:call-template name="indent" />
	<xsl:call-template name="copy-element" />
      </pre>
    </xsl:if>
  </xsl:template>
  <xsl:template name="start" match="*" mode="start">
    <xsl:if test="$output!='text'">
      <pre class="orig">
	<xsl:call-template name="indent" />
	<xsl:text>&lt;</xsl:text><xsl:value-of select="name()"/>
	<xsl:apply-templates select="@*" mode="copy-attr"/>
	<xsl:text>&gt;</xsl:text>
      </pre>
    </xsl:if>
  </xsl:template>
  <xsl:template name="end" match="*" mode="end">
    <xsl:if test="$output!='text'">
      <pre class="orig">
	<xsl:call-template name="indent" />
	<xsl:text>&lt;/</xsl:text><xsl:value-of select="name()"/><xsl:text>&gt;</xsl:text>
      </pre>
    </xsl:if>
  </xsl:template>
  <xsl:template name="copy-attr" match="@*" mode="copy-attr">
    <xsl:text> </xsl:text><xsl:value-of select="name()"/><xsl:text>=</xsl:text><xsl:text>"</xsl:text><xsl:value-of select="."/><xsl:text>"</xsl:text>
  </xsl:template>
  <xsl:template name="indent">
    <xsl:if test="preceding-sibling::text()[1]">
      <xsl:choose>
	<xsl:when test="contains(preceding-sibling::text()[1], '&#10;')">
	  <xsl:value-of select="substring-after(preceding-sibling::text()[1], '&#10;')"/>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:value-of select="preceding-sibling::text()[1]"/>
	</xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
