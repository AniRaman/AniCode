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
                                    <Number>
                                        <xsl:value-of select="translate(Request/TravelAgency/Contact/Phone/PhoneNumber, concat(' `~!@#$%^&amp;*()-_=+[]{}|\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')"/>
                                    </Number>
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
                            <ResidenceCountryCode>
                                <xsl:value-of select="Request/address/CountryCode"/>
                            </ResidenceCountryCode>
                            <CitizenshipCountryCode>
                                <xsl:value-of select="Request/actor/nationality/code"/>
                            </CitizenshipCountryCode>
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
                            <LoyaltyProgramAccount>
                                <Airline>
                                    <AirlineDesignator>
                                        <xsl:value-of select="Request/actor/loyalty/companyCode"/>
                                    </AirlineDesignator>
                                </Airline>
                                <AccountNumber>
                                    <xsl:value-of select="Request/actor/loyalty/identifier"/>
                                </AccountNumber>
                            </LoyaltyProgramAccount>
                            <!-- IdentityDocument creation based on conditions -->
                            <xsl:if test="not(Request/actor/docRef/taxIdentifier) and Request/actor/docRef/type">
                                <IdentityDocument>
                                    <IdentityDocumentNumber>
                                      <xsl:value-of select="Request/actor/docRef"/>
                                    </IdentityDocumentNumber>
                                    <xsl:if test="Request/actor/docRef/type = 'P'">
                                        <IdentityDocumentType>PT</IdentityDocumentType>
                                    </xsl:if>
                                    <IssuingCountryCode>
                                        <xsl:value-of select="Request/actor/docRef/issuer"/>
                                    </IssuingCountryCode>
                                    <CitizenshipCountryCode>
                                        <xsl:value-of select="Request/actor/docRef/nationality"/>
                                    </CitizenshipCountryCode>
                                    <IssueDate>
                                        <xsl:value-of select="Request/actor/docRef/issuanceDate"/>
                                    </IssueDate>
                                    <ExpiryDate>
                                        <xsl:value-of select="Request/actor/docRef/expirationDate"/>
                                    </ExpiryDate>
                                    <Gender>
                                        <xsl:value-of select="Request/actor/Name/Type"/>
                                    </Gender>
                                    <Birthdate>
                                        <xsl:value-of select="Request/actor/docRef/dateOfBirth"/>
                                    </Birthdate>
                                </IdentityDocument>
                            </xsl:if>
                            <xsl:if test="Request/target != 'UA' and Request/target != 'UAD'">
                                <IdentityDocument>
                                    <IdentityDocumentNumber>
                                        <xsl:value-of select="Request/actor/docRef/type"/>
                                    </IdentityDocumentNumber>
                                </IdentityDocument>
                            </xsl:if>
                            <xsl:if test="Request/actor/redress">
                                <IdentityDocument>
                                    <IdentityDocumentNumber>
                                        <xsl:value-of select="Request/actor/redress"/>
                                    </IdentityDocumentNumber>
                                </IdentityDocument>
                            </xsl:if>
                            <xsl:if test="(Request/target = 'UA' or Request/target = 'UAD') and Request/actor/docRef/visa/type = 'R'">
                                <IdentityDocument>
                                    <IdentityDocumentNumber>
                                        <xsl:value-of select="Request/actor/docRef/visa"/>
                                    </IdentityDocumentNumber>
                                </IdentityDocument>
                            </xsl:if>
                            <xsl:if test="(Request/target = 'UA' or Request/target = 'UAD') and Request/actor/docRef/visa/type = 'K'">
                                <IdentityDocument>
                                    <IdentityDocumentNumber>
                                        <xsl:value-of select="Request/actor/docRef/visa"/>
                                    </IdentityDocumentNumber>
                                </IdentityDocument>
                            </xsl:if>
                        </Passenger>
                    </PassengerList>
                    <ContactList>
                        <ContactInformation>
                            <xsl:attribute name="ContactID">
                                <xsl:value-of select="concat('CI', position(), Request/id)"/>
                            </xsl:attribute>
                            <PostalAddress>
                                <xsl:if test="Request/actor/contact/contactType = 'CTC'">
                                    <Label>
                                        <xsl:value-of select="Request/actor/contact/phone/label"/>
                                    </Label>
                                </xsl:if>
                                <Street>
                                    <xsl:value-of select="Request/actor/contact/phone"/>
                                </Street>
                                <PostalCode>
                                    <xsl:value-of select="Request/actor/contact/phone"/>
                                </PostalCode>
                                <CityName>
                                    <xsl:value-of select="Request/actor/contact/phone"/>
                                </CityName>
                                <xsl:if test="Request/actor/address/stateName">
                                    <CountrySubdivisionName>
                                        <xsl:value-of select="Request/actor/address/stateName"/>
                                    </CountrySubdivisionName>
                                </xsl:if>
                                <xsl:if test="Request/actor/address/countryCode">
                                    <CountryCode>
                                        <xsl:value-of select="Request/actor/address/countryCode"/>
                                    </CountryCode>
                                </xsl:if>
                            </PostalAddress>
                            <xsl:if test="Request/actor/contact/contactType">
                                <ContactType>
                                    <xsl:value-of select="Request/actor/contact/contactType"/>
                                </ContactType>
                            </xsl:if>
                            <xsl:if test="Request/actor/contact">
                                <ContactProvided>
                                    <xsl:if test="Request/actor/contact/phone/label">
                                        <Phone>
                                            <Label>
                                                <xsl:value-of select="Request/actor/contact/phone/label"/>
                                            </Label>
                                            <PhoneNumber>
                                                <xsl:value-of select="translate(Request/actor/contact/phone, concat(' `~!@#$%^&amp;*()-_=+[]{}|\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')"/>
                                            </PhoneNumber>
                                        </Phone>
                                    </xsl:if>
                                    <xsl:if test="Request/actor/contact/email">
                                        <EmailAddress>
                                            <Label>
                                                <xsl:value-of select="Request/actor/contact/email/label"/>
                                            </Label>
                                            <EmailAddressValue>
                                                <xsl:value-of select="Request/actor/contact/email"/>
                                            </EmailAddressValue>
                                        </EmailAddress>
                                    </xsl:if>
                                </ContactProvided>
                            </xsl:if>
                            <xsl:if test="Request/actor/contact/ContactRefusedInd = 'true'">
                                <ContactNotProvided/>
                            </xsl:if>
                        </ContactInformation>
                    </ContactList>
                </DataLists>
            </Query>
        </OrderCreateRQ>
    </xsl:template>
</xsl:stylesheet>