<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                exclude-result-prefixes="xs"
                version="2.0"
                xmlns:f="http://hl7.org/fhir"
                xmlns:xhtml="http://www.w3.org/1999/xhtml"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xmlns:l="http://local-mods"
                xmlns:mt="http://local/mapping/">

    <!-- Generation date and time -->
    <xsl:param name="now" select="current-dateTime()"/>  <!--xslt version 2 only-->
    <!--<xsl:param name="now" select="'NOW'"/>-->

    <!-- Name of the root document -->
    <xsl:param name="docParam" select="'[]'"/>

    <!-- Generate inner nodes separately or inline (ref or inline) -->
    <xsl:param name="contained" select="'ref'"/>

    <!-- Generate fhir:reference.display node if set to 'ref' -->
    <xsl:param name="reference" select="'ref'"/>

    <!-- If set to nest, literals are generated as anonymous nodes:
        fhir:element  "foo" ;             - no nested
        fhir:element [fhir:value "foo"];  - nested
      -->
    <xsl:param name="literals" select="'nest'"/>

    <!-- Name of the definitions file -->
    <xsl:param name="fhirdefs">definitions.xml</xsl:param>

    <!-- Debugging -->
    <xsl:param name="debug" select="false()"/>

    <xsl:strip-space elements="*"/>
    <xsl:output method="text" omit-xml-declaration="yes" indent="no"/>

    <!-- Table to value<suffix> to type. This looks like a simple upper case
         to lower case table, but it also serves as a list of primitive
         types.  If not on this list (valueFoo) stays upper. -->

    <xsl:variable name="mappings">
        <mt:mappings>
            <entry suffix="Integer" type="integer"/>
            <entry suffix="Decimal" type="decimal"/>
            <entry suffix="DateTime" type="dateTime"/>
            <entry suffix="Date" type="date"/>
            <entry suffix="Time" type="time"/>
            <entry suffix="Instant" type="instant"/>
            <entry suffix="String" type="string"/>
            <entry suffix="Uri" type="uri"/>
            <entry suffix="Boolean" type="boolean"/>
            <entry suffix="Code" type="code"/>
            <entry suffix="Base64Binary" type="base64Binary"/>
            <entry suffix="UnsignedInt" type="unsignedInt"/>
            <entry suffix="PositiveInt" type="positiveInt"/>
            <entry suffix="Id" type="id"/>
            <entry suffix="Oid" type="oid"/>
            <entry suffix="Markdown" type="markdown"/>
        </mt:mappings>
    </xsl:variable>

    <!-- XSLT 1.0 only -->
    <xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'" />
    <xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />

    <!-- Entry point -->
    <xsl:template match="/">
        <xsl:text># generated on  </xsl:text>
        <xsl:value-of select="$now"/>
        <xsl:call-template name="eol"/>
        <xsl:call-template name="eol"/>
        <xsl:apply-templates select="*" mode="root"/>
    </xsl:template>

    <!-- Actual document starts here -->
    <xsl:template match="*" mode="root">
        <xsl:call-template name="addPrefixes">
            <xsl:with-param name="name" select="name(.)"/>
        </xsl:call-template>
        <xsl:call-template name="ResourceRoot">
            <xsl:with-param name="subject" select="$docParam"/>
        </xsl:call-template>
    </xsl:template>

    <!-- We'll traverse the FHIR instance XML data ($this param) while
     simultanously hopping around a build-in XML structure describing
     each FHIR path and its associated types + sub-propeties ($context param)
     We kick things off from the XML root element... -->
    <xsl:template name="ResourceRoot">
        <xsl:param name="subject"/>

        <xsl:call-template name="FhirElement">
            <xsl:with-param name="subject" select="$subject"/>
        </xsl:call-template>
        <xsl:call-template name="end_subject"/>
        <xsl:call-template name="eol"/>

        <!-- If contained elements are going to be addressed by reference, make a collection of them up front -->
        <xsl:if test="$contained = 'ref'">
            <!-- Reference contained elements by id.
                Example:   <contained>
                                <Observation id="o9">
                                ...
              -->
            <xsl:for-each select=".//f:contained/*">
                <xsl:call-template name="FhirElement">
                    <xsl:with-param name="subject">
                        <xsl:call-template name="as_url">
                            <xsl:with-param name="value" select="f:id/@value"/>
                        </xsl:call-template>
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:for-each>
        </xsl:if>

        <!-- Convert reference/display tuples into:
            <reference/@value> fhir:Reference.display [fhir:value "display/@value"] ;
          -->
        <xsl:if test="$reference = 'ref'">
            <xsl:for-each select=".//f:reference[../f:display]">
                <xsl:call-template name="as_url"> </xsl:call-template>
                <xsl:text> fhir:Reference.display </xsl:text>
                <xsl:call-template name="TypedLiteral">
                    <xsl:with-param name="value" select="../f:display/@value"/>
                </xsl:call-template>
                <xsl:text> .</xsl:text>
                <xsl:call-template name="eol"/>
            </xsl:for-each>
        </xsl:if>

    </xsl:template>


    <!-- called with any f:extension elements anywhere, anytime, you name it, buddy.
change
      from:                                    to:
  <modifierExtension>                     <http://...plus> [
    <url value="http://...plus"/>            a fhir:modified_integer;
    <valueInteger value="2"/>                <http://...times> [
    <modifierExtension>                         a fhir:modified_integer;
      <url value="http://...times"/>            fhir:value "5";
      <valueInteger value="5"/>              ];
    </modifierExtension>                     fhir:modifiedBy <http://...times>;
  </modifierExtension>                       fhir:value "2";
                                          ];
                                          fhir:modifiedBy <http://...plus>;
 -->
    <xsl:template name="extension">
        <xsl:param name="depth"/>
        <xsl:param name="this"/>

        <!-- <http://...plus> [ -->
        <xsl:call-template name="idnt">
            <xsl:with-param name="depth" select="$depth"/>
        </xsl:call-template>
        <xsl:call-template name="as_url">
            <xsl:with-param name="value" select="f:url/@value"/>
        </xsl:call-template>

        <!-- [ -->
        <xsl:text> [</xsl:text>
        <xsl:if test="not(*[substring(name(), 1, 5) = 'value'])">
            <!-- ugh, why do i need this? -->
            <xsl:text>8</xsl:text>
            <xsl:call-template name="eol"/>
        </xsl:if>

        <!-- find the (one) value element, e.g. f:valueInteger -->
        <xsl:for-each select="*[substring(name(), 1, 5) = 'value']">
            <xsl:variable name='sfx' select="substring(name(), 6)"/>
            <!-- change 'f:valueInteger' into 'integer' but NOT f:valueFoo into 'foo' (keep caps in types) -->
            <xsl:variable name="type1">
                <xsl:value-of select="$mappings/mt:mappings/entry[@suffix = $sfx]/@type"/>
            </xsl:variable>
            <xsl:variable name="type">
                <xsl:choose>
                    <xsl:when test="$type1 != ''">
                        <xsl:value-of select="$type1"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="substring(name(), 6)"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>

            <xsl:call-template name="FhirElement">
                <xsl:with-param name="depth" select="$depth + 1"/>
                <xsl:with-param name="context" select="$type"/>
            </xsl:call-template>
        </xsl:for-each>

        <!-- or find the n extensions -->
        <xsl:for-each select="f:extension | f:modifierExtension">
            <xsl:call-template name="extension">
                <xsl:with-param name="depth" select="$depth + 1"/>
            </xsl:call-template>
        </xsl:for-each>

        <!-- ]; -->
        <xsl:call-template name="idnt">
            <xsl:with-param name="depth" select="$depth"/>
        </xsl:call-template>
        <xsl:call-template name="endliteral"/>
        <xsl:text>;</xsl:text>
        <xsl:call-template name="eol"/>

        <xsl:if test="name(.) = 'modifierExtension'">
            <!-- fhir:modifiedBy <http://...plus>; -->
            <xsl:call-template name="idnt">
                <xsl:with-param name="depth" select="$depth"/>
            </xsl:call-template>
            <xsl:value-of select="'fhir:modifiedBy '"/>
            <xsl:call-template name="as_url_eol">
                <xsl:with-param name="value" select="f:url/@value"/>
                <xsl:with-param name="semi" select="false()"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>

    <!-- Main workhorse - output the definition of a FHIR element
        param: depth - indentation level
        param: this  - where we are in the FHIR instance
        param: context - name of the accompanying FHIR definition (in definitions.xsl)
        param: subject - thing being defined
        -->
    <xsl:template name="FhirElement">
        <xsl:param name="depth" select="0"/>
        <xsl:param name="this" select="."/>
        <xsl:param name="context" select="name()"/>
        <xsl:param name="subject"/>

        <xsl:variable name="def" select="document($fhirdefs)/l:fhirdefs/path/fhir_path[text() = $context]/.."/>
        <xsl:if test="$context != 'xhtml'">
            <xsl:if test="not($def)"> 
                WARNING: <xsl:value-of select="$context"/> NOT FOUND IN THE DEFINITIONS </xsl:if>
        </xsl:if>

        <!-- Type of the current element. Type can be null (for internal nodes) -->
        <xsl:variable name="def.type" select="$def/type"/>

        <!-- Sub-elemenets that are defined for this type.  Each sub includes
           * an xpath fragment (e.g. 'f:detail')
           * FHIR path (e.g. Order.detail)
           * target type (e.g. CodeableConcept; or blank if the target is an internal node)
         (Resource) sub-elements of type Extension are handled separately.
         Properties appear to have no sub-elements for Extensions. -->
        <xsl:variable name="def.subs" select="$def/subs/sub[type != 'Extension']"/>
        <xsl:choose>
            <!-- TODO possibly handlers for (some) datatyes: e.g. text-->

            <!-- This first branch represents a leaf node for which no further properties are defined in FHIR Spreadsheets -->
            <xsl:when test="not($def) or $def/fhir_path = 'Reference'">

                <xsl:call-template name="eol"/>
                <xsl:if test="$context != 'Reference'">
                    <xsl:call-template name="idnt">
                        <xsl:with-param name="depth" select="$depth + 1"/>
                    </xsl:call-template>
                    <xsl:if test="$subject">
                        <xsl:value-of select="$subject"/>
                        <xsl:text> </xsl:text>
                    </xsl:if>
                    <xsl:text>a fhir:</xsl:text>
                    <xsl:if test="name(..) = 'modifierExtension'">
                        <xsl:text>modifying_</xsl:text>
                        <!-- a modifying_integer -->
                    </xsl:if>
                    <xsl:value-of select="$context"/>
                    <xsl:text>;</xsl:text>
                    <xsl:call-template name="eol"/>
                </xsl:if>
                <xsl:for-each select="../f:extension | ../f:modifierExtension">
                    <xsl:call-template name="extension">
                        <xsl:with-param name="depth" select="$depth + 1"/>
                        <xsl:with-param name="this" select="."/>
                    </xsl:call-template>
                </xsl:for-each>
                <xsl:if test="$context = 'Reference'">
                    <!--  or $context = 'resource'" -->
                    <!-- @@ $reference = 'ref' and ? -->
                    <xsl:call-template name="idnt">
                        <xsl:with-param name="depth" select="$depth"/>
                    </xsl:call-template>
                    <xsl:text>a fhir2:</xsl:text>
                    <xsl:value-of select="$this/f:type/@value"/>
                    <xsl:text>Reference;</xsl:text>
                    <xsl:call-template name="eol"/>
                    <xsl:call-template name="idnt">
                        <xsl:with-param name="depth" select="$depth"/>
                    </xsl:call-template>
                    <xsl:text>fhir:Reference.reference </xsl:text>
                    <xsl:call-template name="as_url_eol">
                        <xsl:with-param name="value" select="$this/f:reference/@value"/>
                    </xsl:call-template>
                    <xsl:if test="$this/f:display/@value">
                        <xsl:call-template name="idnt">
                            <xsl:with-param name="depth" select="$depth"/>
                        </xsl:call-template>
                        <xsl:text>fhir:Reference.display </xsl:text>
                        <xsl:call-template name="LeafNode">
                            <xsl:with-param name="value" select="$this/f:display/@value"/>
                        </xsl:call-template>
                        <xsl:call-template name="eol"/>
                    </xsl:if>
                </xsl:if>

                <xsl:if test="$this/@value">
                    <xsl:call-template name="idnt">
                        <xsl:with-param name="depth" select="$depth"/>
                    </xsl:call-template>
                    <xsl:text>fhir:value </xsl:text>
                    <xsl:call-template name="LeafNode">
                        <xsl:with-param name="value" select="concat('&quot;', $this/@value, '&quot;')"/>
                    </xsl:call-template>
                </xsl:if>
                <xsl:if test="$context = 'xhtml'">
                    <xsl:call-template name="idnt">
                        <xsl:with-param name="depth" select="$depth + 1"/>
                    </xsl:call-template>
                    <xsl:variable name="xml">
                        <xsl:for-each select="$this">
                            <xsl:call-template name="copy-element"/>
                        </xsl:for-each>
                    </xsl:variable>
                    <xsl:text>fhir:text </xsl:text>
                    <xsl:call-template name="LeafNode">
                        <xsl:with-param name="value" select="concat('&quot;&quot;&quot;', $xml, '&quot;&quot;&quot;')"/>
                    </xsl:call-template>
                </xsl:if>
            </xsl:when>

            <!-- This second branch represents a node with subproperties defined in FHIR Spreadsheets -->
            <xsl:otherwise>

                <xsl:if test="$subject">
                    <xsl:value-of select="$subject"/>
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:if test="$depth > 0">
                    <xsl:call-template name="eol"/>
                </xsl:if>

                <!-- If this is a type (non-internal) node, output the type -->
                <xsl:if test="$def.type != '' and $def.type != 'BackboneElement'">
                    <xsl:if test="$depth">
                        <xsl:call-template name="idnt">
                            <xsl:with-param name="depth" select="$depth + 1"/>
                        </xsl:call-template>
                    </xsl:if>

                    <xsl:text>a fhir:</xsl:text>
                    <xsl:choose>
                        <xsl:when test="f:modifierExtension">
                            <!-- <Resource>:modified_<Property>  -->
                            <xsl:value-of select="concat('modified_', $def.type)"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:value-of select="$def.type"/>
                        </xsl:otherwise>
                    </xsl:choose>
                    <xsl:text>;</xsl:text>
                    <xsl:call-template name="eol"/>
                </xsl:if>

                <xsl:for-each select="f:extension | f:modifierExtension">
                    <xsl:call-template name="extension">
                        <xsl:with-param name="depth" select="$depth + 1"/>
                        <xsl:with-param name="this" select="."/>
                    </xsl:call-template>
                </xsl:for-each>
                <!-- Iterate over defined subproperties, making a recursive application of FhirElement -->
                <xsl:for-each select="$def.subs">
                    <xsl:variable name="last_property_p" select="position() = last()"/>
                    <xsl:variable name="sub" select="."/>
                    <xsl:variable name="predicate" select="./predicate"/>
                    <xsl:variable name="fhir_path" select="./fhir_path"/>
                    <xsl:variable name="type" select="./type"/>
                    <xsl:variable name="xpath">
                        <xsl:call-template name="replace_choice_element">
                            <xsl:with-param name="relpath" select="./relative_xpath"/>
                            <xsl:with-param name="fhir_path" select="$fhir_path"/>
                        </xsl:call-template>
                    </xsl:variable>
                    <xsl:call-template name="debug">
                        <xsl:with-param name="text">searching on <xsl:value-of select="$predicate"/> via <xsl:value-of select="$xpath"/></xsl:with-param>
                    </xsl:call-template>

                    <!-- for a given property, look for its occurence(s) in instance data -->
                    <xsl:for-each select="$this/*[lower-case(name()) = lower-case($xpath)]">  
                    <!--xslt version 2 only-->
                    <!--<xsl:for-each select="$this/*[name() = translate($xpath, $uppercase, $lowercase)]">-->
                        <!-- include contained arcs -->
                        <xsl:variable name="last_instance_p" select="position() = last()"/>
                        <xsl:call-template name="idnt">
                            <xsl:with-param name="depth" select="$depth + 1"/>
                        </xsl:call-template>
                        <xsl:choose>
                            <xsl:when test="f:modifierExtension">
                                <!-- <Resource>:modified_<Property>  -->
                                <xsl:value-of
                                    select="
                                        concat(substring-before($predicate, ':'),
                                        ':modified_',
                                        substring-after($predicate, ':'))"
                                />
                            </xsl:when>
                            <xsl:when test="name() = 'contained'">
                                <!-- include contained arcs -->
                                <xsl:text>fhir:contained</xsl:text>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="$predicate"/>
                            </xsl:otherwise>
                        </xsl:choose>
                        <xsl:text> </xsl:text>
                        <xsl:variable name="subcontext">
                            <xsl:choose>
                                <xsl:when test="$type != '' and $type != 'BackboneElement'">
                                    <xsl:value-of select="$type"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="$fhir_path"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:variable>
                        <xsl:choose>
                            <xsl:when test="name() = 'contained'">
                                <!-- Reference contained elements by id: -->
                                <xsl:for-each select="*">
                                    <xsl:if test="$contained = 'ref'">
                                        <xsl:call-template name="as_url">
                                            <xsl:with-param name="value" select="f:id/@value"/>
                                        </xsl:call-template>
                                    </xsl:if>
                                    <xsl:if test="$contained = 'inline'">
                                        <xsl:call-template name="beginblock"/>
                                        <xsl:call-template name="FhirElement">
                                            <xsl:with-param name="depth" select="$depth + 1"/>
                                            <xsl:with-param name="this" select="."/>
                                            <xsl:with-param name="context" select="name()"/>
                                            <!--xsl:with-param name="subject" select="concat('&lt;', $docParam, '#', @id, '&gt;')"/ -->
                                        </xsl:call-template>
                                        <xsl:call-template name="idnt">
                                            <xsl:with-param name="depth" select="$depth + 1"/>
                                        </xsl:call-template>
                                        <xsl:call-template name="endblock"/>
                                    </xsl:if>
                                    <xsl:choose>
                                        <xsl:when test="following-sibling::*">
                                            <xsl:text>,</xsl:text>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <xsl:text>;</xsl:text>
                                            <xsl:call-template name="eol"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:for-each>
                            </xsl:when>
                            <!-- perform the mappings to xsd types per
                             http://www.hl7.org/implement/standards/fhir/datatypes.html#
                            http://www.hl7.org/implement/standards/fhir/datatypes-examples.html -->
                            <!-- modifierExtension changes the meaning of the element.  We still need to
                                decide what to do with modifiers in the context of RDF -->
                            <xsl:when test="not(name(..) = 'modifierExtension')">
                                <xsl:choose>
                                    <!-- ================== boolean ============= -->
                                    <xsl:when test="$subcontext = 'boolean'">
                                        <xsl:call-template name="LeafNode"/>
                                    </xsl:when>
                                    <!-- ================== id ================== -->
                                    <xsl:when test="$subcontext = 'id'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'fhir:id'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ================== decimal =============== -->
                                    <xsl:when test="$subcontext = 'decimal'">
                                        <xsl:variable name="lexicalValue">
                                            <xsl:choose>
                                                <xsl:when test="contains(@value, '.')">
                                                    <xsl:value-of select="@value"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:value-of select="concat(@value, '.0')"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:variable>
                                        <xsl:call-template name="beginliteral"/>
                                        <xsl:value-of select="$lexicalValue"/>
                                        <xsl:if test="@fractionDigits and $literals = 'nest'">
                                            <xsl:text>; fhir:fractionalDigits </xsl:text>
                                            <xsl:value-of select="@fractionDigits"/>
                                        </xsl:if>
                                        <xsl:call-template name="endliteral"/>
                                    </xsl:when>
                                    <!-- ================== integer =============== -->
                                    <xsl:when test="$subcontext = 'integer'">
                                        <xsl:call-template name="LeafNode"/>
                                    </xsl:when>
                                    <!-- ================== unsignedInt =============== -->
                                    <xsl:when test="$subcontext = 'unsignedInt'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'xsd:nonNegativeInteger'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ================== positiveInt =============== -->
                                    <xsl:when test="$subcontext = 'positiveInt'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'xsd:positiveInteger'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- =================== base64Binary ========== -->
                                    <xsl:when test="$subcontext = 'base64Binary'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'xsd:base64Binary'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ==================== instant ============== -->
                                    <xsl:when test="$subcontext = 'instant'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'xsd:dateTime'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ===================== string =============== -->
                                    <xsl:when test="$subcontext = 'string'">
                                        <xsl:call-template name="TypedLiteral"/>
                                    </xsl:when>
                                    <!-- ===================== code =============== -->
                                    <xsl:when test="$subcontext = 'code'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'fhir:code'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ===================== oid =============== -->
                                    <xsl:when test="$subcontext = 'oid'">
                                        <xsl:call-template name="TypedLiteralEOL">
                                            <xsl:with-param name="type" select="'fhir:oid'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ===================== markdown =============== -->
                                    <xsl:when test="$subcontext = 'oid'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'fhir:markdown'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ====================== uri ================= -->
                                    <xsl:when test="$subcontext = 'uri'">
                                        <xsl:call-template name="TypedLiteral"/>
                                    </xsl:when>
                                    <!-- ====================== date ================ -->
                                    <xsl:when test="$subcontext = 'date'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'xsd:date'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ====================== time ================ -->
                                    <xsl:when test="$subcontext = 'time'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'xsd:time'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <!-- ====================== dateTime ================ -->
                                    <xsl:when test="$subcontext = 'dateTime'">
                                        <xsl:call-template name="TypedLiteral">
                                            <xsl:with-param name="type" select="'xsd:dateTime'"/>
                                        </xsl:call-template>
                                    </xsl:when>
                                    <xsl:when test="$reference = 'ref' and $type = 'Reference'">
                                        <xsl:choose>
                                            <xsl:when test="not(f:reference/@value) and f:display/@value">
                                                <xsl:text>[ fhir:Reference.display </xsl:text>
                                                <xsl:call-template name="LeafNode">
                                                  <xsl:with-param name="value" select="concat('&quot;', f:display/@value, '&quot;')"/>
                                                </xsl:call-template>
                                                <xsl:text> ]</xsl:text>
                                            </xsl:when>
                                            <xsl:when test="contains(f:reference/@value, '#')">
                                                <xsl:call-template name="as_url">
                                                    <xsl:with-param name="value" select="concat($docParam, f:reference/@value)"/>
                                                </xsl:call-template>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:call-template name="as_url">
                                                    <xsl:with-param name="value" select="f:reference/@value"/>
                                                </xsl:call-template>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                        <!--<xsl:call-template name="as_url" xml:space="f:reference/@value"/>
                                        <xsl:call-template name="eol"/>-->
                                        <xsl:if test="not($last_property_p and $last_instance_p)">
                                            <xsl:text>;</xsl:text>
                                        </xsl:if>
                                        <xsl:call-template name="eol"/>
                                        <!-- <xsl:text># skip a resource of type Resource on path: </xsl:text> -->
                                        <!-- <xsl:value-of select="$fhir_path"/> -->
                                        <!-- <xsl:text>  xpath: </xsl:text> -->
                                        <!-- <xsl:value-of select="$xpath"/> -->
                                        <!-- <xsl:call-template name="eol"/> -->
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:call-template name="CompoundElement">
                                            <xsl:with-param name="depth" select="$depth"/>
                                            <xsl:with-param name="subcontext" select="$subcontext"/>
                                            <xsl:with-param name="last_instance_p" select="$last_instance_p"/>
                                            <xsl:with-param name="last_property_p" select="$last_property_p"/>
                                        </xsl:call-template>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:if test="not($last_property_p and $last_instance_p)">
                                    <xsl:text>;</xsl:text>
                                </xsl:if>
                                <xsl:call-template name="eol"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:call-template name="CompoundElement">
                                    <xsl:with-param name="depth" select="$depth"/>
                                    <xsl:with-param name="subcontext" select="$subcontext"/>
                                    <xsl:with-param name="last_instance_p" select="$last_instance_p"/>
                                    <xsl:with-param name="last_property_p" select="$last_property_p"/>
                                </xsl:call-template>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template name="CompoundElement">
        <xsl:param name="depth"/>
        <xsl:param name="subcontext"/>
        <xsl:param name="last_property_p"/>
        <xsl:param name="last_instance_p"/>

        <xsl:call-template name="beginblock"/>
        <xsl:call-template name="FhirElement">
            <xsl:with-param name="depth" select="$depth + 1"/>
            <xsl:with-param name="this" select="."/>
            <xsl:with-param name="context" select="$subcontext"/>
        </xsl:call-template>
        <xsl:call-template name="idnt">
            <xsl:with-param name="depth" select="$depth + 1"/>
        </xsl:call-template>

        <!-- This test only works because FHIR's examples are all serialized with propertiese
                                 in the same order as in the defining spreadsheets.  It will sometimes think a
                                 terminal entry is non-terminal, e.g. if the last property has no instance. -->
        <xsl:call-template name="endblock"/>
        <!--<xsl:if test="not($last_property_p) or not($last_instance_p)">
            <xsl:text>;</xsl:text>
        </xsl:if>-->
    </xsl:template>


    <xsl:template name="id_datatype">
        <xsl:param name="value"/>
        <xsl:text>a fhir:id;</xsl:text>
        <xsl:call-template name="LeafNodeEOL">
            <xsl:with-param name="value" select="$value"/>
        </xsl:call-template>
    </xsl:template>

    <!-- fractionDigits is optional and not emitted if missing -->
    <xsl:template name="decimal_datatype">
        <xsl:param name="value"/>
        <xsl:param name="fractionDigits"/>
    </xsl:template>

    <xsl:template name="copy-element" match="*" mode="copy">
        <xsl:text>&lt;</xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:apply-templates select="@*" mode="copy-attr"/>
        <xsl:choose>
            <xsl:when test="count(node()) > 0">
                <xsl:text>&gt;</xsl:text>
                <xsl:apply-templates select="node()" mode="copy"/>
                <xsl:text>&lt;/</xsl:text>
                <xsl:value-of select="name()"/>
                <xsl:text>&gt;</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text>/&gt;</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template name="copy-attr" match="@*" mode="copy-attr">
        <xsl:text> </xsl:text>
        <xsl:value-of select="name()"/>
        <xsl:text>=</xsl:text>
        <xsl:text>"</xsl:text>
        <xsl:value-of select="."/>
        <xsl:text>"</xsl:text>
    </xsl:template>

    <!-- addPrefixes: generate the header prefixes
        param: name - local namespace of the resource
     -->
    <xsl:variable name="prefixes"> <!--xslt version 2 only-->
        <mt:prefixes xmlns="http://local/mapping/">
            <prefix pfx="fhir:">http://hl7.org/fhir/</prefix>
            <prefix pfx="xhtml:">http://www.w3.org/1999/xhtml</prefix>
            <prefix pfx="xsd:">http://www.w3.org/2001/XMLSchema</prefix>
        </mt:prefixes>
    </xsl:variable> <!--xslt version 2 only-->

    <xsl:template name="addPrefixes">
        <xsl:param name="name"/>
        <xsl:call-template name="prefix">
            <xsl:with-param name="pfx" select="concat($name, ':')"/>
            <xsl:with-param name="uri" select="concat('http://hl7.org/fhir/', $name)"/>
        </xsl:call-template>
        <xsl:for-each select="$prefixes/mt:prefixes/mt:prefix">  <!--xslt version 2 only-->
        <!--<xsl:for-each select="document('')/mt:prefixes/mt:prefix">-->
            <xsl:call-template name="prefix">
                <xsl:with-param name="pfx" select="@pfx"/>
                <xsl:with-param name="uri" select="."/>
            </xsl:call-template>
        </xsl:for-each>
        <xsl:text>@base </xsl:text>
        <xsl:call-template name="as_url">
            <xsl:with-param name="value">http://this-fhir-server/fhir/</xsl:with-param>
        </xsl:call-template>
        <xsl:text> .</xsl:text>
        <xsl:call-template name="eol"/>
        <xsl:call-template name="eol"/>
    </xsl:template>

    <xsl:template name="prefix">
        <xsl:param name="pfx"/>
        <xsl:param name="uri"/>
        <xsl:text>@prefix </xsl:text>
        <xsl:value-of select="$pfx"/>
        <xsl:text> </xsl:text>
        <xsl:call-template name="as_url">
            <xsl:with-param name="value" select="$uri"/>
        </xsl:call-template>
        <xsl:text> .</xsl:text>
        <xsl:call-template name="eol"/>
    </xsl:template>

    <!-- ============================================
        Utilities
        ============================================= -->
    <!-- as_url: convert the supplied value (default @value) into a url -->
    <xsl:template name="as_url">
        <xsl:param name="value" select="@value"/>
        <xsl:param name="semi" select="false()"/>
        <xsl:param name="eol" select="false()"/>
        <xsl:value-of select="concat('&lt;', $value, '&gt;')"/>
        <xsl:if test="$semi">;</xsl:if>
        <xsl:if test="$eol">
            <xsl:call-template name="eol"/>
        </xsl:if>
    </xsl:template>

    <xsl:template name="as_url_eol">
        <xsl:param name="value" select="@value"/>
        <xsl:param name="semi" select="true()"/>
        <xsl:param name="eol" select="true()"/>
        <xsl:call-template name="as_url">
            <xsl:with-param name="value" select="$value"/>
            <xsl:with-param name="semi" select="$semi"/>
            <xsl:with-param name="eol" select="$eol"/>
        </xsl:call-template>
    </xsl:template>


    <!-- beginliteral - start of a literal -->
    <xsl:template name="beginliteral">
        <xsl:if test="$literals = 'nest'">
            <xsl:call-template name="beginblock"/>
            <xsl:text>fhir:value </xsl:text>
        </xsl:if>
    </xsl:template>

    <!-- endliteral - end of a literal -->
    <xsl:template name="endliteral">
        <xsl:if test="$literals = 'nest'">
            <xsl:call-template name="endblock"/>
        </xsl:if>
    </xsl:template>

    <!-- escapeliteral - escape special characters in a literal -->
    <xsl:template name="escapeliteral">
        <xsl:param name="value" select="@value"/>
        <!-- TODO: add escaping -->
        <xsl:value-of select="$value"/>
    </xsl:template>
    
    <xsl:template name="beginblock">
        <xsl:text>[ </xsl:text>
    </xsl:template>
    
    <xsl:template name="endblock">
        <xsl:text> ]</xsl:text>
    </xsl:template>

    <xsl:template name="eol">
        <xsl:text>&#10;</xsl:text>
    </xsl:template>

    <!-- LeafNode:  generate a direct literal or bnode with a value.
        param: value - value
      -->
    <xsl:template name="LeafNode">
        <xsl:param name="value" select="@value"/>
        <xsl:call-template name="beginliteral"/>
        <xsl:call-template name="escapeliteral">
            <xsl:with-param name="value" select="$value"/>
        </xsl:call-template>
        <xsl:call-template name="endliteral"/>
    </xsl:template>

    <!-- LeafNodeEOL:  generate a leaf node w/ a carriage return -->
    <xsl:template name="LeafNodeEOL">
        <xsl:param name="value" select="@value"/>
        <xsl:call-template name="LeafNode">
            <xsl:with-param name="value" select="$value"/>
        </xsl:call-template>
        <xsl:call-template name="eol"/>
    </xsl:template>

    <!-- TypedLiteral: generate a leaf node w/ a typed literal -->
    <xsl:template name="TypedLiteralEOL">
        <xsl:param name="value" select="@value"/>
        <xsl:param name="type"/>
        <xsl:call-template name="LeafNodeEOL">
            <xsl:with-param name="value">
                <xsl:value-of select="concat('&quot;', $value, '&quot;')"/>
                <xsl:if test="@type">
                    <xsl:value-of select="concat('^^', $type)"/>
                </xsl:if>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="TypedLiteral">
        <xsl:param name="value" select="@value"/>
        <xsl:param name="type"/>
        <xsl:call-template name="LeafNode">
            <xsl:with-param name="value">
                <xsl:value-of select="concat('&quot;', $value, '&quot;')"/>
                <xsl:if test="@type">
                    <xsl:value-of select="concat('^^', $type)"/>
                </xsl:if>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>

    <!-- Indent -->
    <xsl:template name="idnt">
        <xsl:param name="depth"/>
        <xsl:if test="$depth > 0">
            <xsl:text>   </xsl:text>
            <xsl:call-template name="idnt">
                <xsl:with-param name="depth" select="number($depth) - 1"/>
            </xsl:call-template>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="end_subject">
        <xsl:text> .</xsl:text>
    </xsl:template>
    
    <xsl:template name="replace_choice_element">
        <xsl:param name="fhir_path"/>
        <xsl:param name="relpath"/>
        <xsl:choose>
            <xsl:when test="contains($relpath, '[x]')">
                <xsl:value-of select="replace($fhir_path, '.*\.', '')"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="substring-after($relpath, ':')"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <!-- =========== Debugging =============== -->
    <xsl:template name="debug">
        <xsl:param name="text"/>
        <xsl:if test="$debug">
            <xsl:call-template name="eol"/>
            <xsl:text># </xsl:text>
            <xsl:value-of select="$text"/>
            <xsl:call-template name="eol"/>
        </xsl:if>
    </xsl:template>

    <xsl:template match="text()">
        <xsl:if test="normalize-space('.')">
            <xsl:text>UNPROCESSED: '</xsl:text>
            <xsl:value-of select="."/>
            <xsl:text>'</xsl:text>
        </xsl:if>
    </xsl:template>

</xsl:stylesheet>
