<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="http://www.iata.org/IATA/2015/00/2018.2/IATA_OrderCreateRQ"
    xmlns:ns2="http://www.iata.org/IATA/2015/EASD/00/PassengerSalesTaxRegistration" version="1.0">
    <xsl:output method="xml" indent="yes"/>
    <xsl:template match="/">
        <IATA_OrderCreateRQ>
            <Party>
                <Participant>
                    <Aggregator>
                        <AggregatorID>1A</AggregatorID>
                        <Name>Amadeus</Name>
                    </Aggregator>
                </Participant>
                <Recipient>
                    <ORA>
                        <AirlineDesigCode>
                            <xsl:value-of select="AMA_ConnectivityLayerRQ/Requests/Request/target"/>
                        </AirlineDesigCode>
                    </ORA>
                </Recipient>
                <Sender>
                    <TravelAgency>
                        <AgencyID>87654324</AgencyID>
                        <ContactInfoRefID>CIPAX</ContactInfoRefID>
                        <IATANumber>87654324</IATANumber>
                        <Name>AMADEUS PRODUCT PLANNING</Name>
                        <PseudoCityID>AMS</PseudoCityID>
                    </TravelAgency>
                </Sender>
            </Party>
            <PayloadAttributes>
                <CorrelationID>
                    <xsl:value-of select="AMA_ConnectivityLayerRQ/Requests/Request/Context/correlationID"/>
                </CorrelationID>
                <VersionNumber>18.2</VersionNumber>
            </PayloadAttributes>
            <Request>
                <CreateOrder>
                    <SelectedOffer>
                        <OfferRefID>
                            <xsl:value-of select="AMA_ConnectivityLayerRQ/Requests/Request/set/ID"/>
                        </OfferRefID>
                        <OwnerCode>
                            <xsl:value-of select="AMA_ConnectivityLayerRQ/Requests/Request/set/property/value"/>
                        </OwnerCode>
                        <xsl:for-each select="AMA_ConnectivityLayerRQ/Requests/Request/set/product">
                            <SelectedOfferItem>
                                <OfferItemRefID>
                                    <xsl:value-of select="ID"/>
                                </OfferItemRefID>
                                <xsl:for-each select="RefIDs">
                                    <xsl:variable name="refIDs" select="."/>
                                    <xsl:for-each select="tokenize($refIDs, ' ')">
                                        <PaxRefID>
                                            <xsl:choose>
                                                <xsl:when test=". = 'T1'">PAX1</xsl:when>
                                                <xsl:when test=". = 'T2'">PAX3</xsl:when>
                                                <xsl:when test=". = 'T3'">PAX2</xsl:when>
                                                <xsl:when test=". = 'T4'">PAX4</xsl:when>
                                                <xsl:when test=". = 'T5'">PAX5</xsl:when>
                                                <xsl:when test=". = 'T6'">PAX6</xsl:when>
                                                <xsl:when test=". = 'T7'">PAX7</xsl:when>
                                            </xsl:choose>
                                        </PaxRefID>
                                    </xsl:for-each>
                                </xsl:for-each>
                            </SelectedOfferItem>
                        </xsl:for-each>
                        <ShoppingResponseRefID>
                            <xsl:value-of select="AMA_ConnectivityLayerRQ/Requests/Request/set/TID"/>
                        </ShoppingResponseRefID>
                    </SelectedOffer>
                </CreateOrder>
                <DataLists>
                    <ContactInfoList>
                        <ContactInfo>
                            <ContactInfoID>CIPAX</ContactInfoID>
                            <EmailAddress>
                                <EmailAddressText>NONE</EmailAddressText>
                            </EmailAddress>
                            <Phone>
                                <PhoneNumber>33492943273</PhoneNumber>
                            </Phone>
                        </ContactInfo>
                        <xsl:for-each select="AMA_ConnectivityLayerRQ/Requests/Request/actor">
                            <ContactInfo>
                                <xsl:variable name="actorID" select="ID"/>
                                <xsl:choose>
                                    <xsl:when test="$actorID = 'T1'">
                                        <ContactInfoID>CIPAX1</ContactInfoID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T2'">
                                        <ContactInfoID>CIPAX3</ContactInfoID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T3'">
                                        <ContactInfoID>CIPAX2</ContactInfoID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T4'">
                                        <ContactInfoID>CIPAX4</ContactInfoID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T5'">
                                        <ContactInfoID>CIPAX5</ContactInfoID>
                                    </xsl:when>
                                </xsl:choose>
                                <EmailAddress>
                                    <EmailAddressText>
                                        <xsl:value-of select="contact/email"/>
                                    </EmailAddressText>
                                    <LabelText>
                                        <xsl:value-of select="contact/email/label"/>
                                    </LabelText>
                                </EmailAddress>
                            </ContactInfo>
                        </xsl:for-each>
                    </ContactInfoList>
                    <PaxList>
                        <xsl:for-each select="AMA_ConnectivityLayerRQ/Requests/Request/actor">
                            <Pax>
                                <xsl:variable name="actorID" select="ID"/>
                                <xsl:choose>
                                    <xsl:when test="$actorID = 'T1'">
                                        <ContactInfoRefID>CIPAX1</ContactInfoRefID>
                                        <IndividualID>PAX1</IndividualID>
                                        <PaxID>PAX1</PaxID>
                                        <PaxRefID>PAX7</PaxRefID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T2'">
                                        <ContactInfoRefID>CIPAX3</ContactInfoRefID>
                                        <IndividualID>PAX3</IndividualID>
                                        <PaxID>PAX3</PaxID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T3'">
                                        <ContactInfoRefID>CIPAX2</ContactInfoRefID>
                                        <IndividualID>PAX2</IndividualID>
                                        <PaxID>PAX2</PaxID>
                                        <PaxRefID>PAX6</PaxRefID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T4'">
                                        <ContactInfoRefID>CIPAX4</ContactInfoRefID>
                                        <IndividualID>PAX4</IndividualID>
                                        <PaxID>PAX4</PaxID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T5'">
                                        <ContactInfoRefID>CIPAX5</ContactInfoRefID>
                                        <IndividualID>PAX5</IndividualID>
                                        <PaxID>PAX5</PaxID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T6'">
                                        <IndividualID>PAX7</IndividualID>
                                        <PaxID>PAX7</PaxID>
                                    </xsl:when>
                                    <xsl:when test="$actorID = 'T7'">
                                        <IndividualID>PAX6</IndividualID>
                                        <PaxID>PAX6</PaxID>
                                    </xsl:when>
                                </xsl:choose>
                                <Individual>
                                    <Birthdate>
                                        <xsl:value-of select="DateOfBirth"/>
                                    </Birthdate>
                                    <GenderCode>
                                        <xsl:choose>
                                            <xsl:when test="Name/Type = 'Male'">M</xsl:when>
                                            <xsl:otherwise>F</xsl:otherwise>
                                        </xsl:choose>
                                    </GenderCode>
                                    <GivenName>
                                        <xsl:value-of select="Name/FirstName"/>
                                    </GivenName>
                                    <Surname>
                                        <xsl:value-of select="Name/LastName"/>
                                    </Surname>
                                </Individual>
                                <PTC>
                                    <xsl:value-of select="PTC"/>
                                </PTC>
                            </Pax>
                        </xsl:for-each>
                    </PaxList>
                </DataLists>
            </Request>
        </IATA_OrderCreateRQ>
    </xsl:template>
</xsl:stylesheet>