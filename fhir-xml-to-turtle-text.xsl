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
  <xsl:param name="output" select="'text'"/>
  <xsl:param name="newline">
    <xsl:choose>
      <xsl:when test="$output='text'"><xsl:value-of select="'&#x0a;'"/></xsl:when>
      <xsl:otherwise><xsl:value-of select="'&#x0d;&#x0a;'"/></xsl:otherwise>
    </xsl:choose>
  </xsl:param>
  <xsl:output method="text" indent="yes" version="4.01" encoding="UTF-8" doctype-system="http://www.w3.org/TR/html4/strict.dtd" doctype-public="-//W3C//DTD HTML 4.01//EN"/>
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
    <xsl:apply-templates select="n1:DiagnosticReport"/>
  </xsl:template>
  <!-- produce browser rendered, human readable clinical document -->
  <xsl:template match="n1:DiagnosticReport">
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
    <xsl:param name="doc" select="'ClinicalDoc'"/>
    <xsl:call-template name="addPrefixes"/>
    <xsl:call-template name="Resource"/>
  </xsl:template>

  <xsl:template name="Resource">
    <div class="machine" style="font-size:small"><pre>
[] a fhir:<xsl:value-of select="name()"/>;</pre>
    <xsl:for-each select="n1:text"><xsl:call-template name="Text"/></xsl:for-each>
    <xsl:if test="n1:status/@value">    :status [a fhir:Code; fhir:value "<xsl:value-of select="n1:status/@value"/>"];
</xsl:if>
    <xsl:if test="n1:issued/@value">    :issued [a fhir:Code; fhir:value "<xsl:value-of select="n1:issued/@value"/>"];
</xsl:if>
    <xsl:apply-templates select="n1:subject" mode="Reference">
      <xsl:with-param name="predicate" select="'subject'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:performer" mode="Reference">
      <xsl:with-param name="predicate" select="'performer'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:reportId" mode="Identifier">
      <xsl:with-param name="predicate" select="'reportId'"/>
    </xsl:apply-templates>
    <xsl:apply-templates select="n1:serviceCategory" mode="Codable">
      <xsl:with-param name="predicate" select="'serviceCategory'"/>
    </xsl:apply-templates>
<pre>.</pre>
    </div>
  </xsl:template>

  <xsl:template name="Reference" match="*" mode="Reference">
    <xsl:param name="predicate"/>    :<xsl:value-of select="$predicate"/> [
        a fhir:Reference; a fhir:<xsl:value-of select="n1:type/@value"/>;
        Reference:reference &lt;<xsl:value-of select="n1:reference/@value"/>&gt;<xsl:if test="n1:display/@value">;
        Reference:display [a fhir:String; fhir:value "<xsl:value-of select="n1:display/@value"/>"]</xsl:if>
    ];
</xsl:template>

  <xsl:template name="Identifier" match="*" mode="Identifier">
    <xsl:param name="predicate"/>    :<xsl:value-of select="$predicate"/> [
        a fhir:Identifier;<xsl:if test="n1:system/@value">;
        :system [a fhir:Uri; fhir:value &lt;<xsl:value-of select="n1:system/@value"/>&gt;]</xsl:if><xsl:if test="n1:coding/@value">;
        :coding [a fhir:String; fhir:value "<xsl:value-of select="n1:coding/@value"/>"]</xsl:if><xsl:if test="n1:code/@value">;
        :code [a fhir:String; fhir:value "<xsl:value-of select="n1:code/@value"/>"]</xsl:if><xsl:if test="n1:key/@value">;
        :key [a fhir:String; fhir:value "<xsl:value-of select="n1:key/@value"/>"]</xsl:if><xsl:if test="n1:display/@value">;
        :display [a fhir:String; fhir:value "<xsl:value-of select="n1:display/@value"/>"]</xsl:if>
    ];
</xsl:template>

  <xsl:template name="Codable" match="*" mode="Codable">
    <xsl:param name="predicate"/>    :<xsl:value-of select="$predicate"/> [
        a fhir:Codable;
	Codeable:coding [<xsl:apply-templates select="n1:coding" mode="Coding"/>
        ]
    ];
</xsl:template>

  <xsl:template name="Coding" match="*" mode="Coding">
            a fhir:Coding;<xsl:if test="n1:system/@value">;
            Coding:system [a fhir:Uri; fhir:value &lt;<xsl:value-of select="n1:system/@value"/>&gt;]</xsl:if><xsl:if test="n1:code/@value">;
            Coding:code [a fhir:String; fhir:value "<xsl:value-of select="n1:code/@value"/>"]</xsl:if><xsl:if test="n1:display/@value">;
            Coding:display [a fhir:String; fhir:value "<xsl:value-of select="n1:display/@value"/>"]</xsl:if>
</xsl:template>

  <xsl:template name="Text">
    <div class="machine" style="font-size:small"><pre>
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
    <div class="machine" style="font-size:small"><pre><span class="comment"># generated by fhir-xml-to-turtle.xslt</span> <!-- xsl:value-of select="$now"/ -->
@prefix : &lt;http://hl7/org/fhir/DiagnosticReport#&gt; .
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
</pre></div>
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
	.machine {
	border: .5ex solid #aaaaff;
	}
	.error {
	background-color: red;
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
    <xsl:text>&lt;</xsl:text><xsl:value-of select="name()"/><xsl:apply-templates select="@*" mode="copy-attr"/><xsl:text>&gt;</xsl:text>
    <xsl:copy>
      <xsl:apply-templates select="node()" mode="copy" />
    </xsl:copy>
    <xsl:text>&lt;/</xsl:text><xsl:value-of select="name()"/><xsl:text>&gt;</xsl:text>
  </xsl:template>
  <xsl:template name="copy-attr" match="@*" mode="copy-attr">
    <xsl:text> </xsl:text><xsl:value-of select="name()"/><xsl:text>=</xsl:text><xsl:text>"</xsl:text><xsl:value-of select="."/><xsl:text>"</xsl:text>
  </xsl:template>

</xsl:stylesheet>
