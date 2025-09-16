<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:vmf="http://www.altova.com/MapForce/UDF/vmf" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:ext="http://exslt.org/common" version="1.0" exclude-result-prefixes="vmf xs ext">
	<!-- Manual change start: Add Xslt Lib -->
	<xsl:import href="xslt/common/XsltLib.xslt"/>
	<!-- Manual change end: Add Xslt Lib -->
	<xsl:template name="vmf:vmf1_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="not($input='GST' or $input='CTC')"/>
	</xsl:template>
	<xsl:template name="vmf:vmf2_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="not($input='GST' or $input='CTC')"/>
	</xsl:template>
	<xsl:template name="vmf:vmf3_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='CTC'">
				<xsl:value-of select="'NTF'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$input"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf4_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='CTC'">
				<xsl:value-of select="'NTF'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$input"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf5_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="not($input='GST' or $input='CTC')"/>
	</xsl:template>
	<xsl:template name="vmf:vmf6_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="not($input='GST' or $input='CTC')"/>
	</xsl:template>
	<xsl:template name="vmf:vmf7_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:value-of select="not($input='GST' or $input='CTC')"/>
	</xsl:template>
	<xsl:template name="vmf:vmf8_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='Male' or $input='Female' or $input='Undisclosed' or $input='Unspecified'">
				<xsl:value-of select="substring('MFUX', 1 + boolean($input='Female') + 2 * boolean($input='Undisclosed') + 3 * boolean($input='Unspecified'), 1)"/>
			</xsl:when>
			<xsl:otherwise>
				<!-- Manual change start: remove xs:string -->
				<xsl:value-of select="$input"/>
				<!-- Manual change end -->
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf9_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='CTC'">
				<xsl:value-of select="'NTF'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$input"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf10_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='CTC'">
				<xsl:value-of select="'NTF'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$input"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf11_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='CTC'">
				<xsl:value-of select="'NTF'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$input"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf12_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='MALE'">
				<xsl:value-of select="'M'"/>
			</xsl:when>
			<xsl:when test="$input='FEMALE'">
				<xsl:value-of select="'F'"/>
			</xsl:when>
			<xsl:when test="$input='UNDISCLOSED'">
				<xsl:value-of select="'U'"/>
			</xsl:when>
			<xsl:when test="$input='UNSPECIFIED' or $input='OTHER'">
				<xsl:value-of select="'X'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="'U'"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:template name="vmf:vmf13_inputtoresult">
		<xsl:param name="input" select="/.."/>
		<xsl:choose>
			<xsl:when test="$input='CTC'">
				<xsl:value-of select="'NTF'"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$input"/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<IATA_OrderCreateRQ xmlns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersMessage" xmlns:cns="http://www.iata.org/IATA/2015/EASD/00/IATA_OffersAndOrdersCommonTypes" xmlns:dsig="http://www.w3.org/2000/09/xmldsig#">
			<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']">
				<DistributionChain>
					<cns:DistributionChainLink>
						<cns:ContactInfo>
							<cns:ContactInfoID>
								<xsl:value-of select="'AgencyContact-1'"/>
							</cns:ContactInfoID>
							<xsl:for-each select="*[local-name()='TravelAgency' and namespace-uri()='']/*[local-name()='Contact' and namespace-uri()='']/*[local-name()='Email' and namespace-uri()='']">
								<cns:EmailAddress>
									<xsl:for-each select="*[local-name()='EmailAddress' and namespace-uri()='']">
										<cns:EmailAddressText>
											<xsl:value-of select="."/>
										</cns:EmailAddressText>
									</xsl:for-each>
								</cns:EmailAddress>
							</xsl:for-each>
							<xsl:variable name="var5_nested">
								<xsl:for-each select="*[local-name()='TravelAgency' and namespace-uri()='']/*[local-name()='Contact' and namespace-uri()='']">
									<xsl:value-of select="number(boolean(*[local-name()='Email' and namespace-uri()='']))"/>
								</xsl:for-each>
							</xsl:variable>
							<xsl:if test="not(boolean(translate(normalize-space($var5_nested), ' 0', '')))">
								<cns:EmailAddress>
									<cns:EmailAddressText>
										<xsl:value-of select="'NONE'"/>
									</cns:EmailAddressText>
								</cns:EmailAddress>
							</xsl:if>
							<xsl:for-each select="*[local-name()='TravelAgency' and namespace-uri()='']/*[local-name()='Contact' and namespace-uri()='']/*[local-name()='Phone' and namespace-uri()='']">
								<cns:Phone>
									<xsl:for-each select="*[local-name()='PhoneNumber' and namespace-uri()='']">
										<cns:PhoneNumber>
											<xsl:value-of select="."/>
										</cns:PhoneNumber>
									</xsl:for-each>
								</cns:Phone>
							</xsl:for-each>
							<xsl:variable name="var9_nested">
								<xsl:for-each select="*[local-name()='TravelAgency' and namespace-uri()='']/*[local-name()='Contact' and namespace-uri()='']">
									<xsl:value-of select="number(boolean(*[local-name()='Phone' and namespace-uri()='']))"/>
								</xsl:for-each>
							</xsl:variable>
							<xsl:if test="not(boolean(translate(normalize-space($var9_nested), ' 0', '')))">
								<cns:Phone>
									<cns:PhoneNumber>
										<xsl:value-of select="'NONE'"/>
									</cns:PhoneNumber>
								</cns:Phone>
							</xsl:if>
							<xsl:for-each select="*[local-name()='TravelAgency' and namespace-uri()='']/*[local-name()='Contact' and namespace-uri()='']/*[local-name()='Address' and namespace-uri()='']">
								<cns:PostalAddress>
									<xsl:for-each select="*[local-name()='CityName' and namespace-uri()='']">
										<cns:CityName>
											<xsl:value-of select="."/>
										</cns:CityName>
									</xsl:for-each>
									<xsl:for-each select="*[local-name()='CountryCode' and namespace-uri()='']">
										<cns:CountryCode>
											<xsl:value-of select="."/>
										</cns:CountryCode>
									</xsl:for-each>
									<xsl:for-each select="*[local-name()='Zip' and namespace-uri()='']">
										<cns:PostalCode>
											<xsl:value-of select="."/>
										</cns:PostalCode>
									</xsl:for-each>
									<xsl:for-each select="*[local-name()='line' and namespace-uri()='']">
										<cns:StreetText>
											<xsl:value-of select="."/>
										</cns:StreetText>
									</xsl:for-each>
								</cns:PostalAddress>
							</xsl:for-each>
						</cns:ContactInfo>
						<cns:Ordinal>
							<xsl:value-of select="number('1')"/>
						</cns:Ordinal>
						<cns:OrgRole>
							<xsl:value-of select="'Seller'"/>
						</cns:OrgRole>
						<cns:ParticipatingOrg>
							<cns:Name>
								<xsl:value-of select="*[local-name()='TravelAgency' and namespace-uri()='']/*[local-name()='Name' and namespace-uri()='']"/>
							</cns:Name>
							<xsl:for-each select="*[local-name()='TravelAgency' and namespace-uri()='']/*[local-name()='IATA_Number' and namespace-uri()='']">
								<cns:OrgID>
									<xsl:value-of select="."/>
								</cns:OrgID>
							</xsl:for-each>
						</cns:ParticipatingOrg>
					</cns:DistributionChainLink>
					<cns:DistributionChainLink>
						<cns:Ordinal>
							<xsl:value-of select="number('2')"/>
						</cns:Ordinal>
						<cns:OrgRole>
							<xsl:value-of select="'Distributor'"/>
						</cns:OrgRole>
						<cns:ParticipatingOrg>
							<cns:OrgID>
								<xsl:value-of select="'1A'"/>
							</cns:OrgID>
						</cns:ParticipatingOrg>
					</cns:DistributionChainLink>
					<cns:DistributionChainLink>
						<cns:Ordinal>
							<xsl:value-of select="number('3')"/>
						</cns:Ordinal>
						<cns:OrgRole>
							<xsl:value-of select="'Carrier'"/>
						</cns:OrgRole>
						<cns:ParticipatingOrg>
							<cns:OrgID>
								<xsl:value-of select="*[local-name()='target' and namespace-uri()='']"/>
							</cns:OrgID>
						</cns:ParticipatingOrg>
					</cns:DistributionChainLink>
				</DistributionChain>
			</xsl:for-each>
			<PayloadAttributes>
				<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='Context' and namespace-uri()='']/*[local-name()='correlationID' and namespace-uri()='']">
					<cns:CorrelationID>
						<xsl:value-of select="."/>
					</cns:CorrelationID>
				</xsl:for-each>
				<cns:VersionNumber>
					<xsl:value-of select="number('21.3')"/>
				</cns:VersionNumber>
			</PayloadAttributes>
			<POS/>
			<Request>
				<cns:CreateOrder>
					<cns:AcceptSelectedQuotedOfferList>
						<cns:SelectedPricedOffer>
							<xsl:variable name="var18_nested">
								<xsl:choose>
									<xsl:when test="(count(*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']) = 1)">
										<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']/*[local-name()='ID' and namespace-uri()='']">
											<xsl:value-of select="'1'"/>
										</xsl:for-each>
									</xsl:when>
									<xsl:otherwise>
										<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']">
											<xsl:for-each select="*[local-name()='ID' and namespace-uri()='']">
												<xsl:variable name="var22_nested">
													<xsl:for-each select="$var20_cur/*[local-name()='product' and namespace-uri()='']">
														<xsl:value-of select="number(boolean(*[local-name()='EST' and namespace-uri()='']))"/>
													</xsl:for-each>
												</xsl:variable>
												<xsl:if test="not(boolean(translate(normalize-space($var22_nested), ' 0', '')))">
													<xsl:value-of select="'1'"/>
												</xsl:if>
											</xsl:for-each>
										</xsl:for-each>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:variable>
							<xsl:if test="boolean(translate(normalize-space($var18_nested), ' 0', ''))">
								<cns:OfferRefID>
									<xsl:choose>
										<xsl:when test="(count(*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']) = 1)">
											<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']/*[local-name()='ID' and namespace-uri()='']">
												<xsl:value-of select="."/>
											</xsl:for-each>
										</xsl:when>
										<xsl:otherwise>
											<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']">
												<xsl:for-each select="*[local-name()='ID' and namespace-uri()='']">
													<xsl:variable name="var27_nested">
														<xsl:for-each select="$var25_cur/*[local-name()='product' and namespace-uri()='']">
															<xsl:value-of select="number(boolean(*[local-name()='EST' and namespace-uri()='']))"/>
														</xsl:for-each>
													</xsl:variable>
													<xsl:if test="not(boolean(translate(normalize-space($var27_nested), ' 0', '')))">
														<xsl:value-of select="."/>
													</xsl:if>
												</xsl:for-each>
											</xsl:for-each>
										</xsl:otherwise>
									</xsl:choose>
								</cns:OfferRefID>
							</xsl:if>
							<xsl:variable name="var29_nested">
								<xsl:choose>
									<xsl:when test="(count(*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']) = 1)">
										<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']/*[local-name()='property' and namespace-uri()='']">
											<xsl:for-each select="(./*[local-name()='value' and namespace-uri()=''])[($var30_cur/*[local-name()='key' and namespace-uri()=''] = 'OwnerCode')]">
												<xsl:value-of select="'1'"/>
											</xsl:for-each>
										</xsl:for-each>
									</xsl:when>
									<xsl:otherwise>
										<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']">
											<xsl:for-each select="*[local-name()='property' and namespace-uri()='']">
												<xsl:for-each select="*[local-name()='value' and namespace-uri()='']">
													<xsl:variable name="var35_nested">
														<xsl:for-each select="$var32_cur/*[local-name()='product' and namespace-uri()='']">
															<xsl:value-of select="number(boolean(*[local-name()='EST' and namespace-uri()='']))"/>
														</xsl:for-each>
													</xsl:variable>
													<xsl:if test="(not(boolean(translate(normalize-space($var35_nested), ' 0', ''))) and ($var33_cur/*[local-name()='key' and namespace-uri()=''] = 'OwnerCode'))">
														<xsl:value-of select="'1'"/>
													</xsl:if>
												</xsl:for-each>
											</xsl:for-each>
										</xsl:for-each>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:variable>
							<xsl:if test="boolean(translate(normalize-space($var29_nested), ' 0', ''))">
								<cns:OwnerCode>
									<xsl:choose>
										<xsl:when test="(count(*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']) = 1)">
											<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']/*[local-name()='property' and namespace-uri()='']">
												<xsl:for-each select="(./*[local-name()='value' and namespace-uri()=''])[($var37_cur/*[local-name()='key' and namespace-uri()=''] = 'OwnerCode')]">
													<xsl:value-of select="."/>
												</xsl:for-each>
											</xsl:for-each>
										</xsl:when>
										<xsl:otherwise>
											<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']">
												<xsl:for-each select="*[local-name()='property' and namespace-uri()='']">
													<xsl:for-each select="*[local-name()='value' and namespace-uri()='']">
														<xsl:variable name="var42_nested">
															<xsl:for-each select="$var39_cur/*[local-name()='product' and namespace-uri()='']">
																<xsl:value-of select="number(boolean(*[local-name()='EST' and namespace-uri()='']))"/>
															</xsl:for-each>
														</xsl:variable>
														<xsl:if test="(not(boolean(translate(normalize-space($var42_nested), ' 0', ''))) and ($var40_cur/*[local-name()='key' and namespace-uri()=''] = 'OwnerCode'))">
															<xsl:value-of select="."/>
														</xsl:if>
													</xsl:for-each>
												</xsl:for-each>
											</xsl:for-each>
										</xsl:otherwise>
									</xsl:choose>
								</cns:OwnerCode>
							</xsl:if>
							<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='set' and namespace-uri()='']/*[local-name()='product' and namespace-uri()='']">
								<cns:SelectedOfferItem>
									<xsl:for-each select="*[local-name()='ID' and namespace-uri()='']">
										<cns:OfferItemRefID>
											<xsl:value-of select="."/>
										</cns:OfferItemRefID>
									</xsl:for-each>
									<xsl:for-each select="*[local-name()='RefIDs' and namespace-uri()='']">
										<!-- Manual change start: Call template from Xslt Lib -->
										<xsl:variable name="PaxRefIDSplit">
											<xsl:call-template name="split"/>
										</xsl:variable>
										<xsl:for-each select="ext:node-set($PaxRefIDSplit)/*">
											<cns:PaxRefID>
												<xsl:value-of select="."/>
											</cns:PaxRefID>
										</xsl:for-each>
									</xsl:for-each>
									<!-- Manual change end: Call template from Xslt Lib -->
									<xsl:for-each select="*[local-name()='EST' and namespace-uri()='']/*[local-name()='Data' and namespace-uri()='']/*[local-name()='seatNbr' and namespace-uri()='']">
										<cns:SelectedSeat>
											<cns:ColumnID>
												<xsl:value-of select="substring(., string-length(string(.)), 1)"/>
											</cns:ColumnID>
											<cns:SeatRowNumber>
												<xsl:value-of select="number(substring(., 1, (string-length(string(.)) - 1)))"/>
											</cns:SeatRowNumber>
										</cns:SelectedSeat>
									</xsl:for-each>
								</cns:SelectedOfferItem>
							</xsl:for-each>
						</cns:SelectedPricedOffer>
					</cns:AcceptSelectedQuotedOfferList>
				</cns:CreateOrder>
				<cns:DataLists>
					<cns:ContactInfoList>
						<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='actor' and namespace-uri()='']">
							<xsl:for-each select="*[local-name()='contact' and namespace-uri()='']">
								<xsl:variable name="var50_nested">
									<xsl:choose>
										<xsl:when test="*[local-name()='contactType' and namespace-uri()='']">
											<xsl:for-each select="*[local-name()='contactType' and namespace-uri()='']">
												<xsl:variable name="var52_nested">
													<xsl:call-template name="vmf:vmf1_inputtoresult">
														<xsl:with-param name="input" select="string(.)"/>
													</xsl:call-template>
												</xsl:variable>
												<xsl:value-of select="number(boolean(translate($var52_nested, 'false0 ', '')))"/>
											</xsl:for-each>
										</xsl:when>
										<xsl:otherwise>
											<xsl:value-of select="1"/>
										</xsl:otherwise>
									</xsl:choose>
								</xsl:variable>
								<xsl:if test="boolean(translate(normalize-space($var50_nested), ' 0', ''))">
									<cns:ContactInfo>
										<xsl:for-each select="$var48_cur/*[local-name()='ID' and namespace-uri()='']">
											<cns:ContactInfoID>
												<xsl:value-of select="concat('CIPAX', translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', ''), '_')"/>
											</cns:ContactInfoID>
										</xsl:for-each>
										<cns:ContactPurposeText>
											<xsl:value-of select="'OTH'"/>
										</cns:ContactPurposeText>
										<xsl:for-each select="*[local-name()='email' and namespace-uri()='']">
											<cns:EmailAddress>
												<xsl:for-each select="*[local-name()='label' and namespace-uri()='']">
													<cns:ContactTypeText>
														<xsl:value-of select="."/>
													</cns:ContactTypeText>
												</xsl:for-each>
												<cns:EmailAddressText>
													<!-- Manual change start -->
													<xsl:value-of select="(./node())[./self::text()]"/>
													<!-- Manual change end -->
												</cns:EmailAddressText>
											</cns:EmailAddress>
										</xsl:for-each>
										<xsl:for-each select="$var48_cur/*[local-name()='ID' and namespace-uri()='']">
											<cns:IndividualRefID>
												<xsl:value-of select="."/>
											</cns:IndividualRefID>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='phone' and namespace-uri()='']">
											<cns:Phone>
												<xsl:for-each select="*[local-name()='label' and namespace-uri()='']">
													<cns:ContactTypeText>
														<xsl:value-of select="."/>
													</cns:ContactTypeText>
												</xsl:for-each>
												<xsl:for-each select="*[local-name()='overseasCode' and namespace-uri()='']">
													<cns:CountryDialingCode>
														<xsl:value-of select="."/>
													</cns:CountryDialingCode>
												</xsl:for-each>
												<xsl:for-each select="(./node())[./self::text()]">
													<cns:PhoneNumber>
														<xsl:value-of select="translate(., concat(' `~!@#$%^&amp;*()-_=+[]{}|\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')"/>
													</cns:PhoneNumber>
												</xsl:for-each>
											</cns:Phone>
										</xsl:for-each>
									</cns:ContactInfo>
								</xsl:if>
							</xsl:for-each>
						</xsl:for-each>
						<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='actor' and namespace-uri()='']">
							<xsl:for-each select="*[local-name()='contact' and namespace-uri()='']">
								<xsl:variable name="var63_nested">
									<xsl:for-each select="*[local-name()='contactType' and namespace-uri()='']">
										<xsl:variable name="var65_nested">
											<xsl:call-template name="vmf:vmf2_inputtoresult">
												<xsl:with-param name="input" select="string(.)"/>
											</xsl:call-template>
										</xsl:variable>
										<xsl:value-of select="number(boolean(translate($var65_nested, 'false0 ', '')))"/>
									</xsl:for-each>
								</xsl:variable>
								<xsl:if test="boolean(translate(normalize-space($var63_nested), ' 0', ''))">
									<cns:ContactInfo>
										<xsl:for-each select="$var61_cur/*[local-name()='ID' and namespace-uri()='']">
											<cns:ContactInfoID>
												<xsl:value-of select="concat('CIPAX', translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', ''), '_')"/>
											</cns:ContactInfoID>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='contactType' and namespace-uri()='']">
											<cns:ContactPurposeText>
												<xsl:variable name="var68_nested">
													<xsl:call-template name="vmf:vmf3_inputtoresult">
														<xsl:with-param name="input" select="string(.)"/>
													</xsl:call-template>
												</xsl:variable>
												<xsl:value-of select="$var68_nested"/>
											</cns:ContactPurposeText>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='ContactRefusedInd' and namespace-uri()='']">
											<cns:ContactRefusedInd>
												<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
											</cns:ContactRefusedInd>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='email' and namespace-uri()='']">
											<cns:EmailAddress>
												<cns:EmailAddressText>
													<!-- Manual change start -->
													<xsl:value-of select="(./node())[./self::text()]"/>
													<!-- Manual change end -->
												</cns:EmailAddressText>
											</cns:EmailAddress>
										</xsl:for-each>
										<xsl:for-each select="$var61_cur/*[local-name()='ID' and namespace-uri()='']">
											<cns:IndividualRefID>
												<xsl:value-of select="."/>
											</cns:IndividualRefID>
										</xsl:for-each>
										<xsl:for-each select="$var61_cur/*[local-name()='address' and namespace-uri()='']/*[local-name()='addresseeName' and namespace-uri()='']">
											<xsl:variable name="var73_nested">
												<xsl:for-each select="$var62_filter/*[local-name()='contactType' and namespace-uri()='']">
													<xsl:variable name="var75_nested">
														<xsl:call-template name="vmf:vmf4_inputtoresult">
															<xsl:with-param name="input" select="string(.)"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="number(boolean(translate($var75_nested, 'false0 ', '')))"/>
												</xsl:for-each>
											</xsl:variable>
											<xsl:if test="boolean(translate(normalize-space($var73_nested), ' 0', ''))">
												<cns:OtherAddress>
													<cns:ContactTypeText>
														<xsl:value-of select="'GSTIN'"/>
													</cns:ContactTypeText>
													<cns:OtherAddressText>
														<xsl:value-of select="."/>
													</cns:OtherAddressText>
												</cns:OtherAddress>
											</xsl:if>
										</xsl:for-each>
										<xsl:for-each select="$var61_cur/*[local-name()='address' and namespace-uri()='']/*[local-name()='companyName' and namespace-uri()='']">
											<xsl:variable name="var77_nested">
												<xsl:for-each select="$var62_filter/*[local-name()='contactType' and namespace-uri()='']">
													<xsl:variable name="var79_nested">
														<xsl:call-template name="vmf:vmf4_inputtoresult">
															<xsl:with-param name="input" select="string(.)"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="number(boolean(translate($var79_nested, 'false0 ', '')))"/>
												</xsl:for-each>
											</xsl:variable>
											<xsl:if test="boolean(translate(normalize-space($var77_nested), ' 0', ''))">
												<cns:OtherAddress>
													<cns:ContactTypeText>
														<xsl:value-of select="'COMPANY'"/>
													</cns:ContactTypeText>
													<cns:OtherAddressText>
														<xsl:value-of select="."/>
													</cns:OtherAddressText>
												</cns:OtherAddress>
											</xsl:if>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='phone' and namespace-uri()='']">
											<cns:Phone>
												<xsl:for-each select="*[local-name()='label' and namespace-uri()='']">
													<cns:ContactTypeText>
														<xsl:value-of select="."/>
													</cns:ContactTypeText>
												</xsl:for-each>
												<xsl:for-each select="*[local-name()='overseasCode' and namespace-uri()='']">
													<cns:CountryDialingCode>
														<xsl:value-of select="."/>
													</cns:CountryDialingCode>
												</xsl:for-each>
												<xsl:for-each select="(./node())[./self::text()]">
													<cns:PhoneNumber>
														<xsl:value-of select="translate(., concat(' `~!@#$%^&amp;*()-_=+[]{}|\:;&quot;',&quot;',./&lt;&gt;?abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&quot;), '')"/>
													</cns:PhoneNumber>
												</xsl:for-each>
											</cns:Phone>
										</xsl:for-each>
										<xsl:for-each select="$var61_cur/*[local-name()='address' and namespace-uri()='']">
											<xsl:variable name="var85_nested">
												<xsl:for-each select="$var62_filter/*[local-name()='contactType' and namespace-uri()='']">
													<xsl:variable name="var87_nested">
														<xsl:call-template name="vmf:vmf4_inputtoresult">
															<xsl:with-param name="input" select="string(.)"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="number(((boolean(translate($var87_nested, 'false0 ', '')) and boolean($var84_filter/*[local-name()='companyName' and namespace-uri()=''])) and boolean($var84_filter/*[local-name()='addresseeName' and namespace-uri()=''])))"/>
												</xsl:for-each>
											</xsl:variable>
											<xsl:if test="boolean(translate(normalize-space($var85_nested), ' 0', ''))">
												<cns:PostalAddress>
													<xsl:for-each select="*[local-name()='cityName' and namespace-uri()='']">
														<cns:CityName>
															<xsl:value-of select="."/>
														</cns:CityName>
													</xsl:for-each>
													<xsl:for-each select="*[local-name()='countryCode' and namespace-uri()='']">
														<cns:CountryCode>
															<xsl:value-of select="."/>
														</cns:CountryCode>
													</xsl:for-each>
													<xsl:for-each select="*[local-name()='countryName' and namespace-uri()='']">
														<cns:CountryName>
															<xsl:value-of select="."/>
														</cns:CountryName>
													</xsl:for-each>
													<xsl:for-each select="*[local-name()='stateName' and namespace-uri()='']">
														<cns:CountrySubDivisionName>
															<xsl:value-of select="."/>
														</cns:CountrySubDivisionName>
													</xsl:for-each>
													<xsl:for-each select="*[local-name()='zip' and namespace-uri()='']">
														<cns:PostalCode>
															<xsl:value-of select="."/>
														</cns:PostalCode>
													</xsl:for-each>
													<xsl:for-each select="*[local-name()='line' and namespace-uri()='']">
														<cns:StreetText>
															<xsl:value-of select="."/>
														</cns:StreetText>
													</xsl:for-each>
													<xsl:for-each select="*[local-name()='complement' and namespace-uri()='']">
														<cns:StreetText>
															<xsl:value-of select="."/>
														</cns:StreetText>
													</xsl:for-each>
												</cns:PostalAddress>
											</xsl:if>
										</xsl:for-each>
									</cns:ContactInfo>
								</xsl:if>
							</xsl:for-each>
						</xsl:for-each>
						<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='actor' and namespace-uri()='']">
							<xsl:for-each select="*[local-name()='address' and namespace-uri()='']">
								<xsl:variable name="var97_nested">
									<xsl:for-each select="*[local-name()='label' and namespace-uri()='']">
										<xsl:variable name="var99_nested">
											<xsl:call-template name="vmf:vmf5_inputtoresult">
												<xsl:with-param name="input" select="translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
											</xsl:call-template>
										</xsl:variable>
										<xsl:value-of select="number(boolean(translate($var99_nested, 'false0 ', '')))"/>
									</xsl:for-each>
								</xsl:variable>
								<xsl:if test="boolean(translate(normalize-space($var97_nested), ' 0', ''))">
									<cns:ContactInfo>
										<xsl:for-each select="$var95_cur/*[local-name()='ID' and namespace-uri()='']">
											<cns:ContactInfoID>
												<xsl:value-of select="concat('CIPAX', translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', ''), '_')"/>
											</cns:ContactInfoID>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='label' and namespace-uri()='']">
											<xsl:variable name="var102_nested">
												<xsl:call-template name="vmf:vmf6_inputtoresult">
													<xsl:with-param name="input" select="translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
												</xsl:call-template>
											</xsl:variable>
											<xsl:if test="string($var102_nested)">
												<cns:ContactPurposeText>
													<xsl:variable name="var103_nested">
														<xsl:call-template name="vmf:vmf6_inputtoresult">
															<xsl:with-param name="input" select="translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="substring($var103_nested, 2)"/>
												</cns:ContactPurposeText>
											</xsl:if>
										</xsl:for-each>
										<xsl:for-each select="$var95_cur/*[local-name()='ID' and namespace-uri()='']">
											<cns:IndividualRefID>
												<xsl:value-of select="."/>
											</cns:IndividualRefID>
										</xsl:for-each>
										<cns:PostalAddress>
											<xsl:for-each select="*[local-name()='cityName' and namespace-uri()='']">
												<cns:CityName>
													<xsl:value-of select="."/>
												</cns:CityName>
											</xsl:for-each>
											<xsl:for-each select="*[local-name()='countryCode' and namespace-uri()='']">
												<cns:CountryCode>
													<xsl:value-of select="."/>
												</cns:CountryCode>
											</xsl:for-each>
											<xsl:for-each select="*[local-name()='countryName' and namespace-uri()='']">
												<cns:CountryName>
													<xsl:value-of select="."/>
												</cns:CountryName>
											</xsl:for-each>
											<xsl:for-each select="*[local-name()='stateName' and namespace-uri()='']">
												<cns:CountrySubDivisionName>
													<xsl:value-of select="."/>
												</cns:CountrySubDivisionName>
											</xsl:for-each>
											<xsl:for-each select="*[local-name()='zip' and namespace-uri()='']">
												<cns:PostalCode>
													<xsl:value-of select="."/>
												</cns:PostalCode>
											</xsl:for-each>
											<xsl:for-each select="*[local-name()='line' and namespace-uri()='']">
												<cns:StreetText>
													<xsl:value-of select="."/>
												</cns:StreetText>
											</xsl:for-each>
											<xsl:for-each select="*[local-name()='complement' and namespace-uri()='']">
												<cns:StreetText>
													<xsl:value-of select="."/>
												</cns:StreetText>
											</xsl:for-each>
										</cns:PostalAddress>
									</cns:ContactInfo>
								</xsl:if>
							</xsl:for-each>
						</xsl:for-each>
					</cns:ContactInfoList>
					<cns:PaxList>
						<xsl:for-each select="*[local-name()='Request' and namespace-uri()='']/*[local-name()='actor' and namespace-uri()='']">
							<cns:Pax>
								<xsl:for-each select="(./*[local-name()='docRef' and namespace-uri()=''])[not(*[local-name()='taxIdentifier' and namespace-uri()=''])]">
									<cns:IdentityDoc>
										<xsl:for-each select="*[local-name()='dateOfBirth' and namespace-uri()='']">
											<cns:Birthdate>
												<xsl:value-of select="."/>
											</cns:Birthdate>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='birthPlace' and namespace-uri()='']">
											<xsl:variable name="var116_nested">
												<xsl:for-each select="$var113_filter/*[local-name()='visa' and namespace-uri()='']/*[local-name()='visaType' and namespace-uri()='']">
													<xsl:variable name="var118_nested">
														<xsl:call-template name="vmf:vmf7_inputtoresult">
															<xsl:with-param name="input" select="string(.)"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="number(boolean(translate($var118_nested, 'false0 ', '')))"/>
												</xsl:for-each>
											</xsl:variable>
											<xsl:if test="boolean(translate(normalize-space($var116_nested), ' 0', ''))">
												<cns:BirthplaceText>
													<xsl:value-of select="."/>
												</cns:BirthplaceText>
											</xsl:if>
										</xsl:for-each>
										<xsl:choose>
											<xsl:when test="*[local-name()='nationalityIATACode' and namespace-uri()='']">
												<xsl:for-each select="*[local-name()='nationalityIATACode' and namespace-uri()='']">
													<cns:CitizenshipCountryCode>
														<xsl:value-of select="."/>
													</cns:CitizenshipCountryCode>
												</xsl:for-each>
											</xsl:when>
											<xsl:otherwise>
												<xsl:for-each select="*[local-name()='nationality' and namespace-uri()='']">
													<cns:CitizenshipCountryCode>
														<xsl:value-of select="."/>
													</cns:CitizenshipCountryCode>
												</xsl:for-each>
											</xsl:otherwise>
										</xsl:choose>
										<xsl:for-each select="*[local-name()='expirationDate' and namespace-uri()='']">
											<cns:ExpiryDate>
												<xsl:value-of select="."/>
											</cns:ExpiryDate>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='Gender' and namespace-uri()='']">
											<cns:GenderCode>
												<xsl:variable name="var123_nested">
													<xsl:call-template name="vmf:vmf8_inputtoresult">
														<xsl:with-param name="input" select="string(.)"/>
													</xsl:call-template>
												</xsl:variable>
												<xsl:value-of select="$var123_nested"/>
											</cns:GenderCode>
										</xsl:for-each>
										<xsl:variable name="var124_nested">
											<xsl:choose>
												<xsl:when test="*[local-name()='GivenName' and namespace-uri()='']">
													<xsl:for-each select="*[local-name()='GivenName' and namespace-uri()='']">
														<xsl:value-of select="'1'"/>
													</xsl:for-each>
												</xsl:when>
												<xsl:otherwise>
													<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='FirstName' and namespace-uri()='']">
														<xsl:value-of select="'1'"/>
													</xsl:for-each>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<xsl:if test="boolean(translate(normalize-space($var124_nested), ' 0', ''))">
											<cns:GivenName>
												<xsl:choose>
													<xsl:when test="*[local-name()='GivenName' and namespace-uri()='']">
														<xsl:for-each select="*[local-name()='GivenName' and namespace-uri()='']">
															<xsl:value-of select="."/>
														</xsl:for-each>
													</xsl:when>
													<xsl:otherwise>
														<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='FirstName' and namespace-uri()='']">
															<xsl:value-of select="."/>
														</xsl:for-each>
													</xsl:otherwise>
												</xsl:choose>
											</cns:GivenName>
										</xsl:if>
										<xsl:for-each select="(./node())[./self::text()]">
											<cns:IdentityDocID>
												<xsl:value-of select="."/>
											</cns:IdentityDocID>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='type' and namespace-uri()='']">
											<cns:IdentityDocTypeCode>
												<xsl:variable name="var131_nested">
													<xsl:call-template name="vmf:vmf9_inputtoresult">
														<xsl:with-param name="input" select="string(.)"/>
													</xsl:call-template>
												</xsl:variable>
												<xsl:value-of select="$var131_nested"/>
											</cns:IdentityDocTypeCode>
										</xsl:for-each>
										<xsl:for-each select="*[local-name()='issuanceDate' and namespace-uri()='']">
											<cns:IssueDate>
												<xsl:value-of select="."/>
											</cns:IssueDate>
										</xsl:for-each>
										<xsl:choose>
											<xsl:when test="*[local-name()='issuerIATACountryCode' and namespace-uri()='']">
												<xsl:for-each select="*[local-name()='issuerIATACountryCode' and namespace-uri()='']">
													<cns:IssuingCountryCode>
														<xsl:value-of select="."/>
													</cns:IssuingCountryCode>
												</xsl:for-each>
											</xsl:when>
											<xsl:otherwise>
												<xsl:for-each select="*[local-name()='issuer' and namespace-uri()='']">
													<cns:IssuingCountryCode>
														<xsl:value-of select="."/>
													</cns:IssuingCountryCode>
												</xsl:for-each>
											</xsl:otherwise>
										</xsl:choose>
										<xsl:variable name="var135_nested">
											<xsl:choose>
												<xsl:when test="*[local-name()='Surname' and namespace-uri()='']">
													<xsl:for-each select="*[local-name()='Surname' and namespace-uri()='']">
														<xsl:value-of select="'1'"/>
													</xsl:for-each>
												</xsl:when>
												<xsl:otherwise>
													<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
														<xsl:value-of select="'1'"/>
													</xsl:for-each>
												</xsl:otherwise>
											</xsl:choose>
										</xsl:variable>
										<xsl:if test="boolean(translate(normalize-space($var135_nested), ' 0', ''))">
											<cns:Surname>
												<xsl:choose>
													<xsl:when test="*[local-name()='Surname' and namespace-uri()='']">
														<xsl:for-each select="*[local-name()='Surname' and namespace-uri()='']">
															<xsl:value-of select="."/>
														</xsl:for-each>
													</xsl:when>
													<xsl:otherwise>
														<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
															<xsl:value-of select="."/>
														</xsl:for-each>
													</xsl:otherwise>
												</xsl:choose>
											</cns:Surname>
										</xsl:if>
									</cns:IdentityDoc>
								</xsl:for-each>
								<xsl:for-each select="*[local-name()='docRef' and namespace-uri()='']">
									<xsl:if test="*[local-name()='taxIdentifier' and namespace-uri()='']">
										<cns:IdentityDoc>
											<xsl:for-each select="*[local-name()='taxIdentifier' and namespace-uri()='']">
												<cns:IdentityDocID>
													<xsl:value-of select="*[local-name()='fiscalNumber' and namespace-uri()='']"/>
												</cns:IdentityDocID>
											</xsl:for-each>
											<cns:IdentityDocTypeCode>
												<xsl:choose>
													<xsl:when test="*[local-name()='taxIdentifier' and namespace-uri()='']">
														<xsl:variable name="var142_nested">
															<xsl:for-each select="*[local-name()='taxIdentifier' and namespace-uri()='']">
																<xsl:value-of select="*[local-name()='fiscalType' and namespace-uri()='']"/>
															</xsl:for-each>
														</xsl:variable>
														<xsl:value-of select="$var142_nested"/>
													</xsl:when>
													<xsl:otherwise>
														<xsl:value-of select="'NULL'"/>
													</xsl:otherwise>
												</xsl:choose>
											</cns:IdentityDocTypeCode>
											<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
												<cns:Surname>
													<xsl:value-of select="."/>
												</cns:Surname>
											</xsl:for-each>
										</cns:IdentityDoc>
									</xsl:if>
								</xsl:for-each>
								<xsl:for-each select="*[local-name()='docRef' and namespace-uri()='']">
									<xsl:for-each select="*[local-name()='visa' and namespace-uri()='']">
										<xsl:variable name="var147_nested">
											<xsl:for-each select="*[local-name()='visaType' and namespace-uri()='']">
												<xsl:variable name="var149_nested">
													<xsl:call-template name="vmf:vmf10_inputtoresult">
														<xsl:with-param name="input" select="string(.)"/>
													</xsl:call-template>
												</xsl:variable>
												<xsl:value-of select="number(boolean(translate($var149_nested, 'false0 ', '')))"/>
											</xsl:for-each>
										</xsl:variable>
										<xsl:if test="boolean(translate(normalize-space($var147_nested), ' 0', ''))">
											<cns:IdentityDoc>
												<xsl:for-each select="*[local-name()='visaNumber' and namespace-uri()='']">
													<cns:IdentityDocID>
														<xsl:value-of select="."/>
													</cns:IdentityDocID>
												</xsl:for-each>
												<cns:IdentityDocTypeCode>
													<xsl:value-of select="'VS'"/>
												</cns:IdentityDocTypeCode>
												<xsl:variable name="var151_nested">
													<xsl:choose>
														<xsl:when test="$var145_cur/*[local-name()='Surname' and namespace-uri()='']">
															<xsl:for-each select="$var145_cur/*[local-name()='Surname' and namespace-uri()='']">
																<xsl:value-of select="'1'"/>
															</xsl:for-each>
														</xsl:when>
														<xsl:otherwise>
															<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
																<xsl:value-of select="'1'"/>
															</xsl:for-each>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:variable>
												<xsl:if test="boolean(translate(normalize-space($var151_nested), ' 0', ''))">
													<cns:Surname>
														<xsl:choose>
															<xsl:when test="$var145_cur/*[local-name()='Surname' and namespace-uri()='']">
																<xsl:for-each select="$var145_cur/*[local-name()='Surname' and namespace-uri()='']">
																	<xsl:value-of select="."/>
																</xsl:for-each>
															</xsl:when>
															<xsl:otherwise>
																<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
																	<xsl:value-of select="."/>
																</xsl:for-each>
															</xsl:otherwise>
														</xsl:choose>
													</cns:Surname>
												</xsl:if>
												<cns:Visa>
													<xsl:for-each select="*[local-name()='enterBeforeDate' and namespace-uri()='']">
														<cns:ExpiryDate>
															<xsl:value-of select="."/>
														</cns:ExpiryDate>
													</xsl:for-each>
													<xsl:choose>
														<xsl:when test="*[local-name()='visaHostIATACountryCode' and namespace-uri()='']">
															<xsl:for-each select="*[local-name()='visaHostIATACountryCode' and namespace-uri()='']">
																<cns:HostCountryCode>
																	<xsl:value-of select="."/>
																</cns:HostCountryCode>
															</xsl:for-each>
														</xsl:when>
														<xsl:otherwise>
															<xsl:for-each select="*[local-name()='visaHostCountryCode' and namespace-uri()='']">
																<cns:HostCountryCode>
																	<xsl:value-of select="."/>
																</cns:HostCountryCode>
															</xsl:for-each>
														</xsl:otherwise>
													</xsl:choose>
													<xsl:for-each select="*[local-name()='visaIssuanceDate' and namespace-uri()='']">
														<cns:IssueDate>
															<xsl:value-of select="."/>
														</cns:IssueDate>
													</xsl:for-each>
													<xsl:choose>
														<xsl:when test="*[local-name()='visaIssueIATACountryCode' and namespace-uri()='']">
															<xsl:for-each select="*[local-name()='visaIssueIATACountryCode' and namespace-uri()='']">
																<cns:IssuingCountryCode>
																	<xsl:value-of select="."/>
																</cns:IssuingCountryCode>
															</xsl:for-each>
														</xsl:when>
														<xsl:otherwise>
															<xsl:for-each select="*[local-name()='visaIssueCountryCode' and namespace-uri()='']">
																<cns:IssuingCountryCode>
																	<xsl:value-of select="."/>
																</cns:IssuingCountryCode>
															</xsl:for-each>
														</xsl:otherwise>
													</xsl:choose>
													<xsl:for-each select="*[local-name()='visaNumber' and namespace-uri()='']">
														<cns:VisaID>
															<xsl:value-of select="."/>
														</cns:VisaID>
													</xsl:for-each>
												</cns:Visa>
											</cns:IdentityDoc>
										</xsl:if>
									</xsl:for-each>
								</xsl:for-each>
								<xsl:for-each select="*[local-name()='docRef' and namespace-uri()='']">
									<xsl:for-each select="*[local-name()='visa' and namespace-uri()='']">
										<xsl:variable name="var165_nested">
											<xsl:for-each select="*[local-name()='visaType' and namespace-uri()='']">
												<xsl:variable name="var167_nested">
													<xsl:call-template name="vmf:vmf11_inputtoresult">
														<xsl:with-param name="input" select="string(.)"/>
													</xsl:call-template>
												</xsl:variable>
												<xsl:value-of select="number(boolean(translate($var167_nested, 'false0 ', '')))"/>
											</xsl:for-each>
										</xsl:variable>
										<xsl:if test="boolean(translate(normalize-space($var165_nested), ' 0', ''))">
											<cns:IdentityDoc>
												<xsl:for-each select="*[local-name()='visaNumber' and namespace-uri()='']">
													<cns:IdentityDocID>
														<xsl:value-of select="."/>
													</cns:IdentityDocID>
												</xsl:for-each>
												<cns:IdentityDocTypeCode>
													<xsl:value-of select="'CR'"/>
												</cns:IdentityDocTypeCode>
												<xsl:choose>
													<xsl:when test="*[local-name()='visaIssueIATACountryCode' and namespace-uri()='']">
														<xsl:for-each select="*[local-name()='visaIssueIATACountryCode' and namespace-uri()='']">
															<cns:IssuingCountryCode>
																<xsl:value-of select="."/>
															</cns:IssuingCountryCode>
														</xsl:for-each>
													</xsl:when>
													<xsl:when test="*[local-name()='visaHostIATACountryCode' and namespace-uri()='']">
														<xsl:for-each select="*[local-name()='visaHostIATACountryCode' and namespace-uri()='']">
															<cns:IssuingCountryCode>
																<xsl:value-of select="."/>
															</cns:IssuingCountryCode>
														</xsl:for-each>
													</xsl:when>
													<xsl:when test="*[local-name()='visaIssueCountryCode' and namespace-uri()='']">
														<xsl:for-each select="*[local-name()='visaIssueCountryCode' and namespace-uri()='']">
															<cns:IssuingCountryCode>
																<xsl:value-of select="."/>
															</cns:IssuingCountryCode>
														</xsl:for-each>
													</xsl:when>
													<xsl:otherwise>
														<xsl:for-each select="*[local-name()='visaHostCountryCode' and namespace-uri()='']">
															<cns:IssuingCountryCode>
																<xsl:value-of select="."/>
															</cns:IssuingCountryCode>
														</xsl:for-each>
													</xsl:otherwise>
												</xsl:choose>
												<xsl:variable name="var173_nested">
													<xsl:choose>
														<xsl:when test="$var163_cur/*[local-name()='Surname' and namespace-uri()='']">
															<xsl:for-each select="$var163_cur/*[local-name()='Surname' and namespace-uri()='']">
																<xsl:value-of select="'1'"/>
															</xsl:for-each>
														</xsl:when>
														<xsl:otherwise>
															<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
																<xsl:value-of select="'1'"/>
															</xsl:for-each>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:variable>
												<xsl:if test="boolean(translate(normalize-space($var173_nested), ' 0', ''))">
													<cns:Surname>
														<xsl:choose>
															<xsl:when test="$var163_cur/*[local-name()='Surname' and namespace-uri()='']">
																<xsl:for-each select="$var163_cur/*[local-name()='Surname' and namespace-uri()='']">
																	<xsl:value-of select="."/>
																</xsl:for-each>
															</xsl:when>
															<xsl:otherwise>
																<xsl:for-each select="$var112_cur/*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
																	<xsl:value-of select="."/>
																</xsl:for-each>
															</xsl:otherwise>
														</xsl:choose>
													</cns:Surname>
												</xsl:if>
											</cns:IdentityDoc>
										</xsl:if>
									</xsl:for-each>
								</xsl:for-each>
								<cns:Individual>
									<xsl:for-each select="*[local-name()='DateOfBirth' and namespace-uri()='']">
										<cns:Birthdate>
											<xsl:value-of select="."/>
										</cns:Birthdate>
									</xsl:for-each>
									<cns:GenderCode>
										<xsl:variable name="var179_nested">
											<xsl:for-each select="*[local-name()='Name' and namespace-uri()='']">
												<xsl:value-of select="number(boolean(*[local-name()='Type' and namespace-uri()='']))"/>
											</xsl:for-each>
										</xsl:variable>
										<xsl:choose>
											<xsl:when test="boolean(translate(normalize-space($var179_nested), ' 0', ''))">
												<xsl:variable name="var181_nested">
													<xsl:for-each select="*[local-name()='Name' and namespace-uri()='']/*[local-name()='Type' and namespace-uri()='']">
														<xsl:variable name="var183_nested">
															<xsl:call-template name="vmf:vmf12_inputtoresult">
																<xsl:with-param name="input" select="translate(., 'abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')"/>
															</xsl:call-template>
														</xsl:variable>
														<xsl:value-of select="$var183_nested"/>
													</xsl:for-each>
												</xsl:variable>
												<xsl:value-of select="$var181_nested"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="'U'"/>
											</xsl:otherwise>
										</xsl:choose>
									</cns:GenderCode>
									<xsl:for-each select="*[local-name()='Name' and namespace-uri()='']/*[local-name()='FirstName' and namespace-uri()='']">
										<cns:GivenName>
											<xsl:value-of select="."/>
										</cns:GivenName>
									</xsl:for-each>
									<xsl:for-each select="*[local-name()='ID' and namespace-uri()='']">
										<cns:IndividualID>
											<xsl:value-of select="."/>
										</cns:IndividualID>
									</xsl:for-each>
									<xsl:for-each select="*[local-name()='Name' and namespace-uri()='']/*[local-name()='LastName' and namespace-uri()='']">
										<cns:Surname>
											<xsl:value-of select="."/>
										</cns:Surname>
									</xsl:for-each>
									<xsl:for-each select="*[local-name()='Name' and namespace-uri()='']/*[local-name()='Title' and namespace-uri()='']">
										<cns:TitleName>
											<xsl:value-of select="."/>
										</cns:TitleName>
									</xsl:for-each>
								</cns:Individual>
								<xsl:for-each select="*[local-name()='loyalty' and namespace-uri()='']">
									<cns:LoyaltyProgramAccount>
										<xsl:for-each select="*[local-name()='identifier' and namespace-uri()='']">
											<cns:AccountNumber>
												<xsl:value-of select="."/>
											</cns:AccountNumber>
										</xsl:for-each>
										<cns:LoyaltyProgram>
											<cns:Carrier>
												<xsl:for-each select="*[local-name()='companyCode' and namespace-uri()='']">
													<cns:AirlineDesigCode>
														<xsl:value-of select="."/>
													</cns:AirlineDesigCode>
												</xsl:for-each>
											</cns:Carrier>
										</cns:LoyaltyProgram>
									</cns:LoyaltyProgramAccount>
								</xsl:for-each>
								<xsl:for-each select="*[local-name()='ID' and namespace-uri()='']">
									<cns:PaxID>
										<xsl:value-of select="."/>
									</cns:PaxID>
								</xsl:for-each>
								<!-- Manual change start: Call template from Xslt Lib -->
								<xsl:variable name="PassengerRef">
									<xsl:call-template name="getPaxRef"/>
								</xsl:variable>
								<xsl:if test="$PassengerRef != ''">
									<cns:PaxRefID>
										<xsl:value-of select="$PassengerRef"/>
									</cns:PaxRefID>
								</xsl:if>
								<!-- Manual change end: Call template from Xslt Lib -->
								<xsl:for-each select="*[local-name()='PTC' and namespace-uri()='']">
									<cns:PTC>
										<xsl:value-of select="."/>
									</cns:PTC>
								</xsl:for-each>
								<xsl:for-each select="*[local-name()='docRef' and namespace-uri()='']/*[local-name()='visa' and namespace-uri()='']">
									<xsl:variable name="var194_nested">
										<xsl:for-each select="*[local-name()='visaType' and namespace-uri()='']">
											<xsl:variable name="var196_nested">
												<xsl:call-template name="vmf:vmf13_inputtoresult">
													<xsl:with-param name="input" select="string(.)"/>
												</xsl:call-template>
											</xsl:variable>
											<xsl:value-of select="number(boolean(translate($var196_nested, 'false0 ', '')))"/>
										</xsl:for-each>
									</xsl:variable>
									<xsl:if test="boolean(translate(normalize-space($var194_nested), ' 0', ''))">
										<cns:RedressCase>
											<xsl:choose>
												<xsl:when test="*[local-name()='visaHostIATACountryCode' and namespace-uri()='']">
													<xsl:for-each select="*[local-name()='visaHostIATACountryCode' and namespace-uri()='']">
														<cns:CountryCode>
															<xsl:value-of select="."/>
														</cns:CountryCode>
													</xsl:for-each>
												</xsl:when>
												<xsl:otherwise>
													<xsl:for-each select="*[local-name()='visaHostCountryCode' and namespace-uri()='']">
														<cns:CountryCode>
															<xsl:value-of select="."/>
														</cns:CountryCode>
													</xsl:for-each>
												</xsl:otherwise>
											</xsl:choose>
											<xsl:for-each select="*[local-name()='visaNumber' and namespace-uri()='']">
												<cns:RedressCaseID>
													<xsl:value-of select="."/>
												</cns:RedressCaseID>
											</xsl:for-each>
										</cns:RedressCase>
									</xsl:if>
								</xsl:for-each>
							</cns:Pax>
						</xsl:for-each>
					</cns:PaxList>
				</cns:DataLists>
			</Request>
		</IATA_OrderCreateRQ>
	</xsl:template>
</xsl:stylesheet>