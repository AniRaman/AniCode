<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tbf="http://www.altova.com/MapForce/UDF/tbf" xmlns:vmf="http://www.altova.com/MapForce/UDF/vmf" xmlns:ns0="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes" xmlns:ns1="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage" xmlns:xs="http://www.w3.org/2001/XMLSchema" version="1.0" exclude-result-prefixes="tbf vmf ns0 ns1 xs">
	<xsl:template name="tbf:tbf1_MeasureType">
		<xsl:param name="input" select="/.."/>
		<xsl:attribute name="UnitCode">
			<xsl:value-of select="$input/@*[name()='UnitCode']"/>
		</xsl:attribute>
		<xsl:value-of select="$input"/>
	</xsl:template>
	<xsl:template name="tbf:tbf2_AmountType">
		<xsl:param name="input" select="/.."/>
		<xsl:attribute name="UnitCode">
			<xsl:value-of select="$input/@*[name()='UnitCode']"/>
		</xsl:attribute>
		<xsl:value-of select="$input"/>
	</xsl:template>
	<!-- Manual Change : START -->
	<xsl:template match="text()" name="getPaxRef">
		<xsl:param name="inputStr"/>
		<xsl:value-of select="/ns1:IATA_OrderViewRS/ns1:Response/ns0:DataLists/ns0:PaxList/ns0:Pax[$inputStr = ns0:PaxRefID]/ns0:PaxID"/>
	</xsl:template>
	<!-- Manual Change : END -->
	<xsl:template name="vmf:vmf1_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="concat(substring('VKilogram',1,string-length('VKilogram')*($input='KGM')),substring('VUS Pounds',1,string-length('VUS Pounds')*($input='LBR')))"/>
	</xsl:template>
	<xsl:template name="vmf:vmf2_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='NTF' or $input='700' or $input='703'">
				<xsl:value-of select="'NOTIFICATION'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$input"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf3_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="concat(substring('VKilogram',1,string-length('VKilogram')*($input='KGM')),substring('VUS Pounds',1,string-length('VUS Pounds')*($input='LBR')))"/>
	</xsl:template>
	<xsl:template name="vmf:vmf4_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="concat(substring('VKilogram',1,string-length('VKilogram')*($input='KGM')),substring('VUS Pounds',1,string-length('VUS Pounds')*($input='LBR')))"/>
	</xsl:template>
	<xsl:template name="vmf:vmf5_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="concat(substring('VKilogram',1,string-length('VKilogram')*($input='KGM')),substring('VUS Pounds',1,string-length('VUS Pounds')*($input='LBR')))"/>
	</xsl:template>
	<xsl:template name="vmf:vmf6_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="concat(substring('VKilogram',1,string-length('VKilogram')*($input='KGM')),substring('VUS Pounds',1,string-length('VUS Pounds')*($input='LBR')))"/>
	</xsl:template>
	<xsl:template name="vmf:vmf7_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="concat(substring('VKilogram',1,string-length('VKilogram')*($input='KGM')),substring('VUS Pounds',1,string-length('VUS Pounds')*($input='LBR')))"/>
	</xsl:template>
	<xsl:template name="vmf:vmf8_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input=('1','2','3','4','5')">
				<xsl:value-of select="substring('VFVCVYVWVM', string-length(substring-before('12345',$input))*2+1,2)"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="''"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf9_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='REQUESTED'">HN</xsl:when>
			<xsl:when test="$input='WAITLISTED'">HL</xsl:when>
			<xsl:when test="$input='CONFIRMED'">HK</xsl:when>
			<xsl:when test="$input='CANCELLED'">UN</xsl:when>
			<xsl:otherwise>
				<!-- Manual Change: remove xs:string() -->
				<xsl:value-of select="$input"/>
				<!-- Manual Change: remove xs:string() END-->
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<AMA_TravelOrderViewRS xmlns="http://xml.amadeus.com/2010/06/Travel_OrderViewRS_v1">
			<PayloadAttributes>
				<xsl:for-each select="ns1:IATA_OrderViewRS/ns1:PayloadAttributes/ns0:VersionNumber">
					<Version>
						<xsl:value-of select="number(.)"/>
					</Version>
				</xsl:for-each>
				<xsl:for-each select="ns1:IATA_OrderViewRS/ns1:PayloadAttributes/ns0:CorrelationID">
					<CorrelationID>
						<xsl:value-of select="."/>
					</CorrelationID>
				</xsl:for-each>
			</PayloadAttributes>
			<xsl:for-each select="ns1:IATA_OrderViewRS">
				<xsl:for-each select="ns1:Response">
					<Response>
						<DataLists>
							<xsl:for-each select="ns0:DataLists/ns0:BaggageAllowanceList">
								<BaggageAllowanceList>
									<xsl:for-each select="ns0:BaggageAllowance">
										<BaggageAllowance>
											<BaggageAllowanceID>
												<xsl:value-of select="ns0:BaggageAllowanceID"/>
											</BaggageAllowanceID>
											<TypeCode>
												<xsl:value-of select="ns0:TypeCode"/>
											</TypeCode>
											<xsl:for-each select="ns0:WeightAllowance">
												<xsl:variable name="var9_nested">
													<xsl:value-of select="number(boolean(ns0:TotalMaximumWeightMeasure))"/>
													<xsl:value-of select="number(boolean(ns0:MaximumWeightMeasure))"/>
												</xsl:variable>
												<xsl:if test="boolean(translate(normalize-space($var9_nested), ' 0', ''))">
													<WeightAllowance>
														<xsl:choose>
															<xsl:when test="ns0:TotalMaximumWeightMeasure">
																<xsl:for-each select="ns0:TotalMaximumWeightMeasure">
																	<MaximumWeightMeasure>
																		<xsl:variable name="var11_nested">
																			<xsl:call-template name="vmf:vmf1_inputtoresult">
																				<xsl:with-param name="input" select="string($var8_filter/ns0:WeightUnitOfMeasurement)"/>
																			</xsl:call-template>
																		</xsl:variable>
																		<xsl:if test="string($var11_nested)">
																			<xsl:attribute name="UnitCode" namespace="">
																				<xsl:variable name="var12_nested">
																					<xsl:call-template name="vmf:vmf1_inputtoresult">
																						<xsl:with-param name="input" select="string($var8_filter/ns0:WeightUnitOfMeasurement)"/>
																					</xsl:call-template>
																				</xsl:variable>
																				<xsl:value-of select="substring($var12_nested, 2)"/>
																			</xsl:attribute>
																		</xsl:if>
																		<xsl:value-of select="number(.)"/>
																	</MaximumWeightMeasure>
																</xsl:for-each>
															</xsl:when>
															<xsl:when test="ns0:MaximumWeightMeasure">
																<xsl:for-each select="ns0:MaximumWeightMeasure">
																	<MaximumWeightMeasure>
																		<xsl:variable name="var14_nested">
																			<xsl:call-template name="vmf:vmf1_inputtoresult">
																				<xsl:with-param name="input" select="string($var8_filter/ns0:WeightUnitOfMeasurement)"/>
																			</xsl:call-template>
																		</xsl:variable>
																		<xsl:if test="string($var14_nested)">
																			<xsl:attribute name="UnitCode" namespace="">
																				<xsl:variable name="var15_nested">
																					<xsl:call-template name="vmf:vmf1_inputtoresult">
																						<xsl:with-param name="input" select="string($var8_filter/ns0:WeightUnitOfMeasurement)"/>
																					</xsl:call-template>
																				</xsl:variable>
																				<xsl:value-of select="substring($var15_nested, 2)"/>
																			</xsl:attribute>
																		</xsl:if>
																		<xsl:value-of select="number(.)"/>
																	</MaximumWeightMeasure>
																</xsl:for-each>
															</xsl:when>
														</xsl:choose>
														<xsl:for-each select="$var7_cur/ns0:ApplicablePartyText">
															<ApplicablePartyText>
																<xsl:value-of select="."/>
															</ApplicablePartyText>
														</xsl:for-each>
													</WeightAllowance>
												</xsl:if>
											</xsl:for-each>
											<xsl:for-each select="ns0:PieceAllowance">
												<PieceAllowance>
													<xsl:for-each select="$var7_cur/ns0:ApplicablePartyText">
														<ApplicablePartyText>
															<xsl:value-of select="."/>
														</ApplicablePartyText>
													</xsl:for-each>
													<TotalQty>
														<xsl:value-of select="number(ns0:TotalQty)"/>
													</TotalQty>
												</PieceAllowance>
											</xsl:for-each>
										</BaggageAllowance>
									</xsl:for-each>
								</BaggageAllowanceList>
							</xsl:for-each>
							<xsl:for-each select="ns0:DataLists/ns0:ContactInfoList">
								<ContactInfoList>
									<xsl:for-each select="ns0:ContactInfo">
										<ContactInfo>
											<ContactInfoID>
												<xsl:value-of select="ns0:ContactInfoID"/>
											</ContactInfoID>
											<xsl:for-each select="ns0:ContactPurposeText">
												<ContactTypeText>
													<xsl:variable name="var22_nested">
														<xsl:call-template name="vmf:vmf2_inputtoresult">
															<xsl:with-param name="input" select="string(.)"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="$var22_nested"/>
												</ContactTypeText>
											</xsl:for-each>
											<xsl:for-each select="ns0:IndividualRefID">
												<IndividualRef>
													<xsl:value-of select="."/>
												</IndividualRef>
											</xsl:for-each>
											<xsl:for-each select="ns0:Phone">
												<Phone>
													<xsl:if test="(true() and boolean($var20_cur/ns0:IndividualRefID))">
														<LabelText>
															<xsl:value-of select="'MOBILE'"/>
														</LabelText>
													</xsl:if>
													<xsl:for-each select="ns0:AreaCodeNumber">
														<AreaCodeNumber>
															<xsl:value-of select="number(.)"/>
														</AreaCodeNumber>
													</xsl:for-each>
													<xsl:choose>
														<xsl:when test="ns0:CountryDialingCode">
															<xsl:for-each select="ns0:CountryDialingCode">
																<xsl:for-each select="$var24_cur/ns0:PhoneNumber">
																	<PhoneNumber>
																		<!--Manual change-->
																		<xsl:value-of select="concat($var26_cur, .)"/>
																	</PhoneNumber>
																</xsl:for-each>
															</xsl:for-each>
														</xsl:when>
														<xsl:otherwise>
															<xsl:for-each select="ns0:PhoneNumber">
																<PhoneNumber>
																	<!--Manual change-->
																	<xsl:value-of select="."/>
																</PhoneNumber>
															</xsl:for-each>
														</xsl:otherwise>
													</xsl:choose>
													<xsl:for-each select="ns0:ExtensionNumber">
														<ExtensionNumber>
															<xsl:value-of select="number(.)"/>
														</ExtensionNumber>
													</xsl:for-each>
												</Phone>
											</xsl:for-each>
											<xsl:for-each select="ns0:OtherAddress">
												<OtherAddress>
													<OtherAddressText>
														<xsl:value-of select="ns0:OtherAddressText"/>
													</OtherAddressText>
												</OtherAddress>
											</xsl:for-each>
											<xsl:for-each select="ns0:EmailAddress">
												<EmailAddress>
													<xsl:if test="(true() and boolean($var20_cur/ns0:IndividualRefID))">
														<LabelText>
															<xsl:value-of select="'EMAIL'"/>
														</LabelText>
													</xsl:if>
													<EmailAddressText>
														<xsl:value-of select="ns0:EmailAddressText"/>
													</EmailAddressText>
												</EmailAddress>
											</xsl:for-each>
											<xsl:for-each select="ns0:PostalAddress">
												<xsl:if test="($var20_cur/ns0:ContactPurposeText)[(. = '700')]">
													<PostalAddress>
														<LabelText>
															<xsl:value-of select="'AddressAtOrigin'"/>
														</LabelText>
														<xsl:for-each select="ns0:StreetText">
															<StreetText>
																<xsl:value-of select="."/>
															</StreetText>
														</xsl:for-each>
														<xsl:for-each select="ns0:PO_BoxCode">
															<PO_BoxCode>
																<xsl:value-of select="."/>
															</PO_BoxCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:PostalCode">
															<PostalCode>
																<xsl:value-of select="."/>
															</PostalCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:CityName">
															<CityName>
																<xsl:value-of select="."/>
															</CityName>
														</xsl:for-each>
														<xsl:for-each select="ns0:CountryCode">
															<CountryCode>
																<xsl:value-of select="."/>
															</CountryCode>
														</xsl:for-each>
													</PostalAddress>
												</xsl:if>
											</xsl:for-each>
											<xsl:for-each select="ns0:PostalAddress">
												<xsl:if test="($var20_cur/ns0:ContactPurposeText)[(. = '703')]">
													<PostalAddress>
														<LabelText>
															<xsl:value-of select="'AddressAtDestination'"/>
														</LabelText>
														<xsl:for-each select="ns0:StreetText">
															<StreetText>
																<xsl:value-of select="."/>
															</StreetText>
														</xsl:for-each>
														<xsl:for-each select="ns0:PO_BoxCode">
															<PO_BoxCode>
																<xsl:value-of select="."/>
															</PO_BoxCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:PostalCode">
															<PostalCode>
																<xsl:value-of select="."/>
															</PostalCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:CityName">
															<CityName>
																<xsl:value-of select="."/>
															</CityName>
														</xsl:for-each>
														<xsl:for-each select="ns0:CountryCode">
															<CountryCode>
																<xsl:value-of select="."/>
															</CountryCode>
														</xsl:for-each>
													</PostalAddress>
												</xsl:if>
											</xsl:for-each>
										</ContactInfo>
									</xsl:for-each>
								</ContactInfoList>
							</xsl:for-each>
							<FareList/>
							<xsl:for-each select="ns0:DataLists">
								<xsl:for-each select="ns0:PaxJourneyList">
									<OriginDestList>
										<xsl:for-each select="ns0:PaxJourney">
											<xsl:variable name="var47_idx" select="position()"/>
											<OriginDest>
												<OriginDestID>
													<xsl:value-of select="concat('OD', position())"/>
												</OriginDestID>
												<xsl:for-each select="$var44_cur/ns0:DatedMarketingSegmentList/ns0:DatedMarketingSegment">
													<xsl:variable name="var49_nested">
														<xsl:for-each select="$var44_cur/ns0:PaxSegmentList/ns0:PaxSegment">
															<xsl:variable name="var51_nested">
																<xsl:for-each select="$var46_cur/ns0:PaxSegmentRefID">
																	<xsl:variable name="var53_idx" select="position()"/>
																	<xsl:if test="(position() = '1')">
																		<xsl:value-of select="number((string(.) = string($var50_filter/ns0:PaxSegmentID)))"/>
																	</xsl:if>
																</xsl:for-each>
															</xsl:variable>
															<xsl:if test="boolean(translate(normalize-space($var51_nested), ' 0', ''))">
																<xsl:value-of select="number((string(ns0:DatedMarketingSegmentRefId) = string($var48_filter/ns0:DatedMarketingSegmentId)))"/>
															</xsl:if>
														</xsl:for-each>
													</xsl:variable>
													<xsl:if test="boolean(translate(normalize-space($var49_nested), ' 0', ''))">
														<OriginCode>
															<xsl:value-of select="ns0:Dep/ns0:IATA_LocationCode"/>
														</OriginCode>
													</xsl:if>
												</xsl:for-each>
												<xsl:for-each select="$var44_cur/ns0:DatedMarketingSegmentList/ns0:DatedMarketingSegment">
													<xsl:variable name="var55_nested">
														<xsl:for-each select="$var44_cur/ns0:PaxSegmentList/ns0:PaxSegment">
															<xsl:variable name="var57_nested">
																<xsl:for-each select="$var46_cur/ns0:PaxSegmentRefID">
																	<xsl:variable name="var59_idx" select="position()"/>
																	<xsl:if test="(position() = count($var46_cur/ns0:PaxSegmentRefID))">
																		<xsl:value-of select="number((string(.) = string($var56_filter/ns0:PaxSegmentID)))"/>
																	</xsl:if>
																</xsl:for-each>
															</xsl:variable>
															<xsl:if test="boolean(translate(normalize-space($var57_nested), ' 0', ''))">
																<xsl:value-of select="number((string(ns0:DatedMarketingSegmentRefId) = string($var54_filter/ns0:DatedMarketingSegmentId)))"/>
															</xsl:if>
														</xsl:for-each>
													</xsl:variable>
													<xsl:if test="boolean(translate(normalize-space($var55_nested), ' 0', ''))">
														<DestCode>
															<xsl:value-of select="ns0:Arrival/ns0:IATA_LocationCode"/>
														</DestCode>
													</xsl:if>
												</xsl:for-each>
												<PaxJourneyRefID>
													<xsl:value-of select="ns0:PaxJourneyID"/>
												</PaxJourneyRefID>
											</OriginDest>
										</xsl:for-each>
									</OriginDestList>
								</xsl:for-each>
							</xsl:for-each>
							<xsl:for-each select="ns0:DataLists/ns0:PaxJourneyList">
								<PaxJourneyList>
									<xsl:for-each select="ns0:PaxJourney">
										<PaxJourney>
											<PaxJourneyID>
												<xsl:value-of select="ns0:PaxJourneyID"/>
											</PaxJourneyID>
											<xsl:choose>
												<xsl:when test="ns0:Duration">
													<xsl:for-each select="ns0:Duration">
														<Duration>
															<xsl:value-of select="."/>
														</Duration>
													</xsl:for-each>
												</xsl:when>
												<xsl:otherwise>
													<Duration>
														<xsl:value-of select="'0'"/>
													</Duration>
												</xsl:otherwise>
											</xsl:choose>
											<xsl:for-each select="ns0:PaxSegmentRefID">
												<PaxSegmentRefID>
													<xsl:value-of select="."/>
												</PaxSegmentRefID>
											</xsl:for-each>
										</PaxJourney>
									</xsl:for-each>
								</PaxJourneyList>
							</xsl:for-each>
							<xsl:for-each select="ns0:DataLists">
								<xsl:for-each select="ns0:PaxList">
									<PaxList>
										<xsl:for-each select="ns0:Pax">
											<Pax>
												<PaxID>
													<xsl:value-of select="ns0:PaxID"/>
												</PaxID>
												<xsl:for-each select="ns0:PTC">
													<PTC>
														<xsl:value-of select="."/>
													</PTC>
												</xsl:for-each>
												<xsl:for-each select="ns0:Birthdate">
													<Birthdate>
														<xsl:value-of select="."/>
													</Birthdate>
												</xsl:for-each>
												<xsl:for-each select="ns0:ResidenceCountryCode">
													<ResidenceCountryCode>
														<xsl:value-of select="."/>
													</ResidenceCountryCode>
												</xsl:for-each>
												<xsl:for-each select="ns0:CitizenshipCountryCode">
													<CitizenshipCountryCode>
														<xsl:value-of select="."/>
													</CitizenshipCountryCode>
												</xsl:for-each>
												<xsl:for-each select="ns0:ProfileID_Text">
													<ProfileID_Text>
														<xsl:value-of select="."/>
													</ProfileID_Text>
												</xsl:for-each>
												<!-- Manual Change : START -->
												<xsl:variable name="current_PaxID" select="ns0:PaxID"/>
												<!-- Manual Change Start : Call template from Xslt Lib -->
												<xsl:variable name="PassengerRef">
													<xsl:call-template name="getPaxRef">
														<xsl:with-param name="inputStr" select="$current_PaxID"/>
													</xsl:call-template>
												</xsl:variable>
												<!-- Manual Change end : Call template from Xslt Lib -->
												<xsl:if test="string-length($PassengerRef) &gt; 0">
													<PaxRefID>
														<xsl:value-of select="$PassengerRef"/>
													</PaxRefID>
												</xsl:if>
												<!-- Manual Change : END -->
												<xsl:for-each select="$var64_cur/ns0:ContactInfoList/ns0:ContactInfo">
													<xsl:variable name="var73_nested">
														<xsl:for-each select="ns0:IndividualRefID">
															<xsl:value-of select="number((string(.) = string($var66_cur/ns0:PaxID)))"/>
														</xsl:for-each>
													</xsl:variable>
													<xsl:if test="boolean(translate(normalize-space($var73_nested), ' 0', ''))">
														<ContactInfoRefID>
															<xsl:value-of select="ns0:ContactInfoID"/>
														</ContactInfoRefID>
													</xsl:if>
												</xsl:for-each>
												<xsl:for-each select="ns0:FOID">
													<FOID>
														<FOID_ID>
															<xsl:value-of select="ns0:FOID_ID"/>
														</FOID_ID>
														<FOID_TypeText>
															<xsl:value-of select="ns0:FOID_TypeCode"/>
														</FOID_TypeText>
													</FOID>
												</xsl:for-each>
												<xsl:for-each select="(./ns0:IdentityDoc)[(ns0:IdentityDocTypeCode = 'PT')]">
													<IdentityDoc>
														<IdentityDocID>
															<xsl:value-of select="ns0:IdentityDocID"/>
														</IdentityDocID>
														<IdentityDocTypeCode>
															<xsl:value-of select="ns0:IdentityDocTypeCode"/>
														</IdentityDocTypeCode>
														<xsl:for-each select="ns0:IssuingCountryCode">
															<IssuingCountryCode>
																<xsl:value-of select="."/>
															</IssuingCountryCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:CitizenshipCountryCode">
															<CitizenshipCountryCode>
																<xsl:value-of select="."/>
															</CitizenshipCountryCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:ResidenceCountryCode">
															<ResidenceCountryCode>
																<xsl:value-of select="."/>
															</ResidenceCountryCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:IssueDate">
															<IssueDate>
																<xsl:value-of select="."/>
															</IssueDate>
														</xsl:for-each>
														<xsl:for-each select="ns0:ExpiryDate">
															<ExpiryDate>
																<xsl:value-of select="."/>
															</ExpiryDate>
														</xsl:for-each>
														<xsl:for-each select="ns0:TitleName">
															<TitleName>
																<xsl:value-of select="."/>
															</TitleName>
														</xsl:for-each>
														<xsl:for-each select="ns0:GivenName">
															<GivenName>
																<xsl:value-of select="."/>
															</GivenName>
														</xsl:for-each>
														<xsl:for-each select="ns0:MiddleName">
															<MiddleName>
																<xsl:value-of select="."/>
															</MiddleName>
														</xsl:for-each>
														<Surname>
															<xsl:value-of select="ns0:Surname"/>
														</Surname>
														<xsl:for-each select="ns0:SuffixName">
															<SuffixName>
																<xsl:value-of select="."/>
															</SuffixName>
														</xsl:for-each>
														<xsl:for-each select="ns0:Birthdate">
															<Birthdate>
																<xsl:value-of select="."/>
															</Birthdate>
														</xsl:for-each>
														<xsl:for-each select="ns0:BirthplaceText">
															<BirthplaceText>
																<xsl:value-of select="."/>
															</BirthplaceText>
														</xsl:for-each>
														<xsl:for-each select="ns0:GenderCode">
															<GenderCode>
																<xsl:value-of select="."/>
															</GenderCode>
														</xsl:for-each>
													</IdentityDoc>
												</xsl:for-each>
												<xsl:for-each select="(./ns0:IdentityDoc)[(ns0:IdentityDocTypeCode = 'VS')]">
													<IdentityDoc>
														<IdentityDocID>
															<xsl:value-of select="ns0:IdentityDocID"/>
														</IdentityDocID>
														<IdentityDocTypeCode>
															<xsl:value-of select="'V'"/>
														</IdentityDocTypeCode>
														<xsl:for-each select="ns0:Visa">
															<Visa>
																<xsl:for-each select="ns0:VisaID">
																	<VisaID>
																		<xsl:value-of select="."/>
																	</VisaID>
																</xsl:for-each>
																<VisaTypeCode>
																	<xsl:value-of select="'V'"/>
																</VisaTypeCode>
																<xsl:for-each select="ns0:ExpiryDate">
																	<EnterBeforeDate>
																		<xsl:value-of select="."/>
																	</EnterBeforeDate>
																</xsl:for-each>
																<xsl:for-each select="ns0:HostCountryCode">
																	<HostCountryCode>
																		<xsl:value-of select="."/>
																	</HostCountryCode>
																</xsl:for-each>
																<xsl:for-each select="ns0:IssueDate">
																	<IssueDate>
																		<xsl:value-of select="."/>
																	</IssueDate>
																</xsl:for-each>
																<xsl:for-each select="ns0:IssuingCountryCode">
																	<IssuingCountryCode>
																		<xsl:value-of select="."/>
																	</IssuingCountryCode>
																</xsl:for-each>
															</Visa>
														</xsl:for-each>
													</IdentityDoc>
												</xsl:for-each>
												<xsl:for-each select="(./ns0:IdentityDoc)[(ns0:IdentityDocTypeCode = 'CR')]">
													<IdentityDoc>
														<IdentityDocID>
															<xsl:value-of select="ns0:IdentityDocID"/>
														</IdentityDocID>
														<IdentityDocTypeCode>
															<xsl:value-of select="'K'"/>
														</IdentityDocTypeCode>
														<Visa>
															<VisaID>
																<xsl:value-of select="ns0:IdentityDocID"/>
															</VisaID>
															<VisaTypeCode>
																<xsl:value-of select="'K'"/>
															</VisaTypeCode>
															<xsl:for-each select="ns0:IssuingCountryCode">
																<HostCountryCode>
																	<xsl:value-of select="."/>
																</HostCountryCode>
															</xsl:for-each>
														</Visa>
													</IdentityDoc>
												</xsl:for-each>
												<xsl:for-each select="ns0:RedressCase">
													<IdentityDoc>
														<IdentityDocID>
															<xsl:value-of select="ns0:RedressCaseID"/>
														</IdentityDocID>
														<IdentityDocTypeCode>
															<xsl:value-of select="'R'"/>
														</IdentityDocTypeCode>
														<Visa>
															<VisaID>
																<xsl:value-of select="ns0:RedressCaseID"/>
															</VisaID>
															<VisaTypeCode>
																<xsl:value-of select="'R'"/>
															</VisaTypeCode>
															<HostCountryCode>
																<xsl:value-of select="ns0:CountryCode"/>
															</HostCountryCode>
														</Visa>
													</IdentityDoc>
												</xsl:for-each>
												<xsl:for-each select="(./ns0:IdentityDoc)[(((true() and (ns0:IdentityDocTypeCode != 'PT')) and (ns0:IdentityDocTypeCode != 'VS')) and (ns0:IdentityDocTypeCode != 'CR'))]">
													<EntitlementDocument>
														<DocumentType>
															<xsl:value-of select="'TaxIdentification'"/>
														</DocumentType>
														<Number>
															<xsl:value-of select="ns0:IdentityDocID"/>
														</Number>
														<SubDocumentType>
															<xsl:value-of select="ns0:IdentityDocTypeCode"/>
														</SubDocumentType>
													</EntitlementDocument>
												</xsl:for-each>
												<xsl:for-each select="ns0:Individual">
													<Individual>
														<xsl:for-each select="ns0:IndividualID">
															<IndividualID>
																<xsl:value-of select="."/>
															</IndividualID>
														</xsl:for-each>
														<xsl:for-each select="ns0:Birthdate">
															<Birthdate>
																<xsl:value-of select="."/>
															</Birthdate>
														</xsl:for-each>
														<xsl:for-each select="ns0:BirthplaceText">
															<BirthplaceText>
																<xsl:value-of select="."/>
															</BirthplaceText>
														</xsl:for-each>
														<xsl:for-each select="ns0:GenderCode">
															<GenderCode>
																<xsl:value-of select="."/>
															</GenderCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:TitleName">
															<TitleName>
																<xsl:value-of select="."/>
															</TitleName>
														</xsl:for-each>
														<xsl:for-each select="ns0:GivenName">
															<GivenName>
																<xsl:value-of select="."/>
															</GivenName>
														</xsl:for-each>
														<Surname>
															<xsl:value-of select="ns0:Surname"/>
														</Surname>
														<xsl:for-each select="ns0:SuffixName">
															<SuffixName>
																<xsl:value-of select="."/>
															</SuffixName>
														</xsl:for-each>
													</Individual>
												</xsl:for-each>
												<xsl:for-each select="ns0:LoyaltyProgramAccount">
													<LoyaltyProgramAccount>
														<xsl:if test="(./ns0:LoyaltyProgram/ns0:ProgramCode)[(. = 'CLID')]">
															<ProgramName>
																<xsl:value-of select="'CORPORATE_ID'"/>
															</ProgramName>
														</xsl:if>
														<xsl:if test="(./ns0:LoyaltyProgram/ns0:ProgramCode)[(. = 'CLID')]">
															<ProgramCode>
																<xsl:value-of select="'CLID'"/>
															</ProgramCode>
														</xsl:if>
														<xsl:for-each select="ns0:AccountNumber">
															<AccountNumber>
																<xsl:value-of select="."/>
															</AccountNumber>
														</xsl:for-each>
														<xsl:for-each select="ns0:URL">
															<URL>
																<xsl:value-of select="."/>
															</URL>
														</xsl:for-each>
														<xsl:for-each select="ns0:SignInID">
															<SignInID>
																<xsl:value-of select="."/>
															</SignInID>
														</xsl:for-each>
														<xsl:for-each select="ns0:TierCode">
															<TierCode>
																<xsl:value-of select="."/>
															</TierCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:TierName">
															<TierName>
																<xsl:value-of select="."/>
															</TierName>
														</xsl:for-each>
														<xsl:for-each select="ns0:TierPriorityText">
															<TierPriorityText>
																<xsl:value-of select="."/>
															</TierPriorityText>
														</xsl:for-each>
														<xsl:for-each select="ns0:LoyaltyProgram/ns0:ProviderName">
															<ProviderName>
																<xsl:value-of select="."/>
															</ProviderName>
														</xsl:for-each>
														<xsl:for-each select="ns0:LoyaltyProgram/ns0:Alliance">
															<Alliance>
																<AllianceCode>
																	<xsl:value-of select="ns0:AllianceCode"/>
																</AllianceCode>
																<xsl:for-each select="ns0:Name">
																	<Name>
																		<xsl:value-of select="."/>
																	</Name>
																</xsl:for-each>
																<xsl:for-each select="ns0:URL">
																	<URL>
																		<xsl:value-of select="."/>
																	</URL>
																</xsl:for-each>
																<xsl:for-each select="ns0:Carrier">
																	<Carrier>
																		<AirlineDesigCode>
																			<xsl:value-of select="ns0:AirlineDesigCode"/>
																		</AirlineDesigCode>
																		<xsl:for-each select="ns0:Name">
																			<Name>
																				<xsl:value-of select="."/>
																			</Name>
																		</xsl:for-each>
																	</Carrier>
																</xsl:for-each>
															</Alliance>
														</xsl:for-each>
														<xsl:for-each select="ns0:LoyaltyProgram/ns0:Carrier">
															<Carrier>
																<AirlineDesigCode>
																	<xsl:value-of select="ns0:AirlineDesigCode"/>
																</AirlineDesigCode>
																<xsl:for-each select="ns0:Name">
																	<Name>
																		<xsl:value-of select="."/>
																	</Name>
																</xsl:for-each>
															</Carrier>
														</xsl:for-each>
													</LoyaltyProgramAccount>
												</xsl:for-each>
												<xsl:for-each select="ns0:Remark">
													<Remark>
														<xsl:for-each select="ns0:RemarkText">
															<RemarkText>
																<xsl:value-of select="."/>
															</RemarkText>
														</xsl:for-each>
													</Remark>
												</xsl:for-each>
											</Pax>
										</xsl:for-each>
									</PaxList>
								</xsl:for-each>
							</xsl:for-each>
							<xsl:for-each select="ns0:DataLists">
								<xsl:for-each select="ns0:PaxSegmentList">
									<PaxSegmentList>
										<xsl:for-each select="ns0:PaxSegment">
											<PaxSegment>
												<PaxSegmentID>
													<xsl:value-of select="ns0:PaxSegmentID"/>
												</PaxSegmentID>
												<Duration>
													<xsl:value-of select="'0'"/>
												</Duration>
												<xsl:for-each select="($var126_cur/ns0:DatedMarketingSegmentList/ns0:DatedMarketingSegment)[(string($var128_cur/ns0:DatedMarketingSegmentRefId) = string(ns0:DatedMarketingSegmentId))]">
													<Dep>
														<xsl:for-each select="ns0:Dep/ns0:BoardingGateID">
															<BoardingGateID>
																<xsl:value-of select="."/>
															</BoardingGateID>
														</xsl:for-each>
														<IATA_LocationCode>
															<xsl:value-of select="ns0:Dep/ns0:IATA_LocationCode"/>
														</IATA_LocationCode>
														<xsl:for-each select="ns0:Dep/ns0:StationName">
															<StationName>
																<xsl:value-of select="."/>
															</StationName>
														</xsl:for-each>
														<xsl:for-each select="ns0:Dep/ns0:TerminalName">
															<TerminalName>
																<xsl:value-of select="."/>
															</TerminalName>
														</xsl:for-each>
														<xsl:for-each select="ns0:Dep/ns0:AircraftScheduledDateTime">
															<AircraftScheduledDateTime>
																<xsl:value-of select="."/>
															</AircraftScheduledDateTime>
														</xsl:for-each>
													</Dep>
												</xsl:for-each>
												<xsl:for-each select="($var126_cur/ns0:DatedMarketingSegmentList/ns0:DatedMarketingSegment)[(string($var128_cur/ns0:DatedMarketingSegmentRefId) = string(ns0:DatedMarketingSegmentId))]">
													<Arrival>
														<xsl:for-each select="ns0:Arrival/ns0:BoardingGateID">
															<BoardingGateID>
																<xsl:value-of select="."/>
															</BoardingGateID>
														</xsl:for-each>
														<IATA_LocationCode>
															<xsl:value-of select="ns0:Arrival/ns0:IATA_LocationCode"/>
														</IATA_LocationCode>
														<xsl:for-each select="ns0:Arrival/ns0:StationName">
															<StationName>
																<xsl:value-of select="."/>
															</StationName>
														</xsl:for-each>
														<xsl:for-each select="ns0:Arrival/ns0:TerminalName">
															<TerminalName>
																<xsl:value-of select="."/>
															</TerminalName>
														</xsl:for-each>
														<xsl:for-each select="ns0:Arrival/ns0:AircraftScheduledDateTime">
															<AircraftScheduledDateTime>
																<xsl:value-of select="."/>
															</AircraftScheduledDateTime>
														</xsl:for-each>
													</Arrival>
												</xsl:for-each>
												<xsl:for-each select="($var126_cur/ns0:DatedMarketingSegmentList/ns0:DatedMarketingSegment)[(string($var128_cur/ns0:DatedMarketingSegmentRefId) = string(ns0:DatedMarketingSegmentId))]">
													<MarketingCarrierInfo>
														<CarrierDesigCode>
															<xsl:value-of select="ns0:CarrierDesigCode"/>
														</CarrierDesigCode>
														<xsl:for-each select="ns0:CarrierName">
															<CarrierName>
																<xsl:value-of select="."/>
															</CarrierName>
														</xsl:for-each>
														<MarketingCarrierFlightNumberText>
															<xsl:value-of select="ns0:MarketingCarrierFlightNumberText"/>
														</MarketingCarrierFlightNumberText>
														<xsl:for-each select="$var128_cur/ns0:MarketingCarrierRBD_Code">
															<RBD_Code>
																<xsl:value-of select="."/>
															</RBD_Code>
														</xsl:for-each>
													</MarketingCarrierInfo>
												</xsl:for-each>
												<xsl:for-each select="$var126_cur/ns0:DatedOperatingSegmentList/ns0:DatedOperatingSegment">
													<xsl:variable name="var143_nested">
														<xsl:for-each select="$var126_cur/ns0:DatedMarketingSegmentList/ns0:DatedMarketingSegment">
															<xsl:value-of select="number(((string($var128_cur/ns0:DatedMarketingSegmentRefId) = string(ns0:DatedMarketingSegmentId)) and (string(ns0:DatedOperatingSegmentRefId) = string($var142_filter/ns0:DatedOperatingSegmentId))))"/>
														</xsl:for-each>
													</xsl:variable>
													<xsl:if test="boolean(translate(normalize-space($var143_nested), ' 0', ''))">
														<OperatingCarrierInfo>
															<CarrierDesigCode>
																<xsl:value-of select="ns0:CarrierDesigCode"/>
															</CarrierDesigCode>
															<xsl:for-each select="ns0:CarrierName">
																<CarrierName>
																	<xsl:value-of select="."/>
																</CarrierName>
															</xsl:for-each>
															<xsl:for-each select="ns0:OperatingCarrierFlightNumberText">
																<OperatingCarrierFlightNumberText>
																	<xsl:value-of select="."/>
																</OperatingCarrierFlightNumberText>
															</xsl:for-each>
															<xsl:for-each select="$var128_cur/ns0:OperatingCarrierRBD_Code">
																<RBD_Code>
																	<xsl:value-of select="."/>
																</RBD_Code>
															</xsl:for-each>
															<xsl:for-each select="$var126_cur/ns0:DisclosureList/ns0:Disclosure">
																<xsl:variable name="var149_nested">
																	<xsl:for-each select="$var142_filter/ns0:DisclosureRefID">
																		<xsl:value-of select="number((string(.) = string($var148_filter/ns0:DisclosureID)))"/>
																	</xsl:for-each>
																</xsl:variable>
																<xsl:if test="boolean(translate(normalize-space($var149_nested), ' 0', ''))">
																	<Disclosure>
																		<DisclosureID>
																			<xsl:value-of select="ns0:DisclosureID"/>
																		</DisclosureID>
																		<xsl:for-each select="ns0:Desc">
																			<xsl:variable name="var152_idx" select="position()"/>
																			<Desc>
																				<DescID>
																					<xsl:value-of select="concat('DescID-', position())"/>
																				</DescID>
																				<xsl:for-each select="ns0:DescText">
																					<DescText>
																						<xsl:value-of select="."/>
																					</DescText>
																				</xsl:for-each>
																			</Desc>
																		</xsl:for-each>
																	</Disclosure>
																</xsl:if>
															</xsl:for-each>
														</OperatingCarrierInfo>
													</xsl:if>
												</xsl:for-each>
												<xsl:for-each select="$var126_cur/ns0:DatedOperatingLegList/ns0:DatedOperatingLeg">
													<xsl:variable name="var155_nested">
														<xsl:for-each select="$var126_cur/ns0:DatedMarketingSegmentList/ns0:DatedMarketingSegment">
															<xsl:for-each select="$var126_cur/ns0:DatedOperatingSegmentList/ns0:DatedOperatingSegment">
																<xsl:for-each select="ns0:DatedOperatingLegRefID">
																	<xsl:value-of select="number((((string($var128_cur/ns0:DatedMarketingSegmentRefId) = string($var156_cur/ns0:DatedMarketingSegmentId)) and (string($var156_cur/ns0:DatedOperatingSegmentRefId) = string($var157_cur/ns0:DatedOperatingSegmentId))) and (string(.) = string($var154_filter/ns0:DatedOperatingLegID))))"/>
																</xsl:for-each>
															</xsl:for-each>
														</xsl:for-each>
													</xsl:variable>
													<xsl:if test="boolean(translate(normalize-space($var155_nested), ' 0', ''))">
														<DatedOperatingLeg>
															<DatedOperatingLegID>
																<xsl:value-of select="ns0:DatedOperatingLegID"/>
															</DatedOperatingLegID>
															<xsl:for-each select="ns0:DistanceMeasure">
																<DistanceMeasure>
																	<xsl:call-template name="tbf:tbf1_MeasureType">
																		<xsl:with-param name="input" select="."/>
																	</xsl:call-template>
																</DistanceMeasure>
															</xsl:for-each>
															<Dep>
																<IATA_LocationCode>
																	<xsl:value-of select="ns0:Dep/ns0:IATA_LocationCode"/>
																</IATA_LocationCode>
																<xsl:for-each select="ns0:Dep/ns0:AircraftScheduledDateTime">
																	<AircraftScheduledDateTime>
																		<xsl:value-of select="."/>
																	</AircraftScheduledDateTime>
																</xsl:for-each>
															</Dep>
															<Arrival>
																<IATA_LocationCode>
																	<xsl:value-of select="ns0:Arrival/ns0:IATA_LocationCode"/>
																</IATA_LocationCode>
																<xsl:for-each select="ns0:Arrival/ns0:AircraftScheduledDateTime">
																	<AircraftScheduledDateTime>
																		<xsl:value-of select="."/>
																	</AircraftScheduledDateTime>
																</xsl:for-each>
															</Arrival>
															<xsl:for-each select="ns0:IATA_AircraftType">
																<IATA_AircraftType>
																	<xsl:for-each select="ns0:IATA_AircraftTypeCode">
																		<IATA_AircraftTypeCode>
																			<xsl:value-of select="."/>
																		</IATA_AircraftTypeCode>
																	</xsl:for-each>
																</IATA_AircraftType>
															</xsl:for-each>
														</DatedOperatingLeg>
													</xsl:if>
												</xsl:for-each>
											</PaxSegment>
										</xsl:for-each>
									</PaxSegmentList>
								</xsl:for-each>
							</xsl:for-each>
							<xsl:for-each select="ns0:DataLists/ns0:PriceClassList">
								<PriceClassList>
									<xsl:for-each select="ns0:PriceClass">
										<xsl:variable name="var166_idx" select="position()"/>
										<PriceClass>
											<PriceClassID>
												<xsl:value-of select="ns0:PriceClassID"/>
											</PriceClassID>
											<xsl:for-each select="ns0:Code">
												<Code>
													<xsl:value-of select="."/>
												</Code>
											</xsl:for-each>
											<Name>
												<xsl:value-of select="ns0:Name"/>
											</Name>
											<xsl:for-each select="ns0:Desc">
												<xsl:variable name="var169_idx" select="position()"/>
												<Desc>
													<DescID>
														<xsl:value-of select="concat('FFM', $var166_idx, '-', 'DESC', position())"/>
													</DescID>
													<xsl:for-each select="ns0:DescText">
														<DescText>
															<xsl:value-of select="."/>
														</DescText>
													</xsl:for-each>
												</Desc>
											</xsl:for-each>
										</PriceClass>
									</xsl:for-each>
								</PriceClassList>
							</xsl:for-each>
							<xsl:for-each select="ns0:DataLists/ns0:SeatProfileList">
								<SeatProfileList>
									<xsl:for-each select="ns0:SeatProfile">
										<SeatProfile>
											<SeatProfileID>
												<xsl:value-of select="ns0:SeatProfileID"/>
											</SeatProfileID>
											<xsl:for-each select="ns0:SeatCharacteristicCode">
												<CharacteristicCode>
													<xsl:value-of select="."/>
												</CharacteristicCode>
											</xsl:for-each>
											<xsl:for-each select="ns0:MarketingInfo/ns0:DescText">
												<DescText>
													<xsl:value-of select="."/>
												</DescText>
											</xsl:for-each>
										</SeatProfile>
									</xsl:for-each>
								</SeatProfileList>
							</xsl:for-each>
							<xsl:for-each select="ns0:DataLists/ns0:ServiceDefinitionList">
								<ServiceDefinitionList>
									<xsl:for-each select="ns0:ServiceDefinition">
										<ServiceDefinition>
											<ServiceDefinitionID>
												<xsl:value-of select="ns0:ServiceDefinitionID"/>
											</ServiceDefinitionID>
											<OwnerCode>
												<xsl:value-of select="ns0:OwnerCode"/>
											</OwnerCode>
											<Name>
												<xsl:value-of select="ns0:Name"/>
											</Name>
											<xsl:for-each select="ns0:ServiceCode">
												<ServiceCode>
													<xsl:value-of select="."/>
												</ServiceCode>
											</xsl:for-each>
											<xsl:for-each select="ns0:RFIC">
												<ReasonForIssuanceCode>
													<xsl:value-of select="."/>
												</ReasonForIssuanceCode>
											</xsl:for-each>
											<xsl:for-each select="ns0:RFISC">
												<ReasonForIssuanceSubCode>
													<xsl:value-of select="."/>
												</ReasonForIssuanceSubCode>
											</xsl:for-each>
											<Description>
												<DescID>
													<xsl:value-of select="'ServDescID'"/>
												</DescID>
												<xsl:for-each select="ns0:Desc/ns0:DescText">
													<DescText>
														<xsl:value-of select="."/>
													</DescText>
												</xsl:for-each>
											</Description>
											<xsl:for-each select="ns0:ServiceDefinitionAssociation">
												<ServiceDefinitionAssociation>
													<xsl:for-each select="ns0:BaggageAllowanceRef/ns0:BaggageAllowanceRefID">
														<BaggageAllowanceRefID>
															<xsl:value-of select="."/>
														</BaggageAllowanceRefID>
													</xsl:for-each>
													<xsl:for-each select="ns0:SeatProfileRef/ns0:SeatProfileRefID">
														<SeatProfileRefID>
															<xsl:value-of select="."/>
														</SeatProfileRefID>
													</xsl:for-each>
													<xsl:for-each select="ns0:ServiceBundle">
														<ServiceBundle>
															<xsl:for-each select="ns0:MaximumServiceQty">
																<MaximumServiceQty>
																	<xsl:value-of select="number(.)"/>
																</MaximumServiceQty>
															</xsl:for-each>
															<xsl:for-each select="ns0:ServiceDefinitionRefID">
																<ServiceDefinitionRefID>
																	<xsl:value-of select="."/>
																</ServiceDefinitionRefID>
															</xsl:for-each>
														</ServiceBundle>
													</xsl:for-each>
												</ServiceDefinitionAssociation>
											</xsl:for-each>
										</ServiceDefinition>
									</xsl:for-each>
								</ServiceDefinitionList>
							</xsl:for-each>
						</DataLists>
						<Metadata>
							<Other>
								<OtherMetadata>
									<xsl:for-each select="ns0:Order">
										<xsl:for-each select="ns0:OrderItem">
											<xsl:variable name="var189_idx" select="position()"/>
											<xsl:if test="(position() = 1)">
												<RuleMetadatas>
													<xsl:for-each select="ns0:FareDetail/ns0:FareComponent">
														<xsl:for-each select="ns0:CancelRestrictions">
															<xsl:variable name="var192_idx" select="position()"/>
															<RuleMetadata>
																<xsl:attribute name="MetadataKey" namespace="">
																	<xsl:value-of select="concat('RULE', position())"/>
																</xsl:attribute>
																<xsl:for-each select="ns0:JourneyStageCode">
																	<xsl:for-each select="$var191_cur/ns0:DescText">
																		<xsl:choose>
																			<xsl:when test="(($var193_cur = 'No Show') and contains(., 'before departure'))">
																				<RuleID>
																					<xsl:value-of select="'Cancel before Departure - No Show'"/>
																				</RuleID>
																			</xsl:when>
																			<xsl:when test="(($var193_cur = 'No Show') and contains(., 'after departure'))">
																				<RuleID>
																					<xsl:value-of select="'Cancel after Departure - No Show'"/>
																				</RuleID>
																			</xsl:when>
																			<xsl:otherwise>
																				<xsl:variable name="var195_nested">
																					<xsl:call-template name="vmf:vmf3_inputtoresult">
																						<xsl:with-param name="input" select="string($var193_cur)"/>
																					</xsl:call-template>
																				</xsl:variable>
																				<xsl:if test="string($var195_nested)">
																					<RuleID>
																						<xsl:variable name="var196_nested">
																							<xsl:call-template name="vmf:vmf3_inputtoresult">
																								<xsl:with-param name="input" select="string($var193_cur)"/>
																							</xsl:call-template>
																						</xsl:variable>
																						<xsl:value-of select="substring($var196_nested, 2)"/>
																					</RuleID>
																				</xsl:if>
																			</xsl:otherwise>
																		</xsl:choose>
																	</xsl:for-each>
																</xsl:for-each>
																<Values>
																	<Value>
																		<xsl:for-each select="ns0:AllowedModificationInd">
																			<xsl:variable name="var198_nested">
																				<xsl:call-template name="vmf:vmf4_inputtoresult">
																					<xsl:with-param name="input" select="string(boolean(translate(normalize-space(string(.)), ' 0false', '')))"/>
																				</xsl:call-template>
																			</xsl:variable>
																			<xsl:if test="string($var198_nested)">
																				<Instruction>
																					<xsl:variable name="var199_nested">
																						<xsl:call-template name="vmf:vmf4_inputtoresult">
																							<xsl:with-param name="input" select="string(boolean(translate(normalize-space(string(.)), ' 0false', '')))"/>
																						</xsl:call-template>
																					</xsl:variable>
																					<xsl:value-of select="substring($var199_nested, 2)"/>
																				</Instruction>
																			</xsl:if>
																		</xsl:for-each>
																	</Value>
																</Values>
															</RuleMetadata>
														</xsl:for-each>
													</xsl:for-each>
													<xsl:for-each select="ns0:FareDetail/ns0:FareComponent">
														<xsl:for-each select="ns0:ChangeRestrictions">
															<xsl:variable name="var202_idx" select="position()"/>
															<RuleMetadata>
																<xsl:attribute name="MetadataKey" namespace="">
																	<xsl:value-of select="concat('RULE', position())"/>
																</xsl:attribute>
																<xsl:for-each select="ns0:JourneyStageCode">
																	<xsl:for-each select="$var201_cur/ns0:DescText">
																		<xsl:choose>
																			<xsl:when test="(($var203_cur = 'No Show') and contains(., 'before departure'))">
																				<RuleID>
																					<xsl:value-of select="'Change before Departure - No Show'"/>
																				</RuleID>
																			</xsl:when>
																			<xsl:when test="(($var203_cur = 'No Show') and contains(., 'after departure'))">
																				<RuleID>
																					<xsl:value-of select="'Change after Departure - No Show'"/>
																				</RuleID>
																			</xsl:when>
																			<xsl:otherwise>
																				<xsl:variable name="var205_nested">
																					<xsl:call-template name="vmf:vmf5_inputtoresult">
																						<xsl:with-param name="input" select="string($var203_cur)"/>
																					</xsl:call-template>
																				</xsl:variable>
																				<xsl:if test="string($var205_nested)">
																					<RuleID>
																						<xsl:variable name="var206_nested">
																							<xsl:call-template name="vmf:vmf5_inputtoresult">
																								<xsl:with-param name="input" select="string($var203_cur)"/>
																							</xsl:call-template>
																						</xsl:variable>
																						<xsl:value-of select="substring($var206_nested, 2)"/>
																					</RuleID>
																				</xsl:if>
																			</xsl:otherwise>
																		</xsl:choose>
																	</xsl:for-each>
																</xsl:for-each>
																<Values>
																	<Value>
																		<xsl:for-each select="ns0:AllowedModificationInd">
																			<xsl:variable name="var208_nested">
																				<xsl:call-template name="vmf:vmf6_inputtoresult">
																					<xsl:with-param name="input" select="string(boolean(translate(normalize-space(string(.)), ' 0false', '')))"/>
																				</xsl:call-template>
																			</xsl:variable>
																			<xsl:if test="string($var208_nested)">
																				<Instruction>
																					<xsl:variable name="var209_nested">
																						<xsl:call-template name="vmf:vmf6_inputtoresult">
																							<xsl:with-param name="input" select="string(boolean(translate(normalize-space(string(.)), ' 0false', '')))"/>
																						</xsl:call-template>
																					</xsl:variable>
																					<xsl:value-of select="substring($var209_nested, 2)"/>
																				</Instruction>
																			</xsl:if>
																		</xsl:for-each>
																	</Value>
																</Values>
															</RuleMetadata>
														</xsl:for-each>
													</xsl:for-each>
												</RuleMetadatas>
											</xsl:if>
										</xsl:for-each>
									</xsl:for-each>
								</OtherMetadata>
							</Other>
						</Metadata>
						<Order>
							<xsl:for-each select="ns0:Order">
								<OrderID>
									<xsl:value-of select="ns0:OrderID"/>
								</OrderID>
							</xsl:for-each>
							<xsl:for-each select="ns0:Order">
								<OwnerCode>
									<xsl:value-of select="ns0:OwnerCode"/>
								</OwnerCode>
							</xsl:for-each>
							<xsl:for-each select="ns0:Order/ns0:StatusCode">
								<StatusCode>
									<xsl:value-of select="."/>
								</StatusCode>
							</xsl:for-each>
							<xsl:for-each select="ns0:Order">
								<xsl:for-each select="ns0:OrderItem">
									<xsl:variable name="var215_idx" select="position()"/>
									<xsl:for-each select="(./ns0:PaymentTimeLimitDateTime)[($var215_idx = 1)]">
										<PaymentTimeLimitDateTime>
											<xsl:value-of select="."/>
										</PaymentTimeLimitDateTime>
									</xsl:for-each>
								</xsl:for-each>
							</xsl:for-each>
							<xsl:for-each select="ns0:Order">
								<xsl:for-each select="ns0:OrderItem">
									<xsl:variable name="var219_idx" select="position()"/>
									<xsl:for-each select="ns0:Service">
										<xsl:variable name="var221_idx" select="position()"/>
										<xsl:for-each select="ns0:BookingRef">
											<xsl:variable name="var223_nested">
												<xsl:choose>
													<xsl:when test="ns0:BookingRefTypeCode">
														<xsl:for-each select="ns0:BookingRefTypeCode">
															<xsl:value-of select="number(((($var219_idx = 1) and ($var221_idx = 1)) and boolean(translate(normalize-space(string((. != 'ASSOCIATED_BOOKING'))), ' 0false', ''))))"/>
														</xsl:for-each>
													</xsl:when>
													<xsl:otherwise>
														<xsl:value-of select="number(((($var219_idx = 1) and ($var221_idx = 1)) and boolean(translate(normalize-space('True'), ' 0false', ''))))"/>
													</xsl:otherwise>
												</xsl:choose>
											</xsl:variable>
											<xsl:if test="boolean(translate(normalize-space($var223_nested), ' 0', ''))">
												<BookingRef>
													<BookingID>
														<xsl:value-of select="ns0:BookingID"/>
													</BookingID>
													<BookingEntity>
														<Carrier>
															<xsl:for-each select="ns0:BookingEntity/ns0:Carrier">
																<AirlineDesigCode>
																	<xsl:value-of select="ns0:AirlineDesigCode"/>
																</AirlineDesigCode>
															</xsl:for-each>
														</Carrier>
													</BookingEntity>
												</BookingRef>
											</xsl:if>
										</xsl:for-each>
									</xsl:for-each>
								</xsl:for-each>
							</xsl:for-each>
							<xsl:for-each select="ns0:Order">
								<xsl:for-each select="ns0:OrderItem">
									<OrderItem>
										<OrderItemID>
											<xsl:value-of select="ns0:OrderItemID"/>
										</OrderItemID>
										<OwnerCode>
											<xsl:value-of select="ns0:OwnerCode"/>
										</OwnerCode>
										<xsl:for-each select="ns0:StatusCode">
											<xsl:variable name="var229_nested">
												<xsl:call-template name="vmf:vmf7_inputtoresult">
													<xsl:with-param name="input" select="string(.)"/>
												</xsl:call-template>
											</xsl:variable>
											<xsl:if test="string($var229_nested)">
												<StatusCode>
													<xsl:variable name="var230_nested">
														<xsl:call-template name="vmf:vmf7_inputtoresult">
															<xsl:with-param name="input" select="string(.)"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="substring($var230_nested, 2)"/>
												</StatusCode>
											</xsl:if>
										</xsl:for-each>
										<xsl:for-each select="ns0:PriceGuaranteeTimeLimitDateTime">
											<PriceGuaranteeTimeLimitDateTime>
												<xsl:value-of select="."/>
											</PriceGuaranteeTimeLimitDateTime>
										</xsl:for-each>
										<xsl:for-each select="ns0:FareDetail">
											<FareDetail>
												<xsl:for-each select="ns0:PaxRefID">
													<PassengerRefs>
														<xsl:value-of select="."/>
													</PassengerRefs>
												</xsl:for-each>
												<xsl:for-each select="ns0:Price">
													<Price>
														<TotalAmount>
															<DetailCurrencyPrice>
																<xsl:for-each select="ns0:TotalAmount">
																	<Total>
																		<xsl:for-each select="@CurCode">
																			<xsl:attribute name="Code" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:value-of select="number(.)"/>
																	</Total>
																</xsl:for-each>
																<xsl:if test="ns0:Fee">
																	<Fees>
																		<xsl:for-each select="ns0:Fee">
																			<Total>
																				<xsl:for-each select="ns0:Amount/@CurCode">
																					<xsl:attribute name="Code" namespace="">
																						<xsl:value-of select="."/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="ns0:RefundInd">
																					<xsl:attribute name="refundInd" namespace="">
																						<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<!--Manual Change : Remove number()-->
																				<xsl:value-of select="ns0:Amount"/>
																			</Total>
																		</xsl:for-each>
																		<Breakdown>
																			<Fee>
																				<xsl:for-each select="ns0:Fee">
																					<Amount>
																						<xsl:for-each select="ns0:Amount/@CurCode">
																							<xsl:attribute name="Code" namespace="">
																								<xsl:value-of select="."/>
																							</xsl:attribute>
																						</xsl:for-each>
																						<!--Manual Change : Remove number()-->
																						<xsl:value-of select="ns0:Amount"/>
																					</Amount>
																				</xsl:for-each>
																				<xsl:for-each select="ns0:Fee/ns0:DesigText">
																					<Designator>
																						<xsl:variable name="var243_nested">
																							<xsl:value-of select="number(contains(., 'FC'))"/>
																							<xsl:value-of select="number(contains(., 'FD'))"/>
																						</xsl:variable>
																						<xsl:choose>
																							<xsl:when test="boolean(translate(normalize-space($var243_nested), ' 0', ''))">
																								<xsl:value-of select="'OB'"/>
																							</xsl:when>
																							<xsl:otherwise>
																								<xsl:value-of select="."/>
																							</xsl:otherwise>
																						</xsl:choose>
																					</Designator>
																				</xsl:for-each>
																				<xsl:for-each select="ns0:Fee/ns0:DescText">
																					<Description>
																						<xsl:value-of select="."/>
																					</Description>
																				</xsl:for-each>
																				<xsl:for-each select="ns0:Fee/ns0:DesigText">
																					<Nature>
																						<xsl:value-of select="."/>
																					</Nature>
																				</xsl:for-each>
																			</Fee>
																		</Breakdown>
																	</Fees>
																</xsl:if>
															</DetailCurrencyPrice>
														</TotalAmount>
														<xsl:for-each select="ns0:BaseAmount">
															<BaseAmount>
																<xsl:for-each select="@CurCode">
																	<xsl:attribute name="Code" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:value-of select="number(.)"/>
															</BaseAmount>
														</xsl:for-each>
														<xsl:for-each select="ns0:TaxSummary">
															<Taxes>
																<xsl:for-each select="ns0:TotalTaxAmount">
																	<Total>
																		<xsl:for-each select="@CurCode">
																			<xsl:attribute name="Code" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:value-of select="number(.)"/>
																	</Total>
																</xsl:for-each>
																<Breakdown>
																	<xsl:for-each select="ns0:Tax">
																		<Tax>
																			<xsl:for-each select="ns0:ApproximateInd">
																				<xsl:attribute name="ApproxInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:CollectionInd">
																				<xsl:attribute name="CollectionInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:RefundInd">
																				<xsl:attribute name="RefundInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:QualifierCode">
																				<Qualifier>
																					<xsl:value-of select="."/>
																				</Qualifier>
																			</xsl:for-each>
																			<Amount>
																				<xsl:for-each select="ns0:Amount/@CurCode">
																					<xsl:attribute name="Code" namespace="">
																						<xsl:value-of select="."/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:value-of select="number(ns0:Amount)"/>
																			</Amount>
																			<xsl:for-each select="ns0:AddlTaxCode">
																				<Nation>
																					<xsl:value-of select="."/>
																				</Nation>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:TaxCode">
																				<TaxCode>
																					<xsl:value-of select="."/>
																				</TaxCode>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:TaxTypeCode">
																				<TaxType>
																					<xsl:value-of select="."/>
																				</TaxType>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:CollectionPointTax">
																				<CollectionPoint>
																					<xsl:for-each select="ns0:AirportAmount/@CurCode">
																						<CurrCode>
																							<xsl:value-of select="."/>
																						</CurrCode>
																					</xsl:for-each>
																					<AirportAmount>
																						<xsl:value-of select="number(ns0:AirportAmount)"/>
																					</AirportAmount>
																					<AirportCode>
																						<xsl:value-of select="ns0:Station/ns0:IATA_LocationCode"/>
																					</AirportCode>
																				</CollectionPoint>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:CurConversion">
																				<LocalAmount>
																					<xsl:for-each select="ns0:LocalAmount/@CurCode">
																						<xsl:attribute name="Code" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:value-of select="number(ns0:LocalAmount)"/>
																				</LocalAmount>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:DescText">
																				<Description>
																					<xsl:value-of select="."/>
																				</Description>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:CurConversion">
																				<Conversion>
																					<CurrencyAmount>
																						<xsl:for-each select="ns0:Amount/@CurCode">
																							<xsl:attribute name="Code" namespace="">
																								<xsl:value-of select="."/>
																							</xsl:attribute>
																						</xsl:for-each>
																						<xsl:value-of select="number(ns0:Amount)"/>
																					</CurrencyAmount>
																				</Conversion>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:FiledAmount">
																				<FiledAmount>
																					<xsl:for-each select="@CurCode">
																						<xsl:attribute name="Code" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:value-of select="number(.)"/>
																				</FiledAmount>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:FiledTaxCode">
																				<FileTaxType>
																					<xsl:value-of select="."/>
																				</FileTaxType>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:AddlFiledTaxCode">
																				<AddlFiledTaxType>
																					<xsl:value-of select="."/>
																				</AddlFiledTaxType>
																			</xsl:for-each>
																		</Tax>
																	</xsl:for-each>
																</Breakdown>
															</Taxes>
														</xsl:for-each>
													</Price>
												</xsl:for-each>
												<FareComponent>
													<xsl:for-each select="ns0:FareComponent">
														<FareBasis>
															<xsl:for-each select="ns0:FareBasisCode">
																<FareBasisCode>
																	<Code>
																		<xsl:value-of select="."/>
																	</Code>
																</FareBasisCode>
															</xsl:for-each>
															<xsl:for-each select="$var5_cur/ns0:DataLists/ns0:PaxSegmentList/ns0:PaxSegment">
																<xsl:for-each select="ns0:MarketingCarrierRBD_Code">
																	<xsl:variable name="var275_nested">
																		<xsl:for-each select="$var271_cur/ns0:PaxSegmentRefID">
																			<xsl:value-of select="number((string(.) = string($var273_cur/ns0:PaxSegmentID)))"/>
																		</xsl:for-each>
																	</xsl:variable>
																	<xsl:if test="boolean(translate(normalize-space($var275_nested), ' 0', ''))">
																		<RBD>
																			<xsl:value-of select="."/>
																		</RBD>
																	</xsl:if>
																</xsl:for-each>
															</xsl:for-each>
															<xsl:for-each select="ns0:CabinType">
																<CabinType>
																	<xsl:for-each select="ns0:CabinTypeCode">
																		<xsl:variable name="var279_nested">
																			<xsl:call-template name="vmf:vmf8_inputtoresult">
																				<xsl:with-param name="input" select="string(.)"/>
																			</xsl:call-template>
																		</xsl:variable>
																		<xsl:if test="string($var279_nested)">
																			<CabinTypeCode>
																				<xsl:variable name="var280_nested">
																					<xsl:call-template name="vmf:vmf8_inputtoresult">
																						<xsl:with-param name="input" select="string(.)"/>
																					</xsl:call-template>
																				</xsl:variable>
																				<xsl:value-of select="substring($var280_nested, 2)"/>
																			</CabinTypeCode>
																		</xsl:if>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:CabinTypeName">
																		<CabinTypeName>
																			<xsl:value-of select="."/>
																		</CabinTypeName>
																	</xsl:for-each>
																</CabinType>
															</xsl:for-each>
														</FareBasis>
													</xsl:for-each>
													<FareRules>
														<Penalty>
															<xsl:attribute name="CancelFeeInd" namespace="">
																<xsl:value-of select="not((sum(ns0:FareComponent/ns0:CancelRestrictions/ns0:Fee/ns0:MaximumAmount) = 0))"/>
															</xsl:attribute>
															<xsl:attribute name="ChangeFeeInd" namespace="">
																<xsl:value-of select="not((sum(ns0:FareComponent/ns0:ChangeRestrictions/ns0:Fee/ns0:MaximumAmount) = 0))"/>
															</xsl:attribute>
															<Details>
																<xsl:for-each select="ns0:FareComponent">
																	<xsl:for-each select="ns0:CancelRestrictions">
																		<xsl:variable name="var284_idx" select="position()"/>
																		<Detail>
																			<xsl:attribute name="refs" namespace="">
																				<xsl:value-of select="concat('RULE', position())"/>
																			</xsl:attribute>
																			<Type>
																				<xsl:value-of select="'Cancel'"/>
																			</Type>
																			<xsl:for-each select="ns0:JourneyStageCode">
																				<xsl:for-each select="$var283_cur/ns0:DescText">
																					<xsl:choose>
																						<xsl:when test="(($var285_cur = 'No Show') and contains(., 'before departure'))">
																							<Application>
																								<xsl:value-of select="12"/>
																							</Application>
																						</xsl:when>
																						<xsl:when test="(($var285_cur = 'No Show') and contains(., 'after departure'))">
																							<Application>
																								<xsl:value-of select="13"/>
																							</Application>
																						</xsl:when>
																						<xsl:when test="($var285_cur = 'Prior To Departure')">
																							<Application>
																								<xsl:value-of select="2"/>
																							</Application>
																						</xsl:when>
																						<xsl:when test="($var285_cur = 'After Departure')">
																							<Application>
																								<xsl:value-of select="3"/>
																							</Application>
																						</xsl:when>
																					</xsl:choose>
																				</xsl:for-each>
																			</xsl:for-each>
																			<Amounts>
																				<Amount>
																					<xsl:for-each select="ns0:Fee/ns0:MinimumAmount">
																						<CurrencyAmountValue>
																							<xsl:for-each select="@CurCode">
																								<xsl:attribute name="Code" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:value-of select="number(.)"/>
																						</CurrencyAmountValue>
																					</xsl:for-each>
																					<AmountApplication>
																						<xsl:value-of select="'MIN'"/>
																					</AmountApplication>
																					<ApplicableFeeRemarks>
																						<xsl:for-each select="ns0:DescText">
																							<Remark>
																								<xsl:value-of select="."/>
																							</Remark>
																						</xsl:for-each>
																					</ApplicableFeeRemarks>
																				</Amount>
																				<Amount>
																					<xsl:for-each select="ns0:Fee/ns0:MaximumAmount">
																						<CurrencyAmountValue>
																							<xsl:for-each select="@CurCode">
																								<xsl:attribute name="Code" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:value-of select="number(.)"/>
																						</CurrencyAmountValue>
																					</xsl:for-each>
																					<AmountApplication>
																						<xsl:value-of select="'MAX'"/>
																					</AmountApplication>
																					<ApplicableFeeRemarks>
																						<xsl:for-each select="ns0:DescText">
																							<Remark>
																								<xsl:value-of select="."/>
																							</Remark>
																						</xsl:for-each>
																					</ApplicableFeeRemarks>
																				</Amount>
																			</Amounts>
																		</Detail>
																	</xsl:for-each>
																</xsl:for-each>
																<xsl:for-each select="ns0:FareComponent">
																	<xsl:for-each select="ns0:ChangeRestrictions">
																		<xsl:variable name="var295_idx" select="position()"/>
																		<Detail>
																			<xsl:attribute name="refs" namespace="">
																				<xsl:value-of select="concat('RULE', position())"/>
																			</xsl:attribute>
																			<Type>
																				<xsl:value-of select="'Change'"/>
																			</Type>
																			<xsl:for-each select="ns0:JourneyStageCode">
																				<xsl:for-each select="$var294_cur/ns0:DescText">
																					<xsl:choose>
																						<xsl:when test="(($var296_cur = 'No Show') and contains(., 'before departure'))">
																							<Application>
																								<xsl:value-of select="12"/>
																							</Application>
																						</xsl:when>
																						<xsl:when test="(($var296_cur = 'No Show') and contains(., 'after departure'))">
																							<Application>
																								<xsl:value-of select="13"/>
																							</Application>
																						</xsl:when>
																						<xsl:when test="($var296_cur = 'Prior To Departure')">
																							<Application>
																								<xsl:value-of select="2"/>
																							</Application>
																						</xsl:when>
																						<xsl:when test="($var296_cur = 'After Departure')">
																							<Application>
																								<xsl:value-of select="3"/>
																							</Application>
																						</xsl:when>
																					</xsl:choose>
																				</xsl:for-each>
																			</xsl:for-each>
																			<Amounts>
																				<Amount>
																					<xsl:for-each select="ns0:Fee/ns0:MinimumAmount">
																						<CurrencyAmountValue>
																							<xsl:for-each select="@CurCode">
																								<xsl:attribute name="Code" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:value-of select="number(.)"/>
																						</CurrencyAmountValue>
																					</xsl:for-each>
																					<AmountApplication>
																						<xsl:value-of select="'MIN'"/>
																					</AmountApplication>
																					<ApplicableFeeRemarks>
																						<xsl:for-each select="ns0:DescText">
																							<Remark>
																								<xsl:value-of select="."/>
																							</Remark>
																						</xsl:for-each>
																					</ApplicableFeeRemarks>
																				</Amount>
																				<Amount>
																					<xsl:for-each select="ns0:Fee/ns0:MaximumAmount">
																						<CurrencyAmountValue>
																							<xsl:for-each select="@CurCode">
																								<xsl:attribute name="Code" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:value-of select="number(.)"/>
																						</CurrencyAmountValue>
																					</xsl:for-each>
																					<AmountApplication>
																						<xsl:value-of select="'MAX'"/>
																					</AmountApplication>
																					<ApplicableFeeRemarks>
																						<xsl:for-each select="ns0:DescText">
																							<Remark>
																								<xsl:value-of select="."/>
																							</Remark>
																						</xsl:for-each>
																					</ApplicableFeeRemarks>
																				</Amount>
																			</Amounts>
																		</Detail>
																	</xsl:for-each>
																</xsl:for-each>
															</Details>
														</Penalty>
													</FareRules>
													<xsl:for-each select="ns0:FareComponent/ns0:PriceClassRefID">
														<PriceClassRef>
															<xsl:value-of select="."/>
														</PriceClassRef>
													</xsl:for-each>
													<xsl:for-each select="ns0:FareComponent/ns0:PaxSegmentRefID">
														<SegmentRefs>
															<xsl:value-of select="."/>
														</SegmentRefs>
													</xsl:for-each>
												</FareComponent>
												<xsl:for-each select="ns0:FareCalculationInfo">
													<Remarks>
														<Remark>
															<xsl:value-of select="ns0:AddlInfoText"/>
														</Remark>
														<xsl:for-each select="$var5_cur/ns0:TicketDocInfo/ns0:EndorsementText">
															<Remark>
																<xsl:value-of select="."/>
															</Remark>
														</xsl:for-each>
													</Remarks>
												</xsl:for-each>
											</FareDetail>
										</xsl:for-each>
										<xsl:if test="ns0:Commission">
											<OrderItemDetails>
												<OrderItemDetail>
													<OrderCommision>
														<xsl:for-each select="ns0:Commission/ns0:Amount">
															<Amount>
																<xsl:for-each select="@CurCode">
																	<xsl:attribute name="Code" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:value-of select="number(.)"/>
															</Amount>
														</xsl:for-each>
														<xsl:for-each select="ns0:Commission/ns0:Percentage">
															<Percentage>
																<xsl:value-of select="number(.)"/>
															</Percentage>
														</xsl:for-each>
														<xsl:for-each select="ns0:Commission/ns0:CommissionCode">
															<Code>
																<xsl:value-of select="."/>
															</Code>
														</xsl:for-each>
													</OrderCommision>
												</OrderItemDetail>
											</OrderItemDetails>
										</xsl:if>
										<xsl:if test="ns0:FareDetail">
											<Price>
												<xsl:for-each select="ns0:FareDetail/ns0:Price/ns0:TotalAmount">
													<TotalAmount>
														<xsl:call-template name="tbf:tbf2_AmountType">
															<xsl:with-param name="input" select="."/>
														</xsl:call-template>
													</TotalAmount>
												</xsl:for-each>
												<xsl:for-each select="ns0:FareDetail/ns0:Price/ns0:BaseAmount">
													<BaseAmount>
														<xsl:call-template name="tbf:tbf2_AmountType">
															<xsl:with-param name="input" select="."/>
														</xsl:call-template>
													</BaseAmount>
												</xsl:for-each>
												<TaxSummary>
													<xsl:for-each select="ns0:FareDetail/ns0:Price/ns0:TaxSummary/ns0:TotalTaxAmount">
														<TotalTaxAmount>
															<xsl:call-template name="tbf:tbf2_AmountType">
																<xsl:with-param name="input" select="."/>
															</xsl:call-template>
														</TotalTaxAmount>
													</xsl:for-each>
												</TaxSummary>
											</Price>
										</xsl:if>
										<xsl:if test="not(ns0:FareDetail)">
											<Price>
												<xsl:for-each select="ns0:Price/ns0:TotalAmount">
													<TotalAmount>
														<xsl:choose>
															<xsl:when test="((. = 0) and not(@CurCode))">
																<xsl:for-each select="$var226_cur/ns0:TotalPrice/ns0:TotalAmount/@CurCode">
																	<xsl:attribute name="CurCode" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
															</xsl:when>
															<xsl:otherwise>
																<xsl:for-each select="@CurCode">
																	<xsl:attribute name="CurCode" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
															</xsl:otherwise>
														</xsl:choose>
														<xsl:value-of select="number(.)"/>
													</TotalAmount>
												</xsl:for-each>
												<xsl:for-each select="ns0:Price/ns0:BaseAmount">
													<BaseAmount>
														<xsl:call-template name="tbf:tbf2_AmountType">
															<xsl:with-param name="input" select="."/>
														</xsl:call-template>
													</BaseAmount>
												</xsl:for-each>
												<xsl:for-each select="ns0:Price/ns0:TaxSummary">
													<xsl:for-each select="ns0:TotalTaxAmount">
														<TaxSummary>
															<TotalTaxAmount>
																<xsl:call-template name="tbf:tbf2_AmountType">
																	<xsl:with-param name="input" select="."/>
																</xsl:call-template>
															</TotalTaxAmount>
															<xsl:for-each select="$var319_cur/ns0:Tax">
																<Tax>
																	<Amount>
																		<xsl:call-template name="tbf:tbf2_AmountType">
																			<xsl:with-param name="input" select="ns0:Amount"/>
																		</xsl:call-template>
																	</Amount>
																	<xsl:for-each select="ns0:TaxCode">
																		<TaxCode>
																			<xsl:value-of select="."/>
																		</TaxCode>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:AddlTaxCode">
																		<QualifierCode>
																			<xsl:value-of select="."/>
																		</QualifierCode>
																	</xsl:for-each>
																</Tax>
															</xsl:for-each>
														</TaxSummary>
													</xsl:for-each>
												</xsl:for-each>
											</Price>
										</xsl:if>
										<xsl:for-each select="ns0:Service">
											<Service>
												<ServiceID>
													<xsl:value-of select="ns0:ServiceID"/>
												</ServiceID>
												<xsl:for-each select="ns0:StatusCode">
													<StatusCode>
														<xsl:variable name="var326_nested">
															<xsl:call-template name="vmf:vmf9_inputtoresult">
																<xsl:with-param name="input" select="string(.)"/>
															</xsl:call-template>
														</xsl:variable>
														<xsl:value-of select="$var326_nested"/>
													</StatusCode>
												</xsl:for-each>
												<PaxRefID>
													<xsl:value-of select="ns0:PaxRefID"/>
												</PaxRefID>
												<xsl:for-each select="ns0:ServiceRefID">
													<ServiceRefID>
														<xsl:value-of select="."/>
													</ServiceRefID>
												</xsl:for-each>
												<ServiceAssociations>
													<xsl:for-each select="ns0:OrderServiceAssociation/ns0:SeatOnLeg">
														<SelectedSeat>
															<xsl:for-each select="ns0:SeatAssignmentAssociations/ns0:PaxSegmentRef">
																<DatedOperatingLegRefID>
																	<xsl:value-of select="ns0:PaxSegmentRefID"/>
																</DatedOperatingLegRefID>
															</xsl:for-each>
															<Seat>
																<RowNumber>
																	<xsl:value-of select="number(ns0:Seat/ns0:RowNumber)"/>
																</RowNumber>
																<ColumnID>
																	<xsl:value-of select="ns0:Seat/ns0:ColumnID"/>
																</ColumnID>
																<xsl:for-each select="ns0:Seat/ns0:SeatProfileRefID">
																	<SeatProfileRefID>
																		<xsl:value-of select="."/>
																	</SeatProfileRefID>
																</xsl:for-each>
															</Seat>
														</SelectedSeat>
													</xsl:for-each>
													<xsl:for-each select="ns0:OrderServiceAssociation/ns0:ServiceDefinitionRef">
														<ServiceDefinitionRef>
															<ServiceDefinitionRefID>
																<xsl:value-of select="ns0:ServiceDefinitionRefID"/>
															</ServiceDefinitionRefID>
															<xsl:for-each select="ns0:OrderFlightAssociations/ns0:PaxSegmentRef">
																<PaxSegmentRefID>
																	<xsl:value-of select="ns0:PaxSegmentRefID"/>
																</PaxSegmentRefID>
															</xsl:for-each>
														</ServiceDefinitionRef>
													</xsl:for-each>
													<xsl:for-each select="$var5_cur/ns0:DataLists/ns0:ServiceDefinitionList/ns0:ServiceDefinition">
														<xsl:variable name="var334_nested">
															<xsl:for-each select="ns0:ServiceDefinitionAssociation/ns0:SeatProfileRef/ns0:SeatProfileRefID">
																<xsl:for-each select="$var324_cur/ns0:OrderServiceAssociation/ns0:SeatOnLeg/ns0:Seat/ns0:SeatProfileRefID">
																	<xsl:value-of select="number((string($var335_cur) = string(.)))"/>
																</xsl:for-each>
															</xsl:for-each>
														</xsl:variable>
														<xsl:if test="boolean(translate(normalize-space($var334_nested), ' 0', ''))">
															<ServiceDefinitionRef>
																<ServiceDefinitionRefID>
																	<xsl:value-of select="ns0:ServiceDefinitionID"/>
																</ServiceDefinitionRefID>
																<xsl:for-each select="$var324_cur/ns0:OrderServiceAssociation/ns0:SeatOnLeg/ns0:SeatAssignmentAssociations/ns0:PaxSegmentRef">
																	<PaxSegmentRefID>
																		<xsl:value-of select="ns0:PaxSegmentRefID"/>
																	</PaxSegmentRefID>
																</xsl:for-each>
															</ServiceDefinitionRef>
														</xsl:if>
													</xsl:for-each>
													<xsl:for-each select="ns0:OrderServiceAssociation/ns0:PaxSegmentRef">
														<PaxSegmentRefID>
															<xsl:value-of select="ns0:PaxSegmentRefID"/>
														</PaxSegmentRefID>
													</xsl:for-each>
												</ServiceAssociations>
											</Service>
										</xsl:for-each>
									</OrderItem>
								</xsl:for-each>
							</xsl:for-each>
							<xsl:for-each select="$var4_cur/ns1:PaymentFunctions">
								<PaymentInfo>
									<xsl:for-each select="ns0:PaymentProcessingSummary">
										<Amount>
											<xsl:for-each select="ns0:Amount/@CurCode">
												<xsl:attribute name="CurCode" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:value-of select="number(ns0:Amount)"/>
										</Amount>
									</xsl:for-each>
									<xsl:variable name="var342_nested">
										<xsl:for-each select="ns0:PaymentProcessingSummary">
											<xsl:value-of select="number(boolean(ns0:PaymentProcessingSummaryPaymentMethod/ns0:IATA_EasyPay))"/>
										</xsl:for-each>
									</xsl:variable>
									<xsl:choose>
										<xsl:when test="boolean(translate(normalize-space($var342_nested), ' 0', ''))">
											<TypeCode>
												<xsl:value-of select="'CC'"/>
											</TypeCode>
										</xsl:when>
										<xsl:when test="ns0:PaymentSupportedMethod">
											<TypeCode>
												<xsl:value-of select="ns0:PaymentSupportedMethod/ns0:PaymentTypeCode"/>
											</TypeCode>
										</xsl:when>
										<xsl:otherwise>
											<xsl:for-each select="ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:SettlementPlan">
												<TypeCode>
													<xsl:value-of select="ns0:PaymentTypeCode"/>
												</TypeCode>
											</xsl:for-each>
										</xsl:otherwise>
									</xsl:choose>
									<PaymentMethod>
										<xsl:variable name="var345_nested">
											<xsl:choose>
												<xsl:when test="ns0:PaymentSupportedMethod">
													<xsl:value-of select="number((ns0:PaymentSupportedMethod/ns0:PaymentTypeCode = 'CASH'))"/>
												</xsl:when>
												<xsl:otherwise>
													<xsl:for-each select="ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:SettlementPlan">
														<xsl:value-of select="number((ns0:PaymentTypeCode = 'CASH'))"/>
													</xsl:for-each>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<xsl:if test="boolean(translate(normalize-space($var345_nested), ' 0', ''))">
											<Cash/>
										</xsl:if>
										<xsl:for-each select="ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:PaymentCard">
											<PaymentCard>
												<xsl:for-each select="ns0:MaskedCardID">
													<MaskedCardID>
														<xsl:value-of select="."/>
													</MaskedCardID>
												</xsl:for-each>
												<xsl:for-each select="ns0:CardBrandCode">
													<CreditCardVendorCode>
														<xsl:value-of select="."/>
													</CreditCardVendorCode>
												</xsl:for-each>
												<xsl:for-each select="ns0:ExpirationDate">
													<ExpirationDate>
														<xsl:value-of select="."/>
													</ExpirationDate>
												</xsl:for-each>
											</PaymentCard>
										</xsl:for-each>
										<xsl:for-each select="ns0:PaymentProcessingSummary/ns0:PaymentProcessingSummaryPaymentMethod/ns0:IATA_EasyPay">
											<PaymentCard>
												<CreditCardVendorCode>
													<xsl:value-of select="'EP'"/>
												</CreditCardVendorCode>
											</PaymentCard>
										</xsl:for-each>
									</PaymentMethod>
								</PaymentInfo>
							</xsl:for-each>
							<TotalPrice>
								<xsl:for-each select="ns0:Order/ns0:TotalPrice/ns0:TotalAmount">
									<TotalAmount>
										<xsl:call-template name="tbf:tbf2_AmountType">
											<xsl:with-param name="input" select="."/>
										</xsl:call-template>
									</TotalAmount>
								</xsl:for-each>
								<xsl:for-each select="ns0:Order/ns0:TotalPrice/ns0:BaseAmount">
									<BaseAmount>
										<xsl:call-template name="tbf:tbf2_AmountType">
											<xsl:with-param name="input" select="."/>
										</xsl:call-template>
									</BaseAmount>
								</xsl:for-each>
								<TaxSummary>
									<xsl:for-each select="ns0:Order/ns0:TotalPrice/ns0:TaxSummary/ns0:TotalTaxAmount">
										<TotalTaxAmount>
											<xsl:call-template name="tbf:tbf2_AmountType">
												<xsl:with-param name="input" select="."/>
											</xsl:call-template>
										</TotalTaxAmount>
									</xsl:for-each>
								</TaxSummary>
							</TotalPrice>
						</Order>
						<xsl:variable name="var355_nested">
							<xsl:for-each select="ns0:Processing/ns0:Remark">
								<xsl:value-of select="number(boolean(ns0:RemarkText))"/>
							</xsl:for-each>
						</xsl:variable>
						<xsl:if test="boolean(translate(normalize-space($var355_nested), ' 0', ''))">
							<OrderViewProcessing>
								<Remarks>
									<xsl:for-each select="ns0:Processing/ns0:Remark/ns0:RemarkText">
										<Remark>
											<xsl:value-of select="."/>
										</Remark>
									</xsl:for-each>
								</Remarks>
							</OrderViewProcessing>
						</xsl:if>
						<xsl:if test="ns0:TicketDocInfo">
							<TicketDocInfos>
								<xsl:for-each select="ns0:TicketDocInfo">
									<TicketDocInfo>
										<AgentIDs>
											<AgentID>
												<xsl:for-each select="ns0:BookingAgency/ns0:TravelAgent">
													<ID>
														<xsl:value-of select="ns0:TravelAgentID"/>
													</ID>
												</xsl:for-each>
											</AgentID>
										</AgentIDs>
										<xsl:for-each select="ns0:Ticket">
											<TicketDocument>
												<xsl:for-each select="ns0:PrimaryDocInd">
													<xsl:attribute name="PrimaryDocInd" namespace="">
														<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
													</xsl:attribute>
												</xsl:for-each>
												<xsl:for-each select="ns0:TicketNumber">
													<TicketDocNbr>
														<xsl:value-of select="."/>
													</TicketDocNbr>
												</xsl:for-each>
												<xsl:for-each select="ns0:TicketDocTypeCode">
													<Type>
														<xsl:value-of select="."/>
													</Type>
												</xsl:for-each>
												<xsl:for-each select="ns0:ConnectedDocNumber">
													<InConnectionDocNbr>
														<!--Manual Change : Remove number()-->
														<xsl:value-of select="."/>
													</InConnectionDocNbr>
												</xsl:for-each>
												<xsl:for-each select="$var358_cur/ns0:BookletQty">
													<NumberofBooklets>
														<xsl:value-of select="floor(.)"/>
													</NumberofBooklets>
												</xsl:for-each>
												<xsl:for-each select="$var358_cur/ns0:IssueInfo/ns0:IssueDate">
													<DateOfIssue>
														<xsl:value-of select="."/>
													</DateOfIssue>
												</xsl:for-each>
												<xsl:for-each select="ns0:Coupon">
													<CouponInfo>
														<CouponNumber>
															<xsl:value-of select="floor(ns0:CouponNumber)"/>
														</CouponNumber>
														<xsl:variable name="var368_nested">
															<xsl:for-each select="ns0:CurrentCouponFlightInfoRef">
																<xsl:value-of select="number(boolean(ns0:CurrentAirlinePaxSegmentRef))"/>
															</xsl:for-each>
														</xsl:variable>
														<xsl:variable name="var370_nested">
															<xsl:choose>
																<xsl:when test="boolean(translate(normalize-space($var368_nested), ' 0', ''))">
																	<xsl:for-each select="ns0:CurrentCouponFlightInfoRef/ns0:CurrentAirlinePaxSegmentRef/ns0:PaxSegmentRefID">
																		<xsl:value-of select="'1'"/>
																	</xsl:for-each>
																</xsl:when>
																<xsl:otherwise>
																	<xsl:variable name="var372_nested">
																		<xsl:for-each select="ns0:CurrentCouponFlightInfoRef">
																			<xsl:value-of select="number(boolean(ns0:CheckedInAirlinePaxSegmentRef))"/>
																		</xsl:for-each>
																	</xsl:variable>
																	<xsl:choose>
																		<xsl:when test="boolean(translate(normalize-space($var372_nested), ' 0', ''))">
																			<xsl:for-each select="ns0:CurrentCouponFlightInfoRef/ns0:CheckedInAirlinePaxSegmentRef/ns0:PaxSegmentRefID">
																				<xsl:value-of select="'1'"/>
																			</xsl:for-each>
																		</xsl:when>
																		<xsl:otherwise>
																			<xsl:variable name="var375_nested">
																				<xsl:for-each select="ns0:CurrentCouponFlightInfoRef">
																					<xsl:value-of select="number(boolean(ns0:FlownAirlinePaxSegmentRef))"/>
																				</xsl:for-each>
																			</xsl:variable>
																			<xsl:if test="boolean(translate(normalize-space($var375_nested), ' 0', ''))">
																				<xsl:for-each select="ns0:CurrentCouponFlightInfoRef/ns0:FlownAirlinePaxSegmentRef/ns0:PaxSegmentRefID">
																					<xsl:value-of select="'1'"/>
																				</xsl:for-each>
																			</xsl:if>
																		</xsl:otherwise>
																	</xsl:choose>
																</xsl:otherwise>
															</xsl:choose>
														</xsl:variable>
														<xsl:if test="boolean(translate(normalize-space($var370_nested), ' 0', ''))">
															<CouponReference>
																<xsl:variable name="var378_nested">
																	<xsl:for-each select="ns0:CurrentCouponFlightInfoRef">
																		<xsl:value-of select="number(boolean(ns0:CurrentAirlinePaxSegmentRef))"/>
																	</xsl:for-each>
																</xsl:variable>
																<xsl:choose>
																	<xsl:when test="boolean(translate(normalize-space($var378_nested), ' 0', ''))">
																		<xsl:for-each select="ns0:CurrentCouponFlightInfoRef/ns0:CurrentAirlinePaxSegmentRef/ns0:PaxSegmentRefID">
																			<xsl:value-of select="."/>
																		</xsl:for-each>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:variable name="var381_nested">
																			<xsl:for-each select="ns0:CurrentCouponFlightInfoRef">
																				<xsl:value-of select="number(boolean(ns0:CheckedInAirlinePaxSegmentRef))"/>
																			</xsl:for-each>
																		</xsl:variable>
																		<xsl:choose>
																			<xsl:when test="boolean(translate(normalize-space($var381_nested), ' 0', ''))">
																				<xsl:for-each select="ns0:CurrentCouponFlightInfoRef/ns0:CheckedInAirlinePaxSegmentRef/ns0:PaxSegmentRefID">
																					<xsl:value-of select="."/>
																				</xsl:for-each>
																			</xsl:when>
																			<xsl:otherwise>
																				<xsl:variable name="var384_nested">
																					<xsl:for-each select="ns0:CurrentCouponFlightInfoRef">
																						<xsl:value-of select="number(boolean(ns0:FlownAirlinePaxSegmentRef))"/>
																					</xsl:for-each>
																				</xsl:variable>
																				<xsl:if test="boolean(translate(normalize-space($var384_nested), ' 0', ''))">
																					<xsl:for-each select="ns0:CurrentCouponFlightInfoRef/ns0:FlownAirlinePaxSegmentRef/ns0:PaxSegmentRefID">
																						<xsl:value-of select="."/>
																					</xsl:for-each>
																				</xsl:if>
																			</xsl:otherwise>
																		</xsl:choose>
																	</xsl:otherwise>
																</xsl:choose>
															</CouponReference>
														</xsl:if>
														<xsl:for-each select="ns0:FareBasisCode">
															<FareBasisCode>
																<Code>
																	<xsl:value-of select="."/>
																</Code>
															</FareBasisCode>
														</xsl:for-each>
														<xsl:for-each select="ns0:CouponStatusCode">
															<Status>
																<xsl:value-of select="."/>
															</Status>
														</xsl:for-each>
														<xsl:for-each select="ns0:ServiceRefID">
															<ServiceReferences>
																<xsl:value-of select="."/>
															</ServiceReferences>
														</xsl:for-each>
														<xsl:if test="(boolean($var360_cur/ns0:ConnectedDocNumber) and boolean(ns0:ConnectedCouponNumber))">
															<InConnectionWithInfo>
																<xsl:for-each select="$var360_cur/ns0:ConnectedDocNumber">
																	<InConnectionDocNbr>
																		<!--Manual Change : Remove number()-->
																		<xsl:value-of select="."/>
																	</InConnectionDocNbr>
																</xsl:for-each>
																<xsl:for-each select="ns0:ConnectedCouponNumber">
																	<InConnectonCpnNbr>
																		<xsl:value-of select="floor(.)"/>
																	</InConnectonCpnNbr>
																</xsl:for-each>
															</InConnectionWithInfo>
														</xsl:if>
														<xsl:if test="(boolean(ns0:RFIC) and boolean(ns0:RFISC))">
															<ReasonForIssuance>
																<xsl:for-each select="ns0:RFIC">
																	<RFIC>
																		<xsl:value-of select="."/>
																	</RFIC>
																</xsl:for-each>
																<xsl:for-each select="ns0:RFISC">
																	<Code>
																		<xsl:value-of select="."/>
																	</Code>
																</xsl:for-each>
															</ReasonForIssuance>
														</xsl:if>
														<xsl:for-each select="$var5_cur/ns0:DataLists/ns0:BaggageAllowanceList/ns0:BaggageAllowance">
															<xsl:variable name="var395_nested">
																<xsl:for-each select="$var367_cur/ns0:BaggageAllowanceRefID">
																	<xsl:value-of select="number((string(.) = string($var394_filter/ns0:BaggageAllowanceID)))"/>
																</xsl:for-each>
															</xsl:variable>
															<xsl:if test="boolean(translate(normalize-space($var395_nested), ' 0', ''))">
																<AddlBaggageInfo>
																	<xsl:for-each select="ns0:PieceAllowance">
																		<xsl:variable name="var398_nested">
																			<xsl:for-each select="$var367_cur/ns0:BaggageAllowanceRefID">
																				<xsl:value-of select="number((string(.) = string($var394_filter/ns0:BaggageAllowanceID)))"/>
																			</xsl:for-each>
																		</xsl:variable>
																		<xsl:if test="boolean(translate(normalize-space($var398_nested), ' 0', ''))">
																			<AllowableBag>
																				<xsl:attribute name="Number" namespace="">
																					<xsl:value-of select="floor(ns0:TotalQty)"/>
																				</xsl:attribute>
																			</AllowableBag>
																		</xsl:if>
																	</xsl:for-each>
																	<xsl:variable name="var400_nested">
																		<xsl:for-each select="ns0:WeightAllowance">
																			<xsl:value-of select="number(boolean(ns0:TotalMaximumWeightMeasure))"/>
																		</xsl:for-each>
																	</xsl:variable>
																	<xsl:variable name="var402_nested">
																		<xsl:choose>
																			<xsl:when test="boolean(translate(normalize-space($var400_nested), ' 0', ''))">
																				<xsl:for-each select="ns0:WeightAllowance/ns0:TotalMaximumWeightMeasure">
																					<xsl:value-of select="'1'"/>
																				</xsl:for-each>
																			</xsl:when>
																			<xsl:otherwise>
																				<xsl:variable name="var404_nested">
																					<xsl:for-each select="ns0:WeightAllowance">
																						<xsl:value-of select="number(boolean(ns0:MaximumWeightMeasure))"/>
																					</xsl:for-each>
																				</xsl:variable>
																				<xsl:if test="boolean(translate(normalize-space($var404_nested), ' 0', ''))">
																					<xsl:for-each select="ns0:WeightAllowance/ns0:MaximumWeightMeasure">
																						<xsl:value-of select="'1'"/>
																					</xsl:for-each>
																				</xsl:if>
																			</xsl:otherwise>
																		</xsl:choose>
																	</xsl:variable>
																	<xsl:if test="boolean(translate(normalize-space($var402_nested), ' 0', ''))">
																		<xsl:for-each select="ns0:WeightAllowance">
																			<xsl:variable name="var408_nested">
																				<xsl:for-each select="$var367_cur/ns0:BaggageAllowanceRefID">
																					<xsl:value-of select="number((string(.) = string($var394_filter/ns0:BaggageAllowanceID)))"/>
																				</xsl:for-each>
																			</xsl:variable>
																			<xsl:if test="boolean(translate(normalize-space($var408_nested), ' 0', ''))">
																				<CheckedFree>
																					<xsl:attribute name="MaxBagWght" namespace="">
																						<xsl:variable name="var410_nested">
																							<xsl:for-each select="$var394_filter/ns0:WeightAllowance">
																								<xsl:value-of select="number(boolean(ns0:TotalMaximumWeightMeasure))"/>
																							</xsl:for-each>
																						</xsl:variable>
																						<xsl:variable name="var412_nested">
																							<xsl:choose>
																								<xsl:when test="boolean(translate(normalize-space($var410_nested), ' 0', ''))">
																									<xsl:for-each select="$var394_filter/ns0:WeightAllowance/ns0:TotalMaximumWeightMeasure">
																										<xsl:value-of select="number(.)"/>
																									</xsl:for-each>
																								</xsl:when>
																								<xsl:otherwise>
																									<xsl:variable name="var414_nested">
																										<xsl:for-each select="$var394_filter/ns0:WeightAllowance">
																											<xsl:value-of select="number(boolean(ns0:MaximumWeightMeasure))"/>
																										</xsl:for-each>
																									</xsl:variable>
																									<xsl:if test="boolean(translate(normalize-space($var414_nested), ' 0', ''))">
																										<xsl:for-each select="$var394_filter/ns0:WeightAllowance/ns0:MaximumWeightMeasure">
																											<xsl:value-of select="number(.)"/>
																										</xsl:for-each>
																									</xsl:if>
																								</xsl:otherwise>
																							</xsl:choose>
																						</xsl:variable>
																						<xsl:value-of select="concat($var412_nested, substring(ns0:WeightUnitOfMeasurement, 1, 1))"/>
																					</xsl:attribute>
																				</CheckedFree>
																			</xsl:if>
																		</xsl:for-each>
																	</xsl:if>
																</AddlBaggageInfo>
															</xsl:if>
														</xsl:for-each>
													</CouponInfo>
												</xsl:for-each>
												<ReportingType>
													<xsl:value-of select="ns0:ReportingTypeCode"/>
												</ReportingType>
											</TicketDocument>
										</xsl:for-each>
										<PassengerReference>
											<xsl:value-of select="ns0:PaxRefID"/>
										</PassengerReference>
									</TicketDocInfo>
								</xsl:for-each>
							</TicketDocInfos>
						</xsl:if>
						<xsl:for-each select="ns0:Warning">
							<Warning>
								<xsl:for-each select="ns0:Code">
									<Code>
										<xsl:value-of select="."/>
									</Code>
								</xsl:for-each>
								<xsl:for-each select="ns0:DescText">
									<DescText>
										<xsl:value-of select="."/>
									</DescText>
								</xsl:for-each>
								<LanguageCode>
									<xsl:value-of select="ns0:LangCode"/>
								</LanguageCode>
								<xsl:for-each select="ns0:OwnerName">
									<OwnerName>
										<xsl:value-of select="."/>
									</OwnerName>
								</xsl:for-each>
								<xsl:for-each select="ns0:StatusText">
									<StatusText>
										<xsl:value-of select="."/>
									</StatusText>
								</xsl:for-each>
								<xsl:for-each select="ns0:TagText">
									<TagText>
										<xsl:value-of select="."/>
									</TagText>
								</xsl:for-each>
								<xsl:for-each select="ns0:TypeCode">
									<TypeCode>
										<xsl:value-of select="."/>
									</TypeCode>
								</xsl:for-each>
								<xsl:for-each select="ns0:URL">
									<URL>
										<xsl:value-of select="."/>
									</URL>
								</xsl:for-each>
							</Warning>
						</xsl:for-each>
					</Response>
				</xsl:for-each>
			</xsl:for-each>
			<xsl:variable name="var425_nested">
				<xsl:for-each select="ns1:IATA_OrderViewRS">
					<xsl:value-of select="number(boolean(ns1:Error))"/>
				</xsl:for-each>
			</xsl:variable>
			<xsl:if test="boolean(translate(normalize-space($var425_nested), ' 0', ''))">
				<Errors>
					<xsl:for-each select="ns1:IATA_OrderViewRS/ns1:Error">
						<Error>
							<xsl:for-each select="ns0:Code">
								<Code>
									<xsl:value-of select="."/>
								</Code>
							</xsl:for-each>
							<xsl:for-each select="ns0:DescText">
								<DescText>
									<xsl:value-of select="."/>
								</DescText>
							</xsl:for-each>
							<LanguageCode>
								<xsl:value-of select="ns0:LangCode"/>
							</LanguageCode>
							<xsl:for-each select="ns0:OwnerName">
								<OwnerName>
									<xsl:value-of select="."/>
								</OwnerName>
							</xsl:for-each>
							<xsl:for-each select="ns0:StatusText">
								<StatusText>
									<xsl:value-of select="."/>
								</StatusText>
							</xsl:for-each>
							<xsl:for-each select="ns0:TagText">
								<TagText>
									<xsl:value-of select="."/>
								</TagText>
							</xsl:for-each>
							<TypeCode>
								<xsl:value-of select="ns0:TypeCode"/>
							</TypeCode>
							<xsl:for-each select="ns0:URL">
								<URL>
									<xsl:value-of select="."/>
								</URL>
							</xsl:for-each>
						</Error>
					</xsl:for-each>
					<xsl:for-each select="ns1:IATA_OrderViewRS/ns1:Error">
						<Error>
							<xsl:for-each select="ns0:Code">
								<Code>
									<xsl:value-of select="."/>
								</Code>
							</xsl:for-each>
							<xsl:for-each select="ns0:DescText">
								<DescText>
									<xsl:value-of select="."/>
								</DescText>
							</xsl:for-each>
							<LanguageCode>
								<xsl:value-of select="ns0:LangCode"/>
							</LanguageCode>
							<OwnerName>
								<xsl:value-of select="'1A'"/>
							</OwnerName>
							<xsl:for-each select="ns0:StatusText">
								<StatusText>
									<xsl:value-of select="."/>
								</StatusText>
							</xsl:for-each>
							<xsl:for-each select="ns0:TagText">
								<TagText>
									<xsl:value-of select="."/>
								</TagText>
							</xsl:for-each>
							<TypeCode>
								<xsl:value-of select="ns0:TypeCode"/>
							</TypeCode>
							<xsl:for-each select="ns0:URL">
								<URL>
									<xsl:value-of select="."/>
								</URL>
							</xsl:for-each>
						</Error>
					</xsl:for-each>
				</Errors>
			</xsl:if>
		</AMA_TravelOrderViewRS>
	</xsl:template>
</xsl:stylesheet>