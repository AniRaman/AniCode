#!/usr/bin/env python3
"""Debug why placeholders aren't being created."""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('.'))

def test_debug_placeholders():
    """Debug the placeholder creation."""
    print("=== Debugging Placeholder Creation ===")
    
    from genie_core.llm.intelligent_chunk_processor import IntelligentChunkProcessor
    
    def mock_llm_function(chunk_text):
        return chunk_text + "\n<!-- LLM Processed -->"
    
    processor = IntelligentChunkProcessor()
    
    # Test template that should trigger multiple rules
    test_template = '''				<xsl:for-each select="ns0:Success">
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
                                <xsl:for-each select="@Codedf">
									<xsl:variable name="var81_cur" select="."/>
									<xsl:attribute name="Codedf" namespace="">
										<xsl:value-of select="."/>
									</xsl:attribute>
								</xsl:for-each>
								<xsl:for-each select="@DocURLdf">
									<xsl:variable name="var91_cur" select="."/>
									<xsl:attribute name="DocURLdf" namespace="">
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
							</Warning>'''
    
    #print(f"Original template length: {len(test_template)}")

    test_template_2 = '''	<xsl:template name="tbf:tbf6_VehicleChargeType">
		<xsl:param name="input" select="/.."/>
		<xsl:for-each select="$input/@CurrencyCode">
			<xsl:variable name="var1_current" select="."/>
			<xsl:attribute name="CurrencyCode">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@DecimalPlaces">
			<xsl:variable name="var2_current" select="."/>
			<xsl:attribute name="DecimalPlaces">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@Amount">
			<xsl:variable name="var3_current" select="."/>
			<xsl:attribute name="Amount">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@TaxInclusive">
			<xsl:variable name="var4_current" select="."/>
			<xsl:attribute name="TaxInclusive">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@Description">
			<xsl:variable name="var5_current" select="."/>
			<xsl:attribute name="Description">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@GuaranteedInd">
			<xsl:variable name="var6_current" select="."/>
			<xsl:attribute name="GuaranteedInd">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@IncludedInRate">
			<xsl:variable name="var7_current" select="."/>
			<xsl:attribute name="IncludedInRate">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@IncludedInEstTotalInd">
			<xsl:variable name="var8_current" select="."/>
			<xsl:attribute name="IncludedInEstTotalInd">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/@RateConvertInd">
			<xsl:variable name="var9_current" select="."/>
			<xsl:attribute name="RateConvertInd">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</xsl:for-each>
		<xsl:for-each select="$input/node()">
			<xsl:variable name="var10_current" select="."/>
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
	</xsl:template>'''
    
    try:
        result = processor.process_chunk_intelligently(test_template_2, mock_llm_function)
        print(f"Final result length: {len(result)}")
        
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_debug_placeholders()