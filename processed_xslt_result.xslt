<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tbf="http://www.altova.com/MapForce/UDF/tbf" xmlns:ns0="http://www.opentravel.org/OTA/2003/05" xmlns:xs="http://www.w3.org/2001/XMLSchema" version="1.0" exclude-result-prefixes="tbf ns0 xs">
	<xsl:template name="tbf:tbf1_NoShowFeeType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/node()">
			
			<xsl:choose>
				<xsl:when test="self::*">
					<xsl:when test="self::ns0:Deadline">
						<xsl:element name="{name()}" namespace="{namespace-uri()}">
							<xsl:call-template name="tbf:tbf2_">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:when>
					<xsl:if test="self::ns0:GracePeriod">
						<xsl:element name="{name(.)}" namespace="{namespace-uri(.)}">
							<xsl:call-template name="tbf:tbf3_">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:if>
					<xsl:when test="self::ns0:FeeAmount">
						<xsl:element name="{name()}" namespace="{namespace-uri()}">
							<xsl:call-template name="tbf:tbf4_">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:when>
					<xsl:if test="self::ns0:Description">
						<xsl:element name="{name(.)}" namespace="{namespace-uri(.)}">
							<xsl:call-template name="tbf:tbf5_FormattedTextTextType">
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
	</xsl:template><xsl:template name="tbf:tbf2_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@AbsoluteDeadline | $input/@OffsetTimeUnit | $input/@OffsetUnitMultiplier | $input/@OffsetDropTime">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		</xsl:template><xsl:template name="tbf:tbf3_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@AbsoluteDeadline | $input/@OffsetTimeUnit | $input/@OffsetUnitMultiplier | $input/@OffsetDropTime">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		</xsl:template><xsl:template name="tbf:tbf4_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@CurrencyCode | $input/@DecimalPlaces | $input/@Amount | $input/@RateConvertedInd">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		</xsl:template><xsl:template name="tbf:tbf5_FormattedTextTextType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@Formatted | $input/@Language | $input/@TextFormat">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:value-of select="$input"/>
	</xsl:template><xsl:template name="tbf:tbf6_VehicleChargeType">
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
	</xsl:template><xsl:template name="tbf:tbf7_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/node()">
			
			<xsl:choose>
				<xsl:when test="self::ns0:TaxAmount">
						<xsl:element name="{name(.)}" namespace="{namespace-uri(.)}">
							<xsl:call-template name="tbf:tbf8_">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:when>
				<xsl:when test="not(self::text()) and not(self::*)">
					<xsl:copy-of select="."/>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template><xsl:template name="tbf:tbf8_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@Total | $input/@CurrencyCode | $input/@Percentage | $input/@Description">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		</xsl:template><xsl:template name="tbf:tbf9_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@MaxCharge | $input/@MinCharge | $input/@MaxChargeDays">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		</xsl:template><xsl:template name="tbf:tbf10_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@UnitCharge | $input/@UnitName | $input/@Quantity | $input/@Percentage | $input/@Applicability | $input/@MaxQuantity | $input/@Total">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		</xsl:template><xsl:template name="tbf:tbf11_PaymentRulesType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/node()">
			
			<xsl:choose>
				<xsl:when test="self::ns0:PaymentRule">
						<xsl:element name="{name(.)}" namespace="{namespace-uri(.)}">
							<xsl:call-template name="tbf:tbf12_MonetaryRuleType">
								<xsl:with-param name="input" select="."/>
							</xsl:call-template>
						</xsl:element>
					</xsl:when>
				<xsl:when test="not(self::text()) and not(self::*)">
					<xsl:copy-of select="."/>
				</xsl:when>
			</xsl:choose>
		</xsl:for-each>
	</xsl:template><xsl:template name="tbf:tbf12_MonetaryRuleType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@CurrencyCode | $input/@DecimalPlaces | $input/@Amount | $input/@RuleType | $input/@Percent | $input/@DateTime | $input/@PaymentType | $input/@RateConvertedInd | $input/@AbsoluteDeadline | $input/@OffsetTimeUnit | $input/@OffsetUnitMultiplier | $input/@OffsetDropTime">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:value-of select="$input"/>
	</xsl:template><xsl:template name="tbf:tbf13_">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@SeriesCode | $input/@EffectiveDate | $input/@ExpireDate | $input/@ExpireDateExclusiveIndicator | $input/@BillingNumber | $input/@SupplierIdentifier | $input/@Identifier | $input/@ValueType | $input/@ElectronicIndicator">
			
			<xsl:attribute name="{name()}">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		</xsl:template><xsl:output method="xml" encoding="UTF-8" indent="yes"/>
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
								<xsl:attribute name="Type" namespace="">
									<xsl:value-of select="@Type"/>
								</xsl:attribute>
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
								<xsl:for-each select="@Code">
									
									<xsl:attribute name="Code" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@DocURL">
									
									<xsl:attribute name="DocURL" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@Status">
									
									<xsl:attribute name="Status" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@Tag">
									
									<xsl:attribute name="Tag" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@RecordID">
									
									<xsl:attribute name="RecordID" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@RPH">
									
									<xsl:attribute name="RPH" namespace="">
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
							<xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime">
								
								<xsl:attribute name="PickUpDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@ReturnDateTime">
								
								<xsl:attribute name="ReturnDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@StartChargesDateTime">
								
								<xsl:attribute name="StartChargesDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@StopChargesDateTime">
								
								<xsl:attribute name="StopChargesDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@OneWayIndicator">
								
								<xsl:attribute name="OneWayIndicator" namespace="">
									<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@MultiIslandRentalDays">
								
								<xsl:attribute name="MultiIslandRentalDays" namespace="">
									<xsl:value-of select="number(.)"/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@Quantity">
								
								<xsl:attribute name="Quantity" namespace="">
									<xsl:value-of select="number(.)"/>
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
										<xsl:attribute name="CodeContext" namespace="">IATA</xsl:attribute>
									</xsl:if>
									<xsl:for-each select="@LocationCode">
										
										<xsl:attribute name="LocationCode" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:for-each select="@ExtendedLocationCode">
										
										<xsl:attribute name="ExtendedLocationCode" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:for-each select="@CounterLocation">
										
										<xsl:attribute name="CounterLocation" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:value-of select="."/>
								</ns0:PickUpLocation>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/ns0:ReturnLocation">
								
								<ns0:ReturnLocation>
									<xsl:if test="@LocationCode">
										<xsl:attribute name="CodeContext" namespace="">IATA</xsl:attribute>
									</xsl:if>
									<xsl:for-each select="@LocationCode">
										
										<xsl:attribute name="LocationCode" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:for-each select="@ExtendedLocationCode">
										
										<xsl:attribute name="ExtendedLocationCode" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:for-each select="@CounterLocation">
										
										<xsl:attribute name="CounterLocation" namespace="">
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
											<xsl:for-each select="@TravelSector">
												
												<xsl:attribute name="TravelSector" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:for-each select="@Code">
												
												<xsl:attribute name="Code" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:for-each select="@CodeContext">
												
												<xsl:attribute name="CodeContext" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:for-each select="@CountryCode">
												
												<xsl:attribute name="CountryCode" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:for-each select="@Division">
												
												<xsl:attribute name="Division" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:for-each select="@Department">
												
												<xsl:attribute name="Department" namespace="">
													<xsl:value-of select="."/>
												</xsl:attribute>
											</xsl:for-each>
											<xsl:value-of select="."/>
										</ns0:Vendor>
									</xsl:for-each>
									<ns0:VehAvails>
										<xsl:for-each select="ns0:VehAvails/@RateCategory">
											
											<xsl:attribute name="RateCategory" namespace="">
												<xsl:value-of select="."/>
											</xsl:attribute>
										</xsl:for-each>
										<xsl:for-each select="ns0:VehAvails/@RatePeriod">
											
											<xsl:attribute name="RatePeriod" namespace="">
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
														<xsl:attribute name="CodeContext" namespace="">ACRISS</xsl:attribute>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@AirConditionInd">
															
															<xsl:attribute name="AirConditionInd" namespace="">
																<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@TransmissionType">
															
															<xsl:attribute name="TransmissionType" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@FuelType">
															
															<xsl:attribute name="FuelType" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@DriveType">
															
															<xsl:attribute name="DriveType" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@PassengerQuantity">
															
															<xsl:attribute name="PassengerQuantity" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@BaggageQuantity">
															
															<xsl:attribute name="BaggageQuantity" namespace="">
																<xsl:value-of select="number(.)"/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@VendorCarType">
															
															<xsl:attribute name="VendorCarType" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@Code">
															
															<xsl:attribute name="Code" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@UnitOfMeasureQuantity">
															
															<xsl:attribute name="UnitOfMeasureQuantity" namespace="">
																<xsl:value-of select="number(.)"/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@UnitOfMeasure">
															
															<xsl:attribute name="UnitOfMeasure" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@UnitOfMeasureCode">
															
															<xsl:attribute name="UnitOfMeasureCode" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@Start">
															
															<xsl:attribute name="Start" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@Duration">
															
															<xsl:attribute name="Duration" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@End">
															
															<xsl:attribute name="End" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@OdometerUnitOfMeasure">
															
															<xsl:attribute name="OdometerUnitOfMeasure" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/@Description">
															
															<xsl:attribute name="Description" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehType">
															
															<ns0:VehType>
																<xsl:attribute name="VehicleCategory" namespace="">
																	<xsl:value-of select="@VehicleCategory"/>
																</xsl:attribute>
																<xsl:for-each select="@DoorCount">
																	
																	<xsl:attribute name="DoorCount" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
															</ns0:VehType>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehClass">
															
															<ns0:VehClass>
																<xsl:attribute name="Size" namespace="">
																	<xsl:value-of select="@Size"/>
																</xsl:attribute>
															</ns0:VehClass>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehMakeModel">
															
															<ns0:VehMakeModel>
																<xsl:attribute name="Name" namespace="">
																	<xsl:value-of select="@Name"/>
																</xsl:attribute>
																<xsl:for-each select="@Code">
																	
																	<xsl:attribute name="Code" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:for-each select="@ModelYear">
																	
																	<xsl:attribute name="ModelYear" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
															</ns0:VehMakeModel>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:PictureURL">
															
															<ns0:PictureURL>
																<xsl:value-of select="."/>
															</ns0:PictureURL>
														</xsl:for-each>
														<xsl:for-each select="ns0:VehAvailCore/ns0:Vehicle/ns0:VehIdentity">
															
															<ns0:VehIdentity>
																<xsl:for-each select="@VehicleAssetNumber">
																	
																	<xsl:attribute name="VehicleAssetNumber" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:for-each select="@LicensePlateNumber">
																	
																	<xsl:attribute name="LicensePlateNumber" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:for-each select="@StateProvCode">
																	
																	<xsl:attribute name="StateProvCode" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:for-each select="@CountryCode">
																	
																	<xsl:attribute name="CountryCode" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:for-each select="@VehicleID_Number">
																	
																	<xsl:attribute name="VehicleID_Number" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
																<xsl:for-each select="@VehicleColor">
																	
																	<xsl:attribute name="VehicleColor" namespace="">
																		<xsl:value-of select="."/>
																	</xsl:attribute>
																</xsl:for-each>
															</ns0:VehIdentity>
														</xsl:for-each>
													</ns0:Vehicle>
													<xsl:for-each select="ns0:VehAvailCore/ns0:RentalRate">
														
														<ns0:RentalRate>
															<xsl:for-each select="@QuoteID">
																
																<xsl:attribute name="QuoteID" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="ns0:RateDistance">
																
																<ns0:RateDistance>
																	<xsl:attribute name="Unlimited" namespace="">
																		<xsl:value-of select="boolean(translate(normalize-space(string(@Unlimited)), ' 0false', ''))"/>
																	</xsl:attribute>
																	<xsl:for-each select="@Quantity">
																		
																		<xsl:attribute name="Quantity" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@DistUnitName">
																		
																		<xsl:attribute name="DistUnitName" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@VehiclePeriodUnitName">
																		
																		<xsl:attribute name="VehiclePeriodUnitName" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																</ns0:RateDistance>
															</xsl:for-each>
															<xsl:for-each select="ns0:VehicleCharges">
																
																<ns0:VehicleCharges>
																	<xsl:for-each select="ns0:VehicleCharge">
																		
																		<ns0:VehicleCharge>
																			<xsl:attribute name="Purpose" namespace="">
																				<xsl:value-of select="@Purpose"/>
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
																			<xsl:for-each select="@TaxInclusive">
																				
																				<xsl:attribute name="TaxInclusive" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@Description">
																				
																				<xsl:attribute name="Description" namespace="">
																					<xsl:value-of select="substring(., 0, 62)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@GuaranteedInd">
																				
																				<xsl:attribute name="GuaranteedInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@IncludedInRate">
																				
																				<xsl:attribute name="IncludedInRate" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@IncludedInEstTotalInd">
																				
																				<xsl:attribute name="IncludedInEstTotalInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@RateConvertInd">
																				
																				<xsl:attribute name="RateConvertInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@RequiredInd">
																				
																				<xsl:attribute name="RequiredInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:TaxAmounts">
																				
																				<ns0:TaxAmounts>
																					<xsl:for-each select="ns0:TaxAmount">
																						
																						<ns0:TaxAmount>
																							<xsl:attribute name="Total" namespace="">
																								<xsl:value-of select="number(@Total)"/>
																							</xsl:attribute>
																							<xsl:attribute name="CurrencyCode" namespace="">
																								<xsl:value-of select="@CurrencyCode"/>
																							</xsl:attribute>
																							<xsl:for-each select="@TaxCode">
																								
																								<xsl:attribute name="TaxCode" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:for-each select="@Percentage">
																								
																								<xsl:attribute name="Percentage" namespace="">
																									<xsl:value-of select="number(.)"/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:for-each select="@Description">
																								
																								<xsl:attribute name="Description" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																						</ns0:TaxAmount>
																					</xsl:for-each>
																				</ns0:TaxAmounts>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:MinMax">
																				
																				<ns0:MinMax>
																					<xsl:for-each select="@MaxCharge">
																						
																						<xsl:attribute name="MaxCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@MinCharge">
																						
																						<xsl:attribute name="MinCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@MaxChargeDays">
																						
																						<xsl:attribute name="MaxChargeDays" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																				</ns0:MinMax>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Calculation">
																				
																				<ns0:Calculation>
																					<xsl:for-each select="@UnitCharge">
																						
																						<xsl:attribute name="UnitCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@UnitName">
																						
																						<xsl:attribute name="UnitName" namespace="">
																							<xsl:value-of select="."/>
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
																	<xsl:for-each select="@TravelPurpose">
																		
																		<xsl:attribute name="TravelPurpose" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@RateCategory">
																		
																		<xsl:attribute name="RateCategory" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@CorpDiscountNmbr">
																		
																		<xsl:attribute name="CorpDiscountNmbr" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@PromotionCode">
																		
																		<xsl:attribute name="PromotionCode" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@PromotionVendorCode">
																		
																		<xsl:attribute name="PromotionVendorCode" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@RateQualifier">
																		
																		<xsl:attribute name="RateQualifier" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@RatePeriod">
																		
																		<xsl:attribute name="RatePeriod" namespace="">
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
																	<xsl:for-each select="@RateAuthorizationCode">
																		
																		<xsl:attribute name="RateAuthorizationCode" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@VendorRateID">
																		
																		<xsl:attribute name="VendorRateID" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@TourInfoRPH">
																		
																		<xsl:attribute name="TourInfoRPH" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@CustLoyaltyRPH">
																		
																		<xsl:attribute name="CustLoyaltyRPH" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@QuoteID">
																		
																		<xsl:attribute name="QuoteID" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:PromoDesc">
																		
																		<ns0:PromoDesc>
																			<xsl:value-of select="."/>
																		</ns0:PromoDesc>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:RateComments">
																		
																		<ns0:RateComments>
																			<xsl:for-each select="ns0:RateComment">
																				
																				<ns0:RateComment>
																					<xsl:for-each select="@Formatted">
																						
																						<xsl:attribute name="Formatted" namespace="">
																							<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Language">
																						
																						<xsl:attribute name="Language" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@TextFormat">
																						
																						<xsl:attribute name="TextFormat" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Name">
																						
																						<xsl:attribute name="Name" namespace="">
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
																	<xsl:for-each select="@ArriveByFlight">
																		
																		<xsl:attribute name="ArriveByFlight" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@MinimumDayInd">
																		
																		<xsl:attribute name="MinimumDayInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@MaximumDayInd">
																		
																		<xsl:attribute name="MaximumDayInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@AdvancedBookingInd">
																		
																		<xsl:attribute name="AdvancedBookingInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@RestrictedMileageInd">
																		
																		<xsl:attribute name="RestrictedMileageInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@CorporateRateInd">
																		
																		<xsl:attribute name="CorporateRateInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@GuaranteeReqInd">
																		
																		<xsl:attribute name="GuaranteeReqInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@MaximumVehiclesAllowed">
																		
																		<xsl:attribute name="MaximumVehiclesAllowed" namespace="">
																			<xsl:value-of select="number(.)"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@OvernightInd">
																		
																		<xsl:attribute name="OvernightInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
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
															<xsl:for-each select="@RateConvertInd">
																
																<xsl:attribute name="RateConvertInd" namespace="">
																	<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																</xsl:attribute>
															</xsl:for-each>
														</ns0:TotalCharge>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:PricedEquips">
														
														<ns0:PricedEquips>
															<xsl:for-each select="ns0:PricedEquip">
																
																<ns0:PricedEquip>
																	<xsl:for-each select="@Required">
																		
																		<xsl:attribute name="Required" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<ns0:Equipment>
																		<xsl:attribute name="EquipType" namespace="">
																			<xsl:value-of select="ns0:Equipment/@EquipType"/>
																		</xsl:attribute>
																		<xsl:for-each select="ns0:Equipment/@Quantity">
																			
																			<xsl:attribute name="Quantity" namespace="">
																				<xsl:value-of select="number(.)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Equipment/@Restriction">
																			
																			<xsl:attribute name="Restriction" namespace="">
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
																		<xsl:for-each select="ns0:Charge/@CurrencyCode">
																			
																			<xsl:attribute name="CurrencyCode" namespace="">
																				<xsl:value-of select="."/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@DecimalPlaces">
																			
																			<xsl:attribute name="DecimalPlaces" namespace="">
																				<xsl:value-of select="number(.)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@Amount">
																			
																			<xsl:attribute name="Amount" namespace="">
																				<xsl:value-of select="number(.)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@TaxInclusive">
																			
																			<xsl:attribute name="TaxInclusive" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@Description">
																			
																			<xsl:attribute name="Description" namespace="">
																				<xsl:value-of select="substring(., 0, 62)"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@GuaranteedInd">
																			
																			<xsl:attribute name="GuaranteedInd" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@IncludedInRate">
																			
																			<xsl:attribute name="IncludedInRate" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@IncludedInEstTotalInd">
																			
																			<xsl:attribute name="IncludedInEstTotalInd" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/@RateConvertInd">
																			
																			<xsl:attribute name="RateConvertInd" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/ns0:TaxAmounts">
																			
																			<ns0:TaxAmounts>
																				<xsl:for-each select="ns0:TaxAmount">
																					
																					<ns0:TaxAmount>
																						<xsl:attribute name="Total" namespace="">
																							<xsl:value-of select="number(@Total)"/>
																						</xsl:attribute>
																						<xsl:attribute name="CurrencyCode" namespace="">
																							<xsl:value-of select="@CurrencyCode"/>
																						</xsl:attribute>
																						<xsl:for-each select="@TaxCode">
																							
																							<xsl:attribute name="TaxCode" namespace="">
																								<xsl:value-of select="."/>
																							</xsl:attribute>
																						</xsl:for-each>
																						<xsl:for-each select="@Percentage">
																							
																							<xsl:attribute name="Percentage" namespace="">
																								<xsl:value-of select="number(.)"/>
																							</xsl:attribute>
																						</xsl:for-each>
																						<xsl:for-each select="@Description">
																							
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
																				<xsl:for-each select="@MaxCharge">
																					
																					<xsl:attribute name="MaxCharge" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="@MinCharge">
																					
																					<xsl:attribute name="MinCharge" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="@MaxChargeDays">
																					
																					<xsl:attribute name="MaxChargeDays" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																			</ns0:MinMax>
																		</xsl:for-each>
																		<xsl:for-each select="ns0:Charge/ns0:Calculation">
																			
																			<ns0:Calculation>
																				<xsl:for-each select="@UnitCharge">
																					
																					<xsl:attribute name="UnitCharge" namespace="">
																						<xsl:value-of select="number(.)"/>
																					</xsl:attribute>
																				</xsl:for-each>
																				<xsl:for-each select="@UnitName">
																					
																					<xsl:attribute name="UnitName" namespace="">
																						<xsl:value-of select="."/>
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
																	</ns0:Charge>
																</ns0:PricedEquip>
															</xsl:for-each>
														</ns0:PricedEquips>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Fees">
														
														<ns0:Fees>
															<xsl:for-each select="ns0:Fee">
																
																<ns0:Fee>
																	<xsl:attribute name="Purpose" namespace="">
																		<xsl:value-of select="@Purpose"/>
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
																	<xsl:for-each select="@TaxInclusive">
																		
																		<xsl:attribute name="TaxInclusive" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@Description">
																		
																		<xsl:attribute name="Description" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@GuaranteedInd">
																		
																		<xsl:attribute name="GuaranteedInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@IncludedInRate">
																		
																		<xsl:attribute name="IncludedInRate" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@IncludedInEstTotalInd">
																		
																		<xsl:attribute name="IncludedInEstTotalInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@RateConvertInd">
																		
																		<xsl:attribute name="RateConvertInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="@RequiredInd">
																		
																		<xsl:attribute name="RequiredInd" namespace="">
																			<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																		</xsl:attribute>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:TaxAmounts">
																		
																		<ns0:TaxAmounts>
																			<xsl:for-each select="ns0:TaxAmount">
																				
																				<ns0:TaxAmount>
																					<xsl:attribute name="Total" namespace="">
																						<xsl:value-of select="number(@Total)"/>
																					</xsl:attribute>
																					<xsl:attribute name="CurrencyCode" namespace="">
																						<xsl:value-of select="@CurrencyCode"/>
																					</xsl:attribute>
																					<xsl:for-each select="@TaxCode">
																						
																						<xsl:attribute name="TaxCode" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Percentage">
																						
																						<xsl:attribute name="Percentage" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Description">
																						
																						<xsl:attribute name="Description" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																				</ns0:TaxAmount>
																			</xsl:for-each>
																		</ns0:TaxAmounts>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:MinMax">
																		
																		<ns0:MinMax>
																			<xsl:for-each select="@MaxCharge">
																				
																				<xsl:attribute name="MaxCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@MinCharge">
																				
																				<xsl:attribute name="MinCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@MaxChargeDays">
																				
																				<xsl:attribute name="MaxChargeDays" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</ns0:MinMax>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:Calculation">
																		
																		<ns0:Calculation>
																			<xsl:for-each select="@UnitCharge">
																				
																				<xsl:attribute name="UnitCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="@UnitName">
																				
																				<xsl:attribute name="UnitName" namespace="">
																					<xsl:value-of select="."/>
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
																</ns0:Fee>
															</xsl:for-each>
														</ns0:Fees>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Reference">
														
														<ns0:Reference>
															<xsl:attribute name="Type" namespace="">
																<xsl:value-of select="@Type"/>
															</xsl:attribute>
															<xsl:attribute name="ID" namespace="">
																<xsl:value-of select="@ID"/>
															</xsl:attribute>
															<xsl:for-each select="@URL">
																
																<xsl:attribute name="URL" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="@Instance">
																
																<xsl:attribute name="Instance" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="@ID_Context">
																
																<xsl:attribute name="ID_Context" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="@DateTime">
																
																<xsl:attribute name="DateTime" namespace="">
																	<xsl:value-of select="."/>
																</xsl:attribute>
															</xsl:for-each>
															<xsl:for-each select="ns0:CompanyName">
																
																<ns0:CompanyName>
																	<xsl:copy-of select="@node()"/>
																	<xsl:copy-of select="node()"/>
																</ns0:CompanyName>
															</xsl:for-each>
															<xsl:for-each select="ns0:TPA_Extensions">
																
																<ns0:TPA_Extensions>
																	<xsl:copy-of select="@node()"/>
																	<xsl:copy-of select="node()"/>
																</ns0:TPA_Extensions>
															</xsl:for-each>
														</ns0:Reference>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Vendor">
														
														<ns0:Vendor>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</ns0:Vendor>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:VendorLocation">
														
														<ns0:VendorLocation>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</ns0:VendorLocation>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:DropOffLocation">
														
														<ns0:DropOffLocation>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</ns0:DropOffLocation>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Discount">
														
														<ns0:Discount>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</ns0:Discount>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:TPA_Extensions">
														
														<ns0:TPA_Extensions>
															<xsl:for-each select="ns0:ExtendedVehicle">
																
																<ns0:ExtendedVehicle>
																	<xsl:for-each select="@KeylessAccess">
																		
																		<xsl:attribute name="KeylessAccess" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																</ns0:ExtendedVehicle>
															</xsl:for-each>
														</ns0:TPA_Extensions>
													</xsl:for-each>
												</ns0:VehAvailCore>
												<xsl:for-each select="ns0:VehAvailInfo">
													
													<ns0:VehAvailInfo>
														<xsl:for-each select="@ChargeablePeriod">
															
															<xsl:attribute name="ChargeablePeriod" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each>
														<xsl:for-each select="ns0:PricedCoverages">
															
															<ns0:PricedCoverages>
																<xsl:for-each select="ns0:PricedCoverage">
																	
																	<ns0:PricedCoverage>
																		<xsl:for-each select="@Required">
																			
																			<xsl:attribute name="Required" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<ns0:Coverage>
																			<xsl:attribute name="CoverageType" namespace="">
																				<xsl:value-of select="ns0:Coverage/@CoverageType"/>
																			</xsl:attribute>
																			<xsl:for-each select="ns0:Coverage/@Code">
																				
																				<xsl:attribute name="Code" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Coverage/ns0:Details">
																				
																				<ns0:Details>
																					<xsl:attribute name="CoverageTextType" namespace="">
																						<xsl:value-of select="@CoverageTextType"/>
																					</xsl:attribute>
																					<xsl:for-each select="@Formatted">
																						
																						<xsl:attribute name="Formatted" namespace="">
																							<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@Language">
																						
																						<xsl:attribute name="Language" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@TextFormat">
																						
																						<xsl:attribute name="TextFormat" namespace="">
																							<xsl:value-of select="."/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:value-of select="."/>
																				</ns0:Details>
																			</xsl:for-each>
																		</ns0:Coverage>
																		<ns0:Charge>
																			<xsl:for-each select="ns0:Charge/@CurrencyCode">
																				
																				<xsl:attribute name="CurrencyCode" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@DecimalPlaces">
																				
																				<xsl:attribute name="DecimalPlaces" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@Amount">
																				
																				<xsl:attribute name="Amount" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@TaxInclusive">
																				
																				<xsl:attribute name="TaxInclusive" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@Description">
																				
																				<xsl:attribute name="Description" namespace="">
																					<xsl:value-of select="substring(., 0, 62)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@GuaranteedInd">
																				
																				<xsl:attribute name="GuaranteedInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@IncludedInRate">
																				
																				<xsl:attribute name="IncludedInRate" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@IncludedInEstTotalInd">
																				
																				<xsl:attribute name="IncludedInEstTotalInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/@RateConvertInd">
																				
																				<xsl:attribute name="RateConvertInd" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/ns0:TaxAmounts">
																				
																				<ns0:TaxAmounts>
																					<xsl:for-each select="ns0:TaxAmount">
																						
																						<ns0:TaxAmount>
																							<xsl:attribute name="Total" namespace="">
																								<xsl:value-of select="number(@Total)"/>
																							</xsl:attribute>
																							<xsl:attribute name="CurrencyCode" namespace="">
																								<xsl:value-of select="@CurrencyCode"/>
																							</xsl:attribute>
																							<xsl:for-each select="@TaxCode">
																								
																								<xsl:attribute name="TaxCode" namespace="">
																									<xsl:value-of select="."/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:for-each select="@Percentage">
																								
																								<xsl:attribute name="Percentage" namespace="">
																									<xsl:value-of select="number(.)"/>
																								</xsl:attribute>
																							</xsl:for-each>
																							<xsl:for-each select="@Description">
																								
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
																					<xsl:for-each select="@MaxCharge">
																						
																						<xsl:attribute name="MaxCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@MinCharge">
																						
																						<xsl:attribute name="MinCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@MaxChargeDays">
																						
																						<xsl:attribute name="MaxChargeDays" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																				</ns0:MinMax>
																			</xsl:for-each>
																			<xsl:for-each select="ns0:Charge/ns0:Calculation">
																				
																				<ns0:Calculation>
																					<xsl:for-each select="@UnitCharge">
																						
																						<xsl:attribute name="UnitCharge" namespace="">
																							<xsl:value-of select="number(.)"/>
																						</xsl:attribute>
																					</xsl:for-each>
																					<xsl:for-each select="@UnitName">
																						
																						<xsl:attribute name="UnitName" namespace="">
																							<xsl:value-of select="."/>
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
																		<xsl:value-of select="."/>
																	</ns0:PaymentRule>
																</xsl:for-each>
															</ns0:PaymentRules>
														</xsl:for-each>
													</ns0:VehAvailInfo>
												</xsl:for-each>
												<xsl:for-each select="ns0:AdvanceBooking">
													
													<ns0:AdvanceBooking>
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
														<xsl:for-each select="@RulesApplyInd">
															
															<xsl:attribute name="RulesApplyInd" namespace="">
																<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
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
	</xsl:template></xsl:stylesheet>
