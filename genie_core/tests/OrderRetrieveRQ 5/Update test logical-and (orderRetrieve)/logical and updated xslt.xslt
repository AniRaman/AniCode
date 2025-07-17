<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/AMA_ConnectivityLayerRQ">
        <OrderRetrieveRQ 
            Version="17.2" 
            TransactionIdentifier="{Requests/Request/Context/correlationID}" 
            CorrelationID="{Requests/Request/Context/correlationID}">
            <PointOfSale>
                <Location>
                    <CountryCode>FR</CountryCode>
                    <CityCode>NCE</CityCode>
                </Location>
            </PointOfSale>
            <Document id="document"/>
            <Party>
                <Sender>
                    <TravelAgencySender>
                        <xsl:if test="Requests/Request/TravelAgency">
                            <Name><xsl:value-of select="Requests/Request/TravelAgency/Name"/></Name>
                            <PseudoCity>AH9D</PseudoCity>
                            <IATA_Number><xsl:value-of select="Requests/Request/TravelAgency/IATA_Number"/></IATA_Number>
                            <AgencyID><xsl:value-of select="Requests/Request/TravelAgency/IATA_Number"/></AgencyID>
                            <AgentUser>
                                <AgentUserID>xmluser001</AgentUserID>
                            </AgentUser>
                        </xsl:if>
                    </TravelAgencySender>
                </Sender>
                <!-- New logic to add CityTax if conditions are met -->
                <xsl:if test="Requests/Request/distributionMethod='NDCX' and Requests/Request/TravelAgency/Contact/Address/CityName='FRANKFURT'">
                    <CityTax>Frankfurt Tax</CityTax>
                </xsl:if>
            </Party>
            <Query>
                <Filters>
                    <OrderID Owner="{Requests/Request/Context/Retailer/code}">
                        <xsl:value-of select="Requests/Request/bookingSourceInfo/rloc"/>
                    </OrderID>
                </Filters>
            </Query>
        </OrderRetrieveRQ>
    </xsl:template>
</xsl:stylesheet>