<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" encoding="UTF-8" indent="yes"/>
    <xsl:template match="/">
        <OrderCreateRQ Version="17.2">
            <xsl:if test="Request/Context/correlationID">
                <xsl:attribute name="CorrelationID">
                    <xsl:value-of select="Request/Context/correlationID"/>
                </xsl:attribute>
                <xsl:attribute name="TransactionIdentifier">
                    <xsl:value-of select="Request/Context/correlationID"/>
                </xsl:attribute>
            </xsl:if>
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
                        <Name>
                            <xsl:value-of select="Request/TravelAgency/Name"/>
                        </Name>
                        <Contacts>
                            <Contact>
                                <AddressContact>
                                    <Street>
                                        <xsl:value-of select="Request/TravelAgency/Contact/Address/line[1]"/>
                                    </Street>
                                    <Street>
                                        <xsl:value-of select="Request/TravelAgency/Contact/Address/line[2]"/>
                                    </Street>
                                    <CityName>
                                        <xsl:value-of select="Request/TravelAgency/Contact/Address/CityName"/>
                                    </CityName>
                                    <CountryCode>
                                        <xsl:value-of select="Request/TravelAgency/Contact/Address/CountryCode"/>
                                    </CountryCode>
                                </AddressContact>
                                <EmailContact>
                                    <Address>
                                        <xsl:value-of select="Request/TravelAgency/Contact/Email/EmailAddress"/>
                                    </Address>
                                </EmailContact>
                                <PhoneContact>
                                <!--Manual change start-->
                                    <Number>
                                        <xsl:value-of select="translate(Request/TravelAgency/Contact/Phone/PhoneNumber, concat(' `~!@#$%^&amp;*()-_=+[]{}|\:;./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;', &quot;'&quot;), '')"/>
                                    </Number>
                                <!--Manual change end-->
                                </PhoneContact>
                            </Contact>
                        </Contacts>
                        <PseudoCity>AH9D</PseudoCity>
                        <IATA_Number>
                            <xsl:value-of select="Request/TravelAgency/IATA_Number"/>
                        </IATA_Number>
                        <AgencyID>
                            <xsl:value-of select="Request/TravelAgency/IATA_Number"/>
                        </AgencyID>
                        <AgentUser>
                            <AgentUserID>xmluser001</AgentUserID>
                        </AgentUser>
                    </TravelAgencySender>
                </Sender>
            </Party>
            <Query>
                <Order>
                    <Offer>
                        <xsl:attribute name="OfferID">
                            <xsl:value-of select="Request/set/ID"/>
                        </xsl:attribute>
                        <xsl:attribute name="Owner">
                            <xsl:value-of select="Request/set/property/value"/>
                        </xsl:attribute>
                        <xsl:attribute name="ResponseID">
                            <xsl:value-of select="Request/set/TID"/>
                        </xsl:attribute>
                        <OfferItem>
                            <xsl:attribute name="OfferItemID">
                                <xsl:value-of select="Request/set/product/ID"/>
                            </xsl:attribute>
                            <PassengerRefs>
                                <xsl:value-of select="Request/set/product/RefIDs"/>
                            </PassengerRefs>
                        </OfferItem>
                    </Offer>
                </Order>
                <Payments>
                    <Payment>
                        <Method>
                            <Cash CashInd="true"/>
                        </Method>
                        <Amount>0.00</Amount>
                    </Payment>
                </Payments>
                <DataLists>
                    <PassengerList>
                        <Passenger>
                            <xsl:attribute name="PassengerID">
                                <xsl:value-of select="Request/actor/ID"/>
                            </xsl:attribute>
                            <PTC>
                                <xsl:value-of select="Request/actor/PTC"/>
                            </PTC>
                            <Individual>
                                <Birthdate>
                                    <xsl:value-of select="Request/actor/DateOfBirth"/>
                                </Birthdate>
                                <Gender>
                                    <xsl:value-of select="Request/actor/Name/Type"/>
                                </Gender>
                                <NameTitle>
                                    <xsl:value-of select="Request/actor/Name/Title"/>
                                </NameTitle>
                                <GivenName>
                                    <xsl:value-of select="Request/actor/Name/FirstName"/>
                                </GivenName>
                                <Surname>
                                    <xsl:value-of select="Request/actor/Name/LastName"/>
                                </Surname>
                            </Individual>
                        </Passenger>
                    </PassengerList>
                </DataLists>
            </Query>
        </OrderCreateRQ>
    </xsl:template>
</xsl:stylesheet>