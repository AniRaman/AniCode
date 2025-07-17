<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ns0="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage" xmlns:ns1="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/">
        <AMA_ConnectivityLayerRS>
            <Requests>
                <Request>
                    <target>VY</target>
                    <id>1</id>
                    <action>retrieve</action>
                    <DistributionMethod>NDC</DistributionMethod>
                    <Context>
                        <correlationID>
                            <!-- Mapping needed -->
                        </correlationID>
                        <Retailer>
                            <!-- Mapping needed -->
                        </Retailer>
                    </Context>
                    <bookingSourceInfo>
                        <rloc>
                            <xsl:value-of select="'L12345'"/>
                        </rloc>
                    </bookingSourceInfo>
                    <TravelAgency>
                        <IATA_Number>08206881</IATA_Number>
                        <Name>ATravelAgencyName</Name>
                    </TravelAgency>
                    <xsl:for-each select="//ns1:PaxList/ns1:Pax">
                        <actor>
                            <ID>
                                <xsl:value-of select="ns1:PaxID"/>
                            </ID>
                            <TID>
                                <xsl:value-of select="ns1:PaxID"/>
                            </TID>
                            <xsl:if test="ns1:ContactInfoRefID">
                                <address>
                                    <line>
                                        <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:PostalAddress/ns1:StreetText"/>
                                    </line>
                                    <zip>
                                        <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:PostalAddress/ns1:PostalCode"/>
                                    </zip>
                                    <cityName>
                                        <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:PostalAddress/ns1:CityName"/>
                                    </cityName>
                                    <stateName>
                                        <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:PostalAddress/ns1:CountrySubDivisionName"/>
                                    </stateName>
                                    <countryCode>
                                        <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:PostalAddress/ns1:CountryCode"/>
                                    </countryCode>
                                </address>
                                <contact>
                                    <email>
                                        <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:EmailAddress/ns1:EmailAddressText"/>
                                    </email>
                                    <phone>
                                        <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:Phone/ns1:PhoneNumber"/>
                                        <type>
                                            <xsl:value-of select="//ns1:ContactInfo[ns1:ContactInfoID = current()/ns1:ContactInfoRefID]/ns1:Phone/ns1:ContactTypeText"/>
                                        </type>
                                    </phone>
                                </contact>
                            </xsl:if>
                            <type>
                                <xsl:choose>
                                    <xsl:when test="ns1:Individual/ns1:GenderCode = 'M'">Male</xsl:when>
                                    <xsl:when test="ns1:Individual/ns1:GenderCode = 'F'">Female</xsl:when>
                                </xsl:choose>
                            </type>
                            <docRef>
                                <xsl:value-of select="ns1:IdentityDoc/ns1:IdentityDocID"/>
                                <issuer>
                                    <xsl:value-of select="ns1:IdentityDoc/ns1:IssuingCountryCode"/>
                                </issuer>
                                <nationality>
                                    <xsl:value-of select="ns1:IdentityDoc/ns1:CitizenshipCountryCode"/>
                                </nationality>
                                <type>
                                    <xsl:choose>
                                        <xsl:when test="ns1:IdentityDoc/ns1:IdentityDocTypeCode = 'PT'">P</xsl:when>
                                    </xsl:choose>
                                </type>
                                <expirationDate>
                                    <xsl:value-of select="ns1:IdentityDoc/ns1:ExpiryDate"/>
                                </expirationDate>
                                <dateOfBirth>
                                    <xsl:value-of select="ns1:IdentityDoc/ns1:Birthdate"/>
                                </dateOfBirth>
                            </docRef>
                            <DateOfBirth>
                                <xsl:value-of select="ns1:Individual/ns1:Birthdate"/>
                            </DateOfBirth>
                            <Name>
                                <FirstName>
                                    <xsl:value-of select="ns1:Individual/ns1:GivenName"/>
                                </FirstName>
                                <LastName>
                                    <xsl:value-of select="ns1:Individual/ns1:Surname"/>
                                </LastName>
                                <Title>
                                    <xsl:value-of select="ns1:Individual/ns1:TitleName"/>
                                </Title>
                            </Name>
                        </actor>
                    </xsl:for-each>
                    <!-- Additional mappings for 'set' and other elements needed -->
                </Request>
            </Requests>
        </AMA_ConnectivityLayerRS>
    </xsl:template>
</xsl:stylesheet>