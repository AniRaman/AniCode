<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform ">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/">
        <OrderCancelRQ Version="17.2" CorrelationID="{Request/Context/correlationID}" TransactionIdentifier="a3cf6058c27d4e15aab6ffbff17611a6">
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
                        <Name><xsl:value-of select="Request/TravelAgency/Name"/></Name>
                        <PseudoCity>AH9D</PseudoCity>
                        <IATA_Number><xsl:value-of select="Request/TravelAgency/IATA_Number"/></IATA_Number>
                        <AgencyID><xsl:value-of select="Request/TravelAgency/IATA_Number"/></AgencyID>
                        <AgentUser>
                            <AgentUserID>xmluser001</AgentUserID>
                        </AgentUser>
                    </TravelAgencySender>
                </Sender>
            </Party>
        </OrderCancelRQ>
    </xsl:template>
</xsl:stylesheet>