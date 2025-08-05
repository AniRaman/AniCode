# Online Python compiler (interpreter) to run Python online.
# Write Python 3 code in this online editor and run it.
from lxml import etree

chunk_org = '''<xsl:output method="xml" encoding="UTF-8" indent="yes"/>
	<xsl:template match="/"><xsl:variable name="var1_initial" select="."/>
		<OTA_VehAvailRateRS xmlns="http://www.opentravel.org/OTA/2003/05">
			<xsl:for-each select="ns0:OTA_VehAvailRateRS">
				<xsl:variable name="var2_cur" select="."/>
				<xsl:for-each select="ns0:Success">
					<xsl:variable name="var3_cur" select="."/>
					<Success/>
				</xsl:for-each>
				<xsl:for-each select="ns0:Warnings">
					<xsl:variable name="var4_cur" select="."/>
					<Warnings>
						<xsl:for-each select="ns0:Warning">
							<xsl:variable name="var5_cur" select="."/>
							<Warning>
								<xsl:attribute name="Type" namespace="">
									<xsl:value-of select="@Type"/>
								</xsl:attribute>
								<xsl:for-each select="@Language">
									<xsl:variable name="var6_cur" select="."/>
									<xsl:attribute name="Language" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@ShortText">
									<xsl:variable name="var7_cur" select="."/>
									<xsl:attribute name="ShortText" namespace="">
										<xsl:value-of select="substring(., '0', '62')"/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@Code">
									<xsl:variable name="var8_cur" select="."/>
									<xsl:attribute name="Code" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@DocURL">
									<xsl:variable name="var9_cur" select="."/>
									<xsl:attribute name="DocURL" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@Status">
									<xsl:variable name="var10_cur" select="."/>
									<xsl:attribute name="Status" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@Tag">
									<xsl:variable name="var11_cur" select="."/>
									<xsl:attribute name="Tag" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@RecordID">
									<xsl:variable name="var12_cur" select="."/>
									<xsl:attribute name="RecordID" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@RPH">
									<xsl:variable name="var13_cur" select="."/>
									<xsl:attribute name="RPH" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:value-of select="."/>
							</Warning>
						</xsl:for-each>
					</Warnings>
				</xsl:for-each>
				<xsl:for-each select="ns0:VehAvailRSCore">
					<xsl:variable name="var14_cur" select="."/>
					<VehAvailRSCore>
						<VehRentalCore>
							<xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime">
								<xsl:variable name="var15_cur" select="."/>
								<xsl:attribute name="PickUpDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@ReturnDateTime">
								<xsl:variable name="var16_cur" select="."/>
								<xsl:attribute name="ReturnDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@StartChargesDateTime">
								<xsl:variable name="var17_cur" select="."/>
								<xsl:attribute name="StartChargesDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@StopChargesDateTime">
								<xsl:variable name="var18_cur" select="."/>
								<xsl:attribute name="StopChargesDateTime" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@OneWayIndicator">
								<xsl:variable name="var19_cur" select="."/>
								<xsl:attribute name="OneWayIndicator" namespace="">
									<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@MultiIslandRentalDays">
								<xsl:variable name="var20_cur" select="."/>
								<xsl:attribute name="MultiIslandRentalDays" namespace="">
									<xsl:value-of select="number(.)"/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@Quantity">
								<xsl:variable name="var21_cur" select="."/>
								<xsl:attribute name="Quantity" namespace="">
									<xsl:value-of select="number(.)"/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/@DistUnitName">
								<xsl:variable name="var22_cur" select="."/>
								<xsl:attribute name="DistUnitName" namespace="">
									<xsl:value-of select="."/>
								</xsl:attribute>
							</xsl:for-each>
							<xsl:for-each select="ns0:VehRentalCore/ns0:PickUpLocation">
								<xsl:variable name="var23_cur" select="."/>
								<PickUpLocation>
									<xsl:if test="@LocationCode">
										<xsl:attribute name="CodeContext" namespace="">IATA</xsl:attribute>
									</xsl:if>
									<xsl:for-each select="@LocationCode">
										<xsl:variable name="var24_cur" select="."/>
										<xsl:attribute name="LocationCode" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:for-each select="@ExtendedLocationCode">
										<xsl:variable name="var25_cur" select="."/>
										<xsl:attribute name="ExtendedLocationCode" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:for-each select="@CounterLocation">
										<xsl:variable name="var26_cur" select="."/>
										<xsl:attribute name="CounterLocation" namespace="">
											<xsl:value-of select="."/>
										</xsl:attribute>
									</xsl:for-each>
									<xsl:value-of select="."/>
								</PickUpLocation>								</xsl:for-each>  '''


print("Original chunk of Org chunk: " + str(len(chunk_org)))  # Original length
cleaned_chunk_org = "\n".join(line.strip() for line in chunk_org.splitlines() if line.strip())
print("Cleaned chunk of Org chunk: " + str(len(cleaned_chunk_org)))


chunk = '''<xsl:template xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
        xmlns:tbf="http://www.altova.com/MapForce/UDF/tbf"
        xmlns:ns0="http://www.opentravel.org/OTA/2003/05"
        xmlns:xs="http://www.w3.org/2001/XMLSchema" match="/">
        <OTA_VehAvailRateRS xmlns="http://www.opentravel.org/OTA/2003/05">
                <xsl:for-each select="ns0:OTA_VehAvailRateRS">
                        <xsl:for-each select="ns0:Success">
                                <Success/>
                        </xsl:for-each>
                        <xsl:for-each select="ns0:Warnings">
                                <Warnings>
                                        <xsl:for-each select="ns0:Warning">
                                                <Warning>
                                                        <xsl:attribute name="Type">
                                                                <xsl:value-of select="@Type"/>
                                                        </xsl:attribute>
                                                        <xsl:for-each select="@Language">
                                                                <xsl:attribute name="Language">
                                                                        <xsl:value-of select="."/>
                                                                </xsl:attribute>
                                                        </xsl:for-each>
                                                        <xsl:for-each select="@ShortText">
                                                                <xsl:attribute name="ShortText">
                                                                        <xsl:value-of select="substring(., '0', '62')"/>
                                                                </xsl:attribute>
                                                        </xsl:for-each>
                                                        <xsl:for-each select="@Code | @DocURL | @Status | @Tag | @RecordID | @RPH">
                                                                <xsl:attribute name="{name()}" namespace="">
                                                                        <xsl:value-of select="."/>
                                                                </xsl:attribute>
                                                        </xsl:for-each>
                                                        <xsl:value-of select="."/>
                                                </Warning>
                                        </xsl:for-each>
                                </Warnings>
                        </xsl:for-each>
                        <xsl:for-each select="ns0:VehAvailRSCore">
                                <VehAvailRSCore>
                                        <VehRentalCore>
                                                <xsl:for-each select="ns0:VehRentalCore/@PickUpDateTime | ns0:VehRentalCore/@ReturnDateTime | ns0:VehRentalCore/@StartChargesDateTime | ns0:VehRentalCore/@StopChargesDateTime">
                                                        <xsl:attribute name="{name()}" namespace="">
                                                                <xsl:value-of select="."/>
                                                        </xsl:attribute>
                                                </xsl:for-each>
                                                <xsl:for-each select="ns0:VehRentalCore/@OneWayIndicator">
                                                        <xsl:attribute name="OneWayIndicator">
                                                                <xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
                                                        </xsl:attribute>
                                                </xsl:for-each>
                                                <xsl:for-each select="ns0:VehRentalCore/@MultiIslandRentalDays | ns0:VehRentalCore/@Quantity">
                                                        <xsl:attribute name="{name()}" namespace="">
                                                                <xsl:value-of select="number(.)"/>
                                                        </xsl:attribute>
                                                </xsl:for-each>
                                                <xsl:for-each select="ns0:VehRentalCore/@DistUnitName">
                                                        <xsl:attribute name="DistUnitName">
                                                                <xsl:value-of select="."/>
                                                        </xsl:attribute>
                                                </xsl:for-each>
                                                <xsl:for-each select="ns0:VehRentalCore/ns0:PickUpLocation">
                                                        <PickUpLocation>
                                                                <xsl:if test="@LocationCode">
                                                                        <xsl:attribute name="CodeContext">IATA</xsl:attribute>
                                                                </xsl:if>
                                                                <xsl:for-each select="@LocationCode | @ExtendedLocationCode | @CounterLocation">
                                                                        <xsl:attribute name="{name()}" namespace="">
                                                                                <xsl:value-of select="."/>
                                                                        </xsl:attribute>
                                                                </xsl:for-each>
                                                                <xsl:value-of select="."/>
                                                        </PickUpLocation>
                                                </xsl:for-each>
                                        </VehRentalCore>
                                </VehAvailRSCore>
                        </xsl:for-each>
                </xsl:for-each>
        </OTA_VehAvailRateRS>
</xsl:template> '''

print("Original chunk of refined chunk: " + str(len(chunk)))  # Original length
cleaned_chunk = "\n".join(line.strip() for line in chunk.splitlines() if line.strip())
print("Cleaned chunk of refined chunk: " + str(len(cleaned_chunk)))



def _calculate_complexity_score(chunk_text: str) -> float:
    """Calculate complexity score based on XSLT constructs."""
    import re
    
    # Complex patterns (high score)
    complex_patterns = [
        (r'<xsl:choose>', 1.0),  # Complex conditionals
        (r'substring-before|substring-after|contains|translate', 0.8),  # String functions
        (r'<xsl:call-template', 0.7),  # Template calls
        (r'<xsl:for-each[^>]*>.*?<xsl:for-each', 0.6)  # Nested loops
    ]
    
    # Simple patterns (low score)
    simple_patterns = [
        (r'<xsl:copy-of', -0.3),  # Simple copying
        (r'<xsl:value-of', -0.2),  # Simple value extraction
        (r'<xsl:attribute[^>]*>[^<]*</xsl:attribute>', -0.1)  # Simple attributes
    ]
    
    score = 0.0
    total_length = len(chunk_text)
    
    if total_length == 0:
        return 0.0
    
    for pattern, weight in complex_patterns + simple_patterns:
        matches = re.findall(pattern, chunk_text, re.DOTALL)
        score += len(matches) * weight
    
    # Normalize by content length
    return max(0.0, min(1.0, score / max(1, total_length / 200)))

print("Complexity score of Org chunk: " + str(_calculate_complexity_score(chunk_org)))
print("Complexity score of refined chunk: " + str(_calculate_complexity_score(chunk)))






