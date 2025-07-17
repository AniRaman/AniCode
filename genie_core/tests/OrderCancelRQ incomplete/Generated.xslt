<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/AMA_ConnectivityLayerRQ">
        <OrderCancelRQ Version="17.2" CorrelationID="{Requests/Request/Context/correlationID}" TransactionIdentifier="PLACEHOLDER">
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
                        <Name><xsl:value-of select="Requests/Request/TravelAgency/Name"/></Name>
                        <PseudoCity>AH9D</PseudoCity>
                        <IATA_Number><xsl:value-of select="Requests/Request/TravelAgency/IATA_Number"/></IATA_Number>
                        <AgencyID><xsl:value-of select="Requests/Request/TravelAgency/IATA_Number"/></AgencyID>
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