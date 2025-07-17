<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/AMA_ConnectivityLayerRQ">
        <OrderCancelRQ CorrelationID="{Requests/Request/Context/correlationID}" TransactionIdentifier="a3cf6058c27d4e15aab6ffbff17611a6">
            <xsl:attribute name="Version">
                <xsl:choose>
                    <xsl:when test="not(Requests/Request/property)">17.2</xsl:when>
                    <xsl:otherwise>18.1</xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <PointOfSale>
                <Location>
                    <CountryCode>IN</CountryCode>
                    <CityCode>NCE</CityCode>
                </Location>
            </PointOfSale>
            <Document id="document"/>
            <Party>
                <Sender>
                    <TravelAgencySender>
                        <Name>
                            <xsl:value-of select="Requests/Request/TravelAgency/Name"/>
                        </Name>
                        <PseudoCity>AH9D</PseudoCity>
                        <IATA_Number>
                            <xsl:value-of select="Requests/Request/TravelAgency/IATA_Number"/>
                        </IATA_Number>
                        <AgencyID>
                            <xsl:value-of select="Requests/Request/TravelAgency/IATA_Number"/>
                        </AgencyID>
                        <AgentUser>
                            <AgentUserID>xmluser001</AgentUserID>
                        </AgentUser>
                    </TravelAgencySender>
                </Sender>
            </Party>
            <Query>
                <Order OrderID="{Requests/Request/bookingSourceInfo/rloc}" Owner="{Requests/Request/Context/Retailer/code}"/>
            </Query>
        </OrderCancelRQ>
    </xsl:template>
</xsl:stylesheet>