### Additional User Instructions and Examples to Generate the XSLT:

1. **Parameterization:**
    a. Parameterize all elements within the `Party` node. Also, parameterize the `VersionNumber` under `PayloadAttributes`. Use the following default values:
        - `AggregatorID`: `'1A'`
        - `Name`: `'Amadeus'`
        - `AirlineDesigCode`: `'KL'`
        - `AgencyID`: `87654324`
        - `ContactInfoRefID`: `'CIPAX'`
        - `IATANumber`: `87654324`
        - `Name`: `'AMADEUS PRODUCT PLANNING'`
        - `PseudoCityID`: `'AMS'`
        - `VersionNumber`: `18.2`

2. **Mapping conditions and Mandatory Sorting:**
    **Instructions for generating SelectedOfferItem:
    1. Filter the actors based on the RefIDs under each product.
    2. Create a dictionary based on the filtered actors and sort the actors by thier FirstName+LastName.
    3. Replace the sorted actors with PAX.
    4. Use the below code to populate elements.
                <xsl:for-each select="Requests/Request/set/product">
                            <ns0:SelectedOfferItem>
                                <ns0:OfferItemRefID><xsl:value-of select="ID"/></ns0:OfferItemRefID>
                                <xsl:variable name="refIds" select = "RefIDs"/>
                                <xsl:variable name="filteredActors">
                                    <xsl:for-each select="AMA_ConnectivityLayerRQ/Requests/Request/actor">
                                        <xsl:if test="contains(concat(' ', $refIds, ' '), concat(' ', ID, ' '))">
                                            <xsl:copy-of select="."/>
                                        </xsl:if>
                                    </xsl:for-each>
                                </xsl:variable>
                                <xsl:variable name="sortedActors" as="element(actor)+">
                                    <xsl:perform-sort select="$filteredActors/actor">
                                        <xsl:sort select="Name/FirstName"/>
                                        <xsl:sort select="Name/LastName"/>
                                    </xsl:perform-sort>
                                </xsl:variable>
                                <xsl:for-each select = "$sortedActors">
                                    <ns0:PaxRefID><xsl:value-of select="concat('PAX', substring(current()/ID, 2))"/></ns0:PaxRefID>
                                </xsl:for-each>
                            </ns0:SelectedOfferItem>
                </xsl:for-each>
        * Do sort only if PTC = ADT
                
    **Instructions for generating ContactInfo under DataLists/ContactInfoList, PaxList under DataLists:
    1. Generate ContactInfoList:
    * Strictly use the below code to populate elements with additional notes given below.
            <xsl:for-each select="Requests/Request/set/product">
                <xsl:variable name="refIds" select = "RefIDs"/>
                <xsl:variable name="filteredActors">
                    <xsl:for-each select="AMA_ConnectivityLayerRQ/Requests/Request/actor">
                        <xsl:if test="contains(concat(' ', $refIds, ' '), concat(' ', ID, ' '))">
                            <xsl:copy-of select="."/>
                        </xsl:if>
                    </xsl:for-each>
                </xsl:variable>
                <xsl:variable name="sortedActors" as="element(actor)+">
                    <xsl:perform-sort select="$filteredActors/actor">
                        <xsl:sort select="Name/FirstName"/>
                        <xsl:sort select="Name/LastName"/>
                    </xsl:perform-sort>
                </xsl:variable>
                <xsl:for-each select = "$sortedActors">
                    <ns0:PaxRefID><xsl:value-of select="concat('CIPAX', substring(current()/ID, 2))"/></ns0:PaxRefID>
                    <!-- populate other elements -->
                </xsl:for-each>
            </xsl:for-each>        
        * The first ContactInfo element is constant; copy its content directly from the output XML.
        * Do sort only if PTC = ADT
        * Exclude actors with PTC=INF who are infants.
    2. Generate PaxList:
        * Strictly use the below code to populate elements with additional notes given below.
            <xsl:for-each select="Requests/Request/set/product">
                <xsl:variable name="refIds" select = "RefIDs"/>
                <xsl:variable name="filteredActors">
                    <xsl:for-each select="AMA_ConnectivityLayerRQ/Requests/Request/actor">
                        <xsl:if test="contains(concat(' ', $refIds, ' '), concat(' ', ID, ' '))">
                            <xsl:copy-of select="."/>
                        </xsl:if>
                    </xsl:for-each>
                </xsl:variable>
                <xsl:variable name="sortedActors" as="element(actor)+">
                    <xsl:perform-sort select="$filteredActors/actor">
                        <xsl:sort select="Name/FirstName"/>
                        <xsl:sort select="Name/LastName"/>
                    </xsl:perform-sort>
                </xsl:variable>
                <xsl:for-each select = "$sortedActors">
                    <ns0:PaxRefID><xsl:value-of select="concat('CIPAX', substring(current()/ID, 2))"/></ns0:PaxRefID>
                    <!-- populate other elements -->
                </xsl:for-each>
            </xsl:for-each>   
        *  Do sort only if PTC = ADT   
        *. For infants (PTC=INF), the ContactInfoRefID should not be included.