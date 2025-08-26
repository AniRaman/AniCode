<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tbf="http://www.altova.com/MapForce/UDF/tbf" xmlns:ns0="http://www.opentravel.org/OTA/2003/05" xmlns:xs="http://www.w3.org/2001/XMLSchema" version="1.0" exclude-result-prefixes="tbf ns0 xs">
	<xsl:template name="tbf:tbf2_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@AbsoluteDeadline | $input/@OffsetTimeUnit | $input/@OffsetUnitMultiplier | $input/@OffsetDropTime">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf3_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@AbsoluteDeadline | $input/@OffsetTimeUnit | $input/@OffsetUnitMultiplier | $input/@OffsetDropTime">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf4_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@CurrencyCode | $input/@DecimalPlaces | $input/@Amount | $input/@RateConvertedInd">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf5_FormattedTextTextType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@Formatted | $input/@Language | $input/@TextFormat">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:value-of select="$input"/>
	</xsl:template>
	<xsl:template name="tbf:tbf6_VehicleChargeType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@CurrencyCode | $input/@DecimalPlaces | $input/@Amount | $input/@TaxInclusive | $input/@Description | $input/@GuaranteedInd | $input/@IncludedInRate | $input/@IncludedInEstTotalInd | $input/@RateConvertInd">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/node()">
			<xsl:choose>
				<xsl:when test="self::*">
					<xsl:if test="self::ns0:TaxAmounts">
						<xsl:element name="{name(.)}" namespace="{namespace-uri(.)}">
							<xsl:call-template name="tbf:tbf7_">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:if>
					<xsl:if test="self::ns0:MinMax">
						<xsl:element name="{name(.)}" namespace="{namespace-uri(.)}">
							<xsl:call-template name="tbf:tbf9_">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:if>
					<xsl:if test="self::ns0:Calculation">
						<xsl:element name="{name(.)}" namespace="{namespace-uri(.)}">
							<xsl:call-template name="tbf:tbf10_">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:if>
				</xsl:when>
				<xsl:when test="not(self::text())">
					<xsl:copy-of select="."/>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf7_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/node()">
			<xsl:choose>
				<xsl:when test="name() = 'ns0:TaxAmount'">
					<xsl:element name="{name()}" namespace="{namespace-uri()}">
						<xsl:call-template name="tbf:tbf8_">
							<xsl:with-param name="input" select="."/>
						</xsl:call-template>
					</xsl:element>
				</xsl:when>
				<xsl:when test="not(self::text())">
					<xsl:copy-of select="."/>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf8_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@Total | $input/@CurrencyCode | $input/@Percentage | $input/@Description">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf9_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@MaxCharge | $input/@MinCharge | $input/@MaxChargeDays">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf10_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@UnitCharge | $input/@UnitName | $input/@Quantity | $input/@Percentage | $input/@Applicability | $input/@MaxQuantity | $input/@Total">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf11_PaymentRulesType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/node()">
			<xsl:choose>
				<xsl:when test="name() = 'ns0:TaxAmount'">
					<xsl:element name="{name()}" namespace="{namespace-uri()}">
						<xsl:call-template name="tbf:tbf8_">
							<xsl:with-param name="input" select="."/>
						</xsl:call-template>
					</xsl:element>
				</xsl:when>
				<xsl:when test="not(self::text())">
					<xsl:copy-of select="."/>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template>
	<xsl:template name="tbf:tbf12_MonetaryRuleType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@CurrencyCode | $input/@DecimalPlaces | $input/@Amount | $input/@RuleType | $input/@Percent | $input/@DateTime | $input/@PaymentType | $input/@RateConvertedInd | $input/@AbsoluteDeadline | $input/@OffsetTimeUnit | $input/@OffsetUnitMultiplier | $input/@OffsetDropTime">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:value-of select="$input"/>
	</xsl:template>
	<xsl:template name="tbf:tbf13_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@SeriesCode | $input/@EffectiveDate | $input/@ExpireDate | $input/@ExpireDateExclusiveIndicator | $input/@BillingNumber | $input/@SupplierIdentifier | $input/@Identifier | $input/@ValueType | $input/@ElectronicIndicator">
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
	</xsl:template>
	<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/">
		<ns0:OTA_VehAvailRateRS>
			<xsl:for-each select="ns0:OTA_VehAvailRateRS">
				<xsl:for-each select="ns0:Success">
					<ns0:Success/>
				</xsl:for-each>
				<xsl:for-each select="ns0:Warnings">
					<ns0:Warnings>
						<xsl:for-each select="ns0:Warning">
							<ns0:Warning>
								<xsl:copy-of select="@Type"/>
								<xsl:for-each select="@Language">
									<xsl:attribute name="Language" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@ShortText">
									<xsl:attribute name="ShortText" namespace="">
										<xsl:value-of select="substring(., '0', '62')"/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@Code | @DocURL | @Status | @Tag | @RecordID | @RPH">
									<xsl:attribute name="{name()}" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:value-of select="."/>
							</ns0:Warning>
						</xsl:for-each>
					</ns0:Warnings>
				</xsl:for-each>
				<xsl:for-each select="ns0:VehAvailRSCore">
					<ns0:VehAvailRSCore>
						<ns0:VehRentalCore>
							<xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime | ns0:VehRentalCore/@ReturnDateTime | ns0:VehRentalCore/@StartChargesDateTime | ns0:VehRentalCore/@StopChargesDateTime">
								<xsl:attribute name="{name()}" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@OneWayIndicator">
								<xsl:attribute name="OneWayIndicator" namespace="">
									<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@MultiIslandRentalDays | ns0:VehRentalCore/@Quantity">
								<xsl:attribute name="{name()}" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@DistUnitName">
								<xsl:attribute name="DistUnitName" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/ns0:PickUpLocation">
								<ns0:PickUpLocation>
									<xsl:if test="@LocationCode">
										<xsl:attribute name="CodeContext" namespace="">
IATA
</xsl:attribute>
									</xsl:if>
									<xsl:for-each select="@LocationCode | @ExtendedLocationCode | @CounterLocation">
										<xsl:attribute name="{name()}" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:value-of select="."/>
								</ns0:PickUpLocation>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/ns0:ReturnLocation">
								<ns0:ReturnLocation>
									<xsl:if test="@LocationCode">
										<xsl:attribute name="CodeContext" namespace="">
IATA
</xsl:attribute>
									</xsl:if>
									<xsl:for-each select="@LocationCode | @ExtendedLocationCode | @CounterLocation">
										<xsl:attribute name="{name()}" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:value-of select="."/>
								</ns0:ReturnLocation>
							</xsl:for-each>
						</ns0:VehRentalCore>
						<ns0:VehVendorAvails>
							<xsl:for-each select="ns0:VehVendorAvails/ns0:VehVendorAvail">
								<ns0:VehVendorAvail>
									<xsl:for-each select="ns0:Vendor">
										<ns0:Vendor>
											<xsl:for-each select="@CompanyShortName">
												<xsl:attribute name="CompanyShortName" namespace="">
													<xsl:choose>
														<xsl:when test="contains(., ' ')">
															<xsl:value-of select="substring-before(., ' ')"/>
														</xsl:when>
														<xsl:otherwise>
															<xsl:value-of select="."/>
														</xsl:otherwise>
													</xsl:choose>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:for-each select="@TravelSector | @Code | @CodeContext | @CountryCode | @Division | @Department">
												<xsl:attribute name="{name()}" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:value-of select="."/>
										</ns0:Vendor>
									</xsl:for-each>
									<ns0:VehAvails>
										<xsl:for-each select="ns0:VehAvails/@RateCategory | ns0:VehAvails/@RatePeriod">
											<xsl:attribute name="{name()}" namespace="">
												<xsl:value-of select="."/>
											</xsl:attribute>
										</xsl:for-each>
										<xsl:for-each select="ns0:VehAvails/ns0:VehAvail">
											<ns0:VehAvail>
												<ns0:VehAvailCore>
													<xsl:attribute name="Status" namespace="">
														<xsl:value-of select="ns0:VehAvailCore/@Status"/>
													</xsl:attribute>
													<xsl:for-each select="ns0:VehAvailCore/@IsAlternateInd">
														<xsl:attribute name="IsAlternateInd" namespace="">
															<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
														</xsl:attribute>
													</xsl:for-each>
													<ns0:Vehicle>
														<xsl:attribute name="CodeContext" namespace="">
ACRISS
</xsl:attribute>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@AirConditionInd">
															<xsl:attribute name="AirConditionInd" namespace="">
																<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@TransmissionType | ns0:VehAvailCore/ns0:Vehicle/@FuelType">
															<xsl:attribute name="{name()}" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@DriveType | ns0:VehAvailCore/ns0:Vehicle/@PassengerQuantity">
															<xsl:attribute name="{name()}">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@BaggageQuantity">
															<xsl:attribute name="BaggageQuantity" namespace="">
																<xsl:value-of select="number(.)"/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@VendorCarType | ns0:VehAvailCore/ns0:Vehicle/@Code">
															<xsl:attribute name="{name()}">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@UnitOfMeasureQuantity">
															<xsl:attribute name="UnitOfMeasureQuantity" namespace="">
																<xsl:value-of select="number(.)"/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@UnitOfMeasure | ns0:VehAvailCore/ns0:Vehicle/@UnitOfMeasureCode | ns0:VehAvailCore/ns0:Vehicle/@Start | ns0:VehAvailCore/ns0:Vehicle/@Duration | ns0:VehAvailCore/ns0:Vehicle/@End | ns0:VehAvailCore/ns0:Vehicle/@OdometerUnitOfMeasure | ns0:VehAvailCore/ns0:Vehicle/@Description">
															<xsl:attribute name="{name()}">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehType">
															<ns0:VehType>
																<xsl:copy-of select="@VehicleCategory"/>
																<xsl:copy-of select="@DoorCount"/>
															</ns0:VehType>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehClass">
															<ns0:VehClass>
																<xsl:copy-of select="@Size"/>
															</ns0:VehClass>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehMakeModel">
															<ns0:VehMakeModel>
																<xsl:copy-of select="@Name"/>
																<xsl:copy-of select="@Code"/>
																<xsl:copy-of select="@ModelYear"/>
															</ns0:VehMakeModel>
														</xsl:for-each>
														<xsl:copy-of select="ns0:VehAvailCore/ns0:Vehicle/ns0:PictureURL"/>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehIdentity">
															<ns0:VehIdentity>
																<xsl:for-each select="@VehicleAssetNumber | @LicensePlateNumber | @StateProvCode | @CountryCode | @VehicleID_Number | @VehicleColor">
																	<xsl:attribute name="{name()}" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
															</ns0:VehIdentity>
														</xsl:for-each>
													</ns0:Vehicle>
													<xsl:for-each select="ns0:VehAvailCore/ns0:RentalRate">
														<ns0:RentalRate>
															<xsl:for-each select="@*[name()='QuoteID']">
																<xsl:attribute name="QuoteID" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="ns0:RateDistance">
																<ns0:RateDistance>
																	<xsl:for-each select="@*[name()='Unlimited']">
																		<xsl:attribute name="Unlimited" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@*[name()='Quantity']">
																		<xsl:attribute name="Quantity" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@DistUnitName | @VehiclePeriodUnitName">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																</ns0:RateDistance>
															</xsl:for-each>
															<xsl:for-each select="ns0:VehicleCharges">
																<ns0:VehicleCharges>
																	<xsl:for-each select="ns0:VehicleCharge">
																		<ns0:VehicleCharge>
																			<xsl:copy-of select="@Purpose"/>
																			<xsl:for-each select="@*[name()='CurrencyCode']">
																				<xsl:attribute name="CurrencyCode" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@*[name()='DecimalPlaces']">
																				<xsl:attribute name="DecimalPlaces" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@*[name()='Amount']">
																				<xsl:attribute name="Amount" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@*[name()='TaxInclusive']">
																				<xsl:attribute name="TaxInclusive" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@*[name()='Description']">
																				<xsl:attribute name="Description" namespace="">
{substring(.,0,62)}
</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@*[name()='GuaranteedInd' or name()='IncludedInRate' or name()='IncludedInEstTotalInd' or name()='RateConvertInd' or name()='RequiredInd']">
																				<xsl:attribute name="{name()}" namespace="">
{boolean(translate(normalize-space(string(.)),' 0false',''))}
</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:TaxAmounts">
																				<ns0:TaxAmounts>
																					<xsl:for-each select="ns0:TaxAmount">
																						<ns0:TaxAmount>
																							<xsl:for-each select="@Total">
																								<xsl:attribute name="Total" namespace="">
{number(.)}
</xsl:attribute>
																							</xsl:for-each>
																							<xsl:copy-of select="@CurrencyCode"/>
																							<xsl:for-each select="@*[name()='TaxCode' or name()='Percentage' or name()='Description']">
																								<xsl:attribute name="{name()}" namespace="">
																									<xsl:choose>
																										<xsl:when test="name()='Percentage'">
																											<xsl:value-of select="number(.)"/>
																										</xsl:when>
																										<xsl:otherwise>
																											<xsl:value-of select="."/>
																										</xsl:otherwise>
																									</xsl:choose>
																								</xsl:attribute>
																							</xsl:for-each>
																						</ns0:TaxAmount>
																					</xsl:for-each>
																				</ns0:TaxAmounts>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:MinMax">
																				<ns0:MinMax>
																					<xsl:for-each select="@*[name()='MaxCharge' or name()='MinCharge' or name()='MaxChargeDays']">
																						<xsl:attribute name="{name()}" namespace="">
{number(.)}
</xsl:attribute>
																					</xsl:for-each>
																				</ns0:MinMax>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Calculation">
																				<ns0:Calculation>
																					<xsl:for-each select="@*[name()='UnitCharge' or name()='UnitName']">
																						<xsl:attribute name="{name()}" namespace="">
																							<xsl:choose>
																								<xsl:when test="name()='UnitCharge'">
																									<xsl:value-of select="number(.)"/>
																								</xsl:when>
																								<xsl:otherwise>
																									<xsl:value-of select="."/>
																								</xsl:otherwise>
																							</xsl:choose>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Quantity">
																						<xsl:attribute name="Quantity" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Percentage">
																						<xsl:attribute name="Percentage" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Applicability">
																						<xsl:attribute name="Applicability" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@MaxQuantity">
																						<xsl:attribute name="MaxQuantity" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Total">
																						<xsl:attribute name="Total" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																				</ns0:Calculation>
																			</xsl:for-each>
																		</ns0:VehicleCharge>
																	</xsl:for-each>
																</ns0:VehicleCharges>
															</xsl:for-each>
															<xsl:for-each select="ns0:RateQualifier">
																<ns0:RateQualifier>
																	<xsl:for-each select="@TravelPurpose | @RateCategory | @CorpDiscountNmbr | @PromotionCode | @PromotionVendorCode | @RateQualifier | @RatePeriod">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@GuaranteedInd">
																		<xsl:attribute name="GuaranteedInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@ArriveByFlight">
																		<xsl:attribute name="ArriveByFlight" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@RateAuthorizationCode | @VendorRateID | @TourInfoRPH | @CustLoyaltyRPH">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@*[name()='QuoteID']">
																		<xsl:attribute name="{name()}">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:copy-of select="ns0:PromoDesc"/>
																	<xsl:for-each select="ns0:RateComments">
																		<ns0:RateComments>
																			<xsl:for-each select="ns0:RateComment">
																				<ns0:RateComment>
																					<xsl:for-each select="@*[name()='Formatted']">
																						<xsl:attribute name="{name()}" namespace="">
																							<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Language | @TextFormat | @Name">
																						<xsl:attribute name="{name()}" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:value-of select="."/>
																				</ns0:RateComment>
																			</xsl:for-each>
																		</ns0:RateComments>
																	</xsl:for-each>
																</ns0:RateQualifier>
															</xsl:for-each>
															<xsl:for-each select="ns0:RateRestrictions">
																<ns0:RateRestrictions>
																	<xsl:for-each select="@*[name()='ArriveByFlight' or name()='MinimumDayInd' or name()='MaximumDayInd' or name()='AdvancedBookingInd' or name()='RestrictedMileageInd' or name()='CorporateRateInd' or name()='GuaranteeReqInd' or name()='OvernightInd']">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@MaximumVehiclesAllowed">
																		<xsl:attribute name="MaximumVehiclesAllowed" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@OneWayPolicy">
																		<xsl:attribute name="OneWayPolicy" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@CancellationPenaltyInd">
																		<xsl:attribute name="CancellationPenaltyInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@ModificationPenaltyInd">
																		<xsl:attribute name="ModificationPenaltyInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@MinimumAge">
																		<xsl:attribute name="MinimumAge" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@MaximumAge">
																		<xsl:attribute name="MaximumAge" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@NoShowFeeInd">
																		<xsl:attribute name="NoShowFeeInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																</ns0:RateRestrictions>
															</xsl:for-each>
															<xsl:for-each select="ns0:RateGuarantee">
																<ns0:RateGuarantee>
																	<xsl:for-each select="@AbsoluteDeadline">
																		<xsl:attribute name="AbsoluteDeadline" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@OffsetTimeUnit">
																		<xsl:attribute name="OffsetTimeUnit" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@OffsetUnitMultiplier">
																		<xsl:attribute name="OffsetUnitMultiplier" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@OffsetDropTime">
																		<xsl:attribute name="OffsetDropTime" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:Description">
																		<ns0:Description>
																			<xsl:copy-of select="@node()"/>
																			<xsl:copy-of select="node()"/>
																		</ns0:Description>
																	</xsl:for-each>
																</ns0:RateGuarantee>
															</xsl:for-each>
															<xsl:for-each select="ns0:PickupReturnRule">
																<ns0:PickupReturnRule>
																	<xsl:copy-of select="@node()"/>
																	<xsl:copy-of select="node()"/>
																</ns0:PickupReturnRule>
															</xsl:for-each>
															<xsl:for-each select="ns0:NoShowFeeInfo">
																<ns0:NoShowFeeInfo>
																	<xsl:call-template name="tbf:tbf1_NoShowFeeType">
																		<xsl:with-param name="input" select="."/>
																	</xsl:call-template>
																</ns0:NoShowFeeInfo>
															</xsl:for-each>
														</ns0:RentalRate>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:TotalCharge">
														<ns0:TotalCharge>
															<xsl:for-each select="@RateTotalAmount">
																<xsl:attribute name="RateTotalAmount" namespace="">
																	<xsl:value-of select="number(.)"/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="@EstimatedTotalAmount">
																<xsl:attribute name="EstimatedTotalAmount" namespace="">
																	<xsl:value-of select="number(.)"/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="@CurrencyCode">
																<xsl:attribute name="CurrencyCode" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="@DecimalPlaces">
																<xsl:attribute name="DecimalPlaces" namespace="">
																	<xsl:value-of select="number(.)"/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="@*[name()='RateConvertInd']">
																<xsl:attribute name="{name()}" namespace="">
																	<xsl:value-of select="boolean(translate(normalize-space(.), ' 0false', ''))"/>
																</xsl:attribute>
															</xsl:for-each>
														</ns0:TotalCharge>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:PricedEquips">
														<ns0:PricedEquips>
															<xsl:for-each select="ns0:PricedEquip">
																<ns0:PricedEquip>
																	<xsl:for-each select="@*[name()='Required']">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(.), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<ns0:Equipment>
																		<xsl:for-each select="ns0:Equipment/@*[name()='EquipType']">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Equipment/@*[name()='Quantity']">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="number(.)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Equipment/@*[name()='Restriction']">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Equipment/ns0:Description">
																			<ns0:Description>
																				<xsl:value-of select="substring(., 0, 62)"/>
																			</ns0:Description>
																		</xsl:for-each>
																	</ns0:Equipment>
																	<ns0:Charge>
																		<xsl:for-each select="ns0:Charge/@*[name()='CurrencyCode']">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@DecimalPlaces | ns0:Charge/@Amount">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@*[name()='TaxInclusive']">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(.), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@*[name()='Description']">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="substring(., 0, 62)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@GuaranteedInd | ns0:Charge/@IncludedInRate | ns0:Charge/@IncludedInEstTotalInd | ns0:Charge/@RateConvertInd">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/ns0:TaxAmounts">
																			<ns0:TaxAmounts>
																				<xsl:for-each select="ns0:TaxAmount">
																					<ns0:TaxAmount>
																						<xsl:attribute name="Total" namespace="">
																							<xsl:value-of select="number(@Total)"/>
																						</xsl:attribute>
																						<xsl:copy-of select="@CurrencyCode"/>
																						<xsl:for-each select="@*[name() = 'TaxCode' or name() = 'Percentage' or name() = 'Description']">
																							<xsl:attribute name="{name()}">
																								<xsl:choose>
																									<xsl:when test="name()='Percentage'">
																										<xsl:value-of select="number(.)"/>
																									</xsl:when>
																									<xsl:otherwise>
																										<xsl:value-of select="."/>
																									</xsl:otherwise>
																								</xsl:choose>
																							</xsl:attribute>
																						</xsl:for-each>
																					</ns0:TaxAmount>
																				</xsl:for-each>
																			</ns0:TaxAmounts>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/ns0:MinMax">
																			<ns0:MinMax>
																				<xsl:for-each select="@*[name() = 'MaxCharge' or name() = 'MinCharge' or name() = 'MaxChargeDays']">
																					<xsl:attribute name="{name()}" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																			</ns0:MinMax>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/ns0:Calculation">
																			<ns0:Calculation>
																				<xsl:for-each select="@*[name() = 'UnitCharge' or name() = 'UnitName' or name() = 'Quantity' or name() = 'Percentage' or name() = 'Applicability' or name() = 'MaxQuantity' or name() = 'Total']">
																					<xsl:attribute name="{name()}" namespace="">
																						<xsl:choose>
																							<xsl:when test="name()='UnitName' or name()='Applicability'">
																								<xsl:value-of select="."/>
																							</xsl:when>
																							<xsl:otherwise>
																								<xsl:value-of select="number(.)"/>
																							</xsl:otherwise>
																						</xsl:choose>
																					</xsl:attribute>
																				</xsl:for-each>
																			</ns0:Calculation>
																		</xsl:for-each>
																	</ns0:Charge>
																</ns0:PricedEquip>
															</xsl:for-each>
														</ns0:PricedEquips>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Fees">
														<ns0:Fees>
															<xsl:for-each select="ns0:Fee">
																<ns0:Fee>
																	<xsl:copy-of select="@Purpose"/>
																	<xsl:for-each select="@*[name()='CurrencyCode' or name()='Description']">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@*[name()='DecimalPlaces' or name()='Amount']">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@*[name()='TaxInclusive' or name()='GuaranteedInd' or name()='IncludedInRate' or name()='IncludedInEstTotalInd' or name()='RateConvertInd' or name()='RequiredInd']">
																		<xsl:attribute name="{name()}" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)),' 0false',''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:TaxAmounts">
																		<ns0:TaxAmounts>
																			<xsl:for-each select="ns0:TaxAmount">
																				<ns0:TaxAmount>
																					<xsl:attribute name="Total" namespace="">
																						<xsl:value-of select="number(@Total)"/>
																					</xsl:attribute>
																					<xsl:copy-of select="@CurrencyCode"/>
																					<xsl:for-each select="@*[name()='TaxCode' or name()='Description']">
																						<xsl:attribute name="{name()}" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@*[name()='Percentage']">
																						<xsl:attribute name="Percentage" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																				</ns0:TaxAmount>
																			</xsl:for-each>
																		</ns0:TaxAmounts>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:MinMax">
																		<ns0:MinMax>
																			<xsl:for-each select="@*[name()='MaxCharge']">
																				<xsl:attribute name="MaxCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@*[name()='MinCharge' or name()='MaxChargeDays']">
																				<xsl:attribute name="{name()}" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</ns0:MinMax>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:Calculation">
																		<ns0:Calculation>
																			<xsl:for-each select="@*[name()='UnitCharge' or name()='Quantity' or name()='Percentage' or name()='MaxQuantity' or name()='Total']">
																				<xsl:attribute name="{name()}" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@*[name()='UnitName' or name()='Applicability']">
																				<xsl:attribute name="{name()}" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</ns0:Calculation>
																	</xsl:for-each>
																</ns0:Fee>
															</xsl:for-each>
														</ns0:Fees>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Reference">
														<ns0:Reference>
															<xsl:copy-of select="@Type"/>
															<xsl:copy-of select="@ID"/>
															<xsl:for-each select="@URL | @Instance | @ID_Context | @DateTime">
																<xsl:attribute name="{name()}" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="ns0:CompanyName">
																<ns0:CompanyName>
																	<xsl:copy-of select="@*"/>
																	<xsl:copy-of select="node()"/>
																</ns0:CompanyName>
															</xsl:for-each>
															<xsl:for-each select="ns0:TPA_Extensions">
																<ns0:TPA_Extensions>
																	<xsl:copy-of select="@*"/>
																	<xsl:copy-of select="node()"/>
																</ns0:TPA_Extensions>
															</xsl:for-each>
														</ns0:Reference>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Vendor">
														<ns0:Vendor>
															<xsl:copy-of select="@*"/>
															<xsl:copy-of select="node()"/>
														</ns0:Vendor>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:VendorLocation">
														<ns0:VendorLocation>
															<xsl:copy-of select="@*"/>
															<xsl:copy-of select="node()"/>
														</ns0:VendorLocation>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:DropOffLocation">
														<ns0:DropOffLocation>
															<xsl:copy-of select="@*"/>
															<xsl:copy-of select="node()"/>
														</ns0:DropOffLocation>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Discount">
														<ns0:Discount>
															<xsl:copy-of select="@*"/>
															<xsl:copy-of select="node()"/>
														</ns0:Discount>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:TPA_Extensions">
														<ns0:TPA_Extensions>
															<xsl:for-each select="ns0:ExtendedVehicle">
																<ns0:ExtendedVehicle>
																	<xsl:if test="@KeylessAccess">
																		<xsl:attribute name="KeylessAccess">
																			<xsl:value-of select="@KeylessAccess"/>
																		</xsl:attribute>
																	</xsl:if>
																</ns0:ExtendedVehicle>
															</xsl:for-each>
														</ns0:TPA_Extensions>
													</xsl:for-each>
												</ns0:VehAvailCore>
												<xsl:for-each select="ns0:VehAvailInfo">
													<ns0:VehAvailInfo>
														<xsl:if test="@ChargeablePeriod">
															<xsl:attribute name="ChargeablePeriod">
																<xsl:value-of select="@ChargeablePeriod"/>
															</xsl:attribute>
														</xsl:if>
														<xsl:for-each select="ns0:PricedCoverages">
															<ns0:PricedCoverages>
																<xsl:for-each select="ns0:PricedCoverage">
																	<ns0:PricedCoverage>
																		<xsl:if test="@Required">
																			<xsl:attribute name="Required">
																				<xsl:value-of select="boolean(translate(normalize-space(string(@Required)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:if>
																		<ns0:Coverage>
																			<xsl:attribute name="CoverageType">
																				<xsl:value-of select="ns0:Coverage/@CoverageType"/>
																			</xsl:attribute>
																			<xsl:if test="ns0:Coverage/@Code">
																				<xsl:attribute name="Code">
																					<xsl:value-of select="ns0:Coverage/@Code"/>
																				</xsl:attribute>
																			</xsl:if>
																			<xsl:for-each select="ns0:Coverage/ns0:Details">
																				<ns0:Details>
																					<xsl:copy-of select="@CoverageTextType"/>
																					<xsl:if test="@Formatted">
																						<xsl:attribute name="Formatted">
																							<xsl:value-of select="boolean(translate(normalize-space(string(@Formatted)), ' 0false', ''))"/>
																						</xsl:attribute>
																					</xsl:if>
																					<xsl:for-each select="@Language | @TextFormat">
																						<xsl:attribute name="{name()}" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:value-of select="."/>
																				</ns0:Details>
																			</xsl:for-each>
																		</ns0:Coverage>
																		<ns0:Charge>
																			<xsl:if test="ns0:Charge/@CurrencyCode">
																				<xsl:attribute name="CurrencyCode">
																					<xsl:value-of select="ns0:Charge/@CurrencyCode"/>
																				</xsl:attribute>
																			</xsl:if>
																			<xsl:for-each select="ns0:Charge/@DecimalPlaces | ns0:Charge/@Amount">
																				<xsl:attribute name="{name()}" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:if test="ns0:Charge/@TaxInclusive">
																				<xsl:attribute name="TaxInclusive">
																					<xsl:value-of select="boolean(translate(normalize-space(string(ns0:Charge/@TaxInclusive)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:if>
																			<xsl:for-each select="ns0:Charge/@*[name() = 'Description']">
																				<xsl:attribute name="Description" namespace="">
																					<xsl:value-of select="substring(., 0, 62)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@GuaranteedInd | ns0:Charge/@IncludedInRate | ns0:Charge/@IncludedInEstTotalInd | ns0:Charge/@RateConvertInd">
																				<xsl:attribute name="{name()}" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/ns0:TaxAmounts">
																				<ns0:TaxAmounts>
																					<xsl:for-each select="ns0:TaxAmount">
																						<ns0:TaxAmount>
																							<xsl:attribute name="Total" namespace="">
																								<xsl:value-of select="number(@Total)"/>
																							</xsl:attribute>
																							<xsl:copy-of select="@CurrencyCode"/>
																							<xsl:for-each select="@*[name() = 'TaxCode']">
																								<xsl:attribute name="TaxCode" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:for-each select="@*[name() = 'Percentage']">
																								<xsl:attribute name="Percentage" namespace="">
																									<xsl:value-of select="number(.)"/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:for-each select="@*[name() = 'Description']">
																								<xsl:attribute name="Description" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																						</ns0:TaxAmount>
																					</xsl:for-each>
																				</ns0:TaxAmounts>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/ns0:MinMax">
																				<ns0:MinMax>
																					<xsl:for-each select="@*[name() = 'MaxCharge']">
																						<xsl:attribute name="MaxCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@*[name() = 'MinCharge']">
																						<xsl:attribute name="MinCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@*[name() = 'MaxChargeDays']">
																						<xsl:attribute name="MaxChargeDays" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																				</ns0:MinMax>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/ns0:Calculation">
																				<ns0:Calculation>
																					<xsl:for-each select="@*[name() = 'UnitCharge']">
																						<xsl:attribute name="UnitCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@*[name() = 'UnitName']">
																						<xsl:attribute name="UnitName" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@*[name() = 'Quantity']">
																						<xsl:attribute name="Quantity" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Percentage">
																						<xsl:attribute name="Percentage" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Applicability">
																						<xsl:attribute name="Applicability" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@MaxQuantity">
																						<xsl:attribute name="MaxQuantity" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Total">
																						<xsl:attribute name="Total" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																				</ns0:Calculation>
																			</xsl:for-each>
																		</ns0:Charge>
																		<xsl:for-each select="ns0:Deductible">
																			<ns0:Deductible>
																				<xsl:for-each select="@CurrencyCode">
																					<xsl:attribute name="CurrencyCode" namespace="">
																						<xsl:value-of select="."/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="@DecimalPlaces">
																					<xsl:attribute name="DecimalPlaces" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="@Amount">
																					<xsl:attribute name="Amount" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="@LiabilityAmount">
																					<xsl:attribute name="LiabilityAmount" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="@ExcessAmount">
																					<xsl:attribute name="ExcessAmount" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																			</ns0:Deductible>
																		</xsl:for-each>
																	</ns0:PricedCoverage>
																</xsl:for-each>
															</ns0:PricedCoverages>
														</xsl:for-each>
														<xsl:for-each select="ns0:PaymentRules">
															<ns0:PaymentRules>
																<xsl:for-each select="ns0:PaymentRule">
																	<ns0:PaymentRule>
																		<xsl:attribute name="RuleType" namespace="">
																			<xsl:value-of select="@RuleType"/>
																		</xsl:attribute>
																		<xsl:for-each select="@CurrencyCode">
																			<xsl:attribute name="CurrencyCode" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@DecimalPlaces">
																			<xsl:attribute name="DecimalPlaces" namespace="">
																				<xsl:value-of select="number(.)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@Amount">
																			<xsl:attribute name="Amount" namespace="">
																				<xsl:value-of select="number(.)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@Percent">
																			<xsl:attribute name="Percent" namespace="">
																				<xsl:value-of select="number(.)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@DateTime">
																			<xsl:attribute name="DateTime" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@PaymentType">
																			<xsl:attribute name="PaymentType" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@RateConvertedInd">
																			<xsl:attribute name="RateConvertedInd" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@AbsoluteDeadline | @OffsetTimeUnit">
																			<xsl:attribute name="{name()}" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="@*[name()='OffsetUnitMultiplier' or name()='OffsetDropTime']">
																			<xsl:attribute name="{name()}">
																				<xsl:choose>
																					<xsl:when test="name()='OffsetUnitMultiplier'">
																						<xsl:value-of select="number(.)"/>
																					</xsl:when>
																					<xsl:otherwise>
																						<xsl:value-of select="."/>
																					</xsl:otherwise>
																				</xsl:choose>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:value-of select="."/>
																	</ns0:PaymentRule>
																</xsl:for-each>
															</ns0:PaymentRules>
														</xsl:for-each>
													</ns0:VehAvailInfo>
												</xsl:for-each>
												<xsl:for-each select="ns0:AdvanceBooking">
													<ns0:AdvanceBooking>
														<xsl:for-each select="@AbsoluteDeadline | @OffsetTimeUnit">
															<xsl:attribute name="{name()}" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="@*[name()='OffsetUnitMultiplier' or name()='OffsetDropTime' or name()='RulesApplyInd']">
															<xsl:attribute name="{name()}">
																<xsl:choose>
																	<xsl:when test="name()='OffsetUnitMultiplier'">
																		<xsl:value-of select="number(.)"/>
																	</xsl:when>
																	<xsl:when test="name()='RulesApplyInd'">
																		<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																	</xsl:when>
																	<xsl:otherwise>
																		<xsl:value-of select="."/>
																	</xsl:otherwise>
																</xsl:choose>
															</xsl:attribute>
														</xsl:for-each>
													</ns0:AdvanceBooking>
												</xsl:for-each>
											</ns0:VehAvail>
										</xsl:for-each>
									</ns0:VehAvails>
								</ns0:VehVendorAvail>
							</xsl:for-each>
						</ns0:VehVendorAvails>
					</ns0:VehAvailRSCore>
				</xsl:for-each>
			</xsl:for-each>
		</ns0:OTA_VehAvailRateRS>
	</xsl:template>
</xsl:stylesheet>