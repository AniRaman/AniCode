<xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ns1="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage" xmlns:ns2="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes">
    <xsl:output method="xml" indent="yes"/>
    <xsl:param name="rloc" select="'L12345'"/>
    <xsl:param name="IATA_Number" select="'08206881'"/>
    <xsl:param name="TravelAgencyName" select="'ATravelAgencyName'"/>
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
                            <xsl:value-of select="//ns2:CorrelationID"/>
                        </correlationID>
                        <Retailer>
                            <code>VY</code>
                        </Retailer>
                    </Context>
                    <bookingSourceInfo>
                        <rloc>
                            <xsl:value-of select="$rloc"/>
                        </rloc>
                    </bookingSourceInfo>
                    <TravelAgency>
                        <IATA_Number>
                            <xsl:value-of select="$IATA_Number"/>
                        </IATA_Number>
                        <Name>
                            <xsl:value-of select="$TravelAgencyName"/>
                        </Name>
                    </TravelAgency>
                    <xsl:for-each select="//ns2:PaxList/ns2:Pax">
                        <actor>
                            <ID>
                                <xsl:value-of select="ns2:PaxID"/>
                            </ID>
                            <TID>
                                <xsl:value-of select="ns2:PaxID"/>
                            </TID>
                            <xsl:if test="ns2:ContactInfoRefID">
                                <address>
                                    <line>
                                        <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:PostalAddress/ns2:StreetText"/>
                                    </line>
                                    <zip>
                                        <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:PostalAddress/ns2:PostalCode"/>
                                    </zip>
                                    <cityName>
                                        <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:PostalAddress/ns2:CityName"/>
                                    </cityName>
                                    <stateName>
                                        <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:PostalAddress/ns2:CountrySubDivisionName"/>
                                    </stateName>
                                    <countryCode>
                                        <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:PostalAddress/ns2:CountryCode"/>
                                    </countryCode>
                                </address>
                                <contact>
                                    <email>
                                        <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:EmailAddress/ns2:EmailAddressText"/>
                                    </email>
                                    <phone>
                                        <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:Phone/ns2:PhoneNumber"/>
                                        <type>
                                            <xsl:value-of select="//ns2:ContactInfo[ns2:ContactInfoID = current()/ns2:ContactInfoRefID]/ns2:Phone/ns2:ContactTypeText"/>
                                        </type>
                                    </phone>
                                </contact>
                            </xsl:if>
                            <type>
                                <xsl:choose>
                                    <xsl:when test="ns2:Individual/ns2:GenderCode = 'M'">Male</xsl:when>
                                    <xsl:otherwise>Female</xsl:otherwise>
                                </xsl:choose>
                            </type>
                            <xsl:if test="ns2:IdentityDoc">
                                <docRef>
                                    <xsl:value-of select="ns2:IdentityDoc/ns2:IdentityDocID"/>
                                    <issuer>
                                        <xsl:value-of select="ns2:IdentityDoc/ns2:IssuingCountryCode"/>
                                    </issuer>
                                    <nationality>
                                        <xsl:value-of select="ns2:IdentityDoc/ns2:CitizenshipCountryCode"/>
                                    </nationality>
                                    <type>P</type>
                                    <expirationDate>
                                        <xsl:value-of select="ns2:IdentityDoc/ns2:ExpiryDate"/>
                                    </expirationDate>
                                    <dateOfBirth>
                                        <xsl:value-of select="ns2:IdentityDoc/ns2:Birthdate"/>
                                    </dateOfBirth>
                                </docRef>
                            </xsl:if>
                            <DateOfBirth>
                                <xsl:value-of select="ns2:Individual/ns2:Birthdate"/>
                            </DateOfBirth>
                            <Name>
                                <FirstName>
                                    <xsl:value-of select="ns2:Individual/ns2:GivenName"/>
                                </FirstName>
                                <LastName>
                                    <xsl:value-of select="ns2:Individual/ns2:Surname"/>
                                </LastName>
                                <Title>
                                    <xsl:value-of select="ns2:Individual/ns2:TitleName"/>
                                </Title>
                            </Name>
                        </actor>
                    </xsl:for-each>
                    <xsl:for-each select="//ns2:Order/ns2:OrderItem">
                        <set>
                            <ID>
                                <xsl:value-of select="../ns2:OrderID"/>
                            </ID>
                            <xsl:for-each select="ns2:FareDetail/ns2:PaxSegmentRefID">
                                <product>
                                    <ID>
                                        <xsl:value-of select="."/>
                                    </ID>
                                    <PaxJourneyID>
                                        <xsl:value-of select="//ns2:PaxJourneyList/ns2:PaxJourney[ns2:PaxSegmentRefID = current()]/ns2:PaxJourneyID"/>
                                    </PaxJourneyID>
                                    <EAI>
                                        <Data>
                                            <serviceProvider>
                                                <code>
                                                    <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:CarrierDesigCode"/>
                                                </code>
                                            </serviceProvider>
                                            <identifier>
                                                <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:MarketingCarrierFlightNumberText"/>
                                            </identifier>
                                            <partnerInfo>
                                                <serviceProvider>
                                                    <code>
                                                        <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:CarrierDesigCode"/>
                                                    </code>
                                                </serviceProvider>
                                                <identifier>
                                                    <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:MarketingCarrierFlightNumberText"/>
                                                </identifier>
                                            </partnerInfo>
                                            <start>
                                                <dateTime>
                                                    <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:Dep/ns2:AircraftScheduledDateTime"/>
                                                </dateTime>
                                                <locationCode>
                                                    <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:Dep/ns2:IATA_LocationCode"/>
                                                </locationCode>
                                            </start>
                                            <end>
                                                <dateTime>
                                                    <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:Arrival/ns2:AircraftScheduledDateTime"/>
                                                </dateTime>
                                                <locationCode>
                                                    <xsl:value-of select="//ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:Arrival/ns2:IATA_LocationCode"/>
                                                </locationCode>
                                            </end>
                                            <vehicle>
                                                <code>
                                                    <xsl:value-of select="//ns2:DatedOperatingLegList/ns2:DatedOperatingLeg[ns2:DatedOperatingLegID = //ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:DatedOperatingSegmentRefId]/ns2:CarrierAircraftType/ns2:CarrierAircraftTypeCode"/>
                                                </code>
                                            </vehicle>
                                            <duration>
                                                <xsl:value-of select="//ns2:DatedOperatingSegmentList/ns2:DatedOperatingSegment[ns2:DatedOperatingSegmentId = //ns2:DatedMarketingSegmentList/ns2:DatedMarketingSegment[ns2:DatedMarketingSegmentId = current()]/ns2:DatedOperatingSegmentRefId]/ns2:Duration"/>
                                            </duration>
                                            <externalSystem>
                                                <xsl:for-each select="../ns2:OrderItemID">
                                                    <bkgReference>
                                                        <Owner>VY</Owner>
                                                        <Number>
                                                            <xsl:value-of select="."/>
                                                        </Number>
                                                        <additionalInformation>OrderItemID</additionalInformation>
                                                    </bkgReference>
                                                </xsl:for-each>
                                                <bkgReference>
                                                    <Owner>VY</Owner>
                                                    <Number>
                                                        <xsl:value-of select="../ns2:OrderID"/>
                                                    </Number>
                                                    <additionalInformation>OrderID</additionalInformation>
                                                </bkgReference>
                                                <bkgReference>
                                                    <Owner>VY</Owner>
                                                    <Number>
                                                        <xsl:value-of select="../ns2:OrderID"/>
                                                    </Number>
                                                    <additionalInformation>Airline Recloc</additionalInformation>
                                                </bkgReference>
                                            </externalSystem>
                                            <status>
                                                <xsl:choose>
                                                    <xsl:when test="../ns2:StatusCode = 'Active'">HK</xsl:when>
                                                    <xsl:otherwise>HN</xsl:otherwise>
                                                </xsl:choose>
                                            </status>
                                            <bkgClass>
                                                <xsl:value-of select="ns2:FareComponent/ns2:RBD/ns2:RBD_Code"/>
                                            </bkgClass>
                                            <NIP>3</NIP>
                                            <cabin>
                                                Economy
                                                <bkgClass>M</bkgClass>
                                            </cabin>
                                        </Data>
                                        <links>
                                            <xsl:for-each select="ns2:PaxRefID">
                                                <xsl:value-of select="."/>
                                                <xsl:text> </xsl:text>
                                            </xsl:for-each>
                                        </links>
                                    </EAI>
                                    <type>EAI</type>
                                </product>
                            </xsl:for-each>
                            <xsl:for-each select="ns2:Service">
                                <ExternalContext>
                                    <ID>
                                        <xsl:value-of select="concat('EXT', position())"/>
                                    </ID>
                                    <reference>
                                        <xsl:value-of select="ns2:ServiceID"/>
                                    </reference>
                                    <type>OrderItem</type>
                                    <links>
                                        <xsl:value-of select="ns2:PaxRefID"/>
                                    </links>
                                </ExternalContext>
                            </xsl:for-each>
                            <formOfPayment>
                                <Data>
                                    <Payment>
                                        <PaymentInfo>
                                            <Transaction>
                                                <PaymentStatus>
                                                    <xsl:value-of select="//ns2:PaymentProcessingSummary/ns2:PaymentStatusCode"/>
                                                </PaymentStatus>
                                                <Value>
                                                    <CurrencyCode>
                                                        <xsl:value-of select="//ns2:PaymentProcessingSummary/ns2:Amount/@CurCode"/>
                                                    </CurrencyCode>
                                                    <Amount>
                                                        <xsl:value-of select="//ns2:PaymentProcessingSummary/ns2:Amount"/>
                                                    </Amount>
                                                </Value>
                                            </Transaction>
                                        </PaymentInfo>
                                        <MethodOfPayment>
                                            <Code>
                                                <xsl:value-of select="//ns2:PaymentSupportedMethod/ns2:PaymentTypeCode"/>
                                            </Code>
                                            <Card>
                                                <PrimaryAccountNumber>
                                                    <xsl:value-of select="//ns2:PaymentProcessingSummary/ns2:PaymentProcessingSummaryPaymentMethod/ns2:PaymentCard/ns2:MaskedCardID"/>
                                                </PrimaryAccountNumber>
                                                <Vendor>
                                                    <Code>
                                                        <xsl:value-of select="//ns2:PaymentProcessingSummary/ns2:PaymentProcessingSummaryPaymentMethod/ns2:PaymentCard/ns2:CardBrandCode"/>
                                                    </Code>
                                                </Vendor>
                                            </Card>
                                        </MethodOfPayment>
                                    </Payment>
                                </Data>
                            </formOfPayment>
                            <timeLimit>
                                <paymentTimeLimit>
                                    <xsl:value-of select="substring-before(ns2:PaymentTimeLimitDateTime, 'Z')"/>
                                </paymentTimeLimit>
                                <RefIDs>
                                    <xsl:for-each select="ns2:FareDetail/ns2:PaxSegmentRefID">
                                        <xsl:value-of select="."/>
                                        <xsl:text> </xsl:text>
                                    </xsl:for-each>
                                </RefIDs>
                            </timeLimit>
                        </set>
                    </xsl:for-each>
                </Request>
            </Requests>
        </AMA_ConnectivityLayerRS>
    </xsl:template>
</xsl:stylesheet>