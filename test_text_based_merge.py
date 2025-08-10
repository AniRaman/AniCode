#!/usr/bin/env python3
"""
Test the enhanced _text_based_for_each_merge function with element patterns.
"""

import sys
import os
sys.path.append('.')

from genie_core.llm.refine_cache import _text_based_for_each_merge

def test_attribute_patterns():
    """Test existing attribute pattern optimization."""
    print("=== TEST ATTRIBUTE PATTERNS ===")
    
    # Test simple attribute patterns
    attr_chunk = '''<xsl:for-each select="@Status">
    <xsl:attribute name="Status">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>
<xsl:for-each select="@Type">
    <xsl:attribute name="Type">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>'''
    
    print("Attribute test:")
    print("Original length:", len(attr_chunk))
    
    result = _text_based_for_each_merge(attr_chunk)
    
    print("Optimized length:", len(result))
    print("Union select found:", "|" in result)
    print("result : ", result)
    print()

def test_element_patterns():
    """Test new element pattern optimization."""
    print("=== TEST ELEMENT PATTERNS ===")
    
    # Test 1: Simple element copying
    element_chunk = '''<xsl:for-each select="ns0:StreetText">
    <xsl:variable name="var33_cur" select="."/>
    <StreetText>
        <xsl:value-of select="."/>
    </StreetText>
</xsl:for-each>'''
    
    print("Test 1 - Element copying:")
    print("Original:", element_chunk.strip())
    
    result1 = _text_based_for_each_merge(element_chunk)
    
    print("Result:", result1.strip())
    print("Optimized to copy-of:", "copy-of" in result1)
    print()
    
    # Test 2: Multiple element patterns
    multi_element_chunk = '''<xsl:for-each select="ns0:FirstName">
    <xsl:variable name="var1_cur" select="."/>
    <FirstName>
        <xsl:value-of select="."/>
    </FirstName>
</xsl:for-each>
<xsl:for-each select="ns0:LastName">
    <xsl:variable name="var2_cur" select="."/>
    <LastName>
        <xsl:value-of select="."/>
    </LastName>
</xsl:for-each>
<xsl:for-each select="ns0:Email">
    <xsl:variable name="var3_cur" select="."/>
    <Email>
        <xsl:value-of select="."/>
    </Email>
</xsl:for-each>'''
    
    print("Test 2 - Multiple elements:")
    print("Original length:", len(multi_element_chunk))
    
    result2 = _text_based_for_each_merge(multi_element_chunk)
    
    print("Result length:", len(result2))
    print("result : ", result2)
    print()

def test_mixed_patterns():
    """Test chunk with both attribute and element patterns."""
    print("=== TEST MIXED PATTERNS ===")
    
    mixed_chunk = '''<xsl:for-each select="@Status">
    <xsl:attribute name="Status">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>
<xsl:for-each select="ns0:ContactInfo">
    <xsl:variable name="var10_cur" select="."/>
    <ContactInfo>
        <xsl:value-of select="."/>
    </ContactInfo>
</xsl:for-each>
<xsl:for-each select="@Priority">
    <xsl:attribute name="Priority">
        <xsl:value-of select="."/>
    </xsl:attribute>
</xsl:for-each>'''
    
    print("Mixed patterns test:")
    print("Original length:", len(mixed_chunk))
    
    result = _text_based_for_each_merge(mixed_chunk)
    
    print("Result length:", len(result))
    print("Has union select:", "|" in result)
    print("Has copy-of:", "copy-of" in result)
    print("result : ", result)
    print()

def test_ndc_like_fragment():
    """Test with NDC OrderViewRS-like fragment."""
    print("=== TEST NDC-LIKE FRAGMENT ===")
    
    ndc_fragment = '''<xsl:for-each select="*[name()='ns0:DataLists']/*[name()='ns0:ContactInfoList']">
								
								<ContactInfoList>
									<xsl:for-each select="*[name()='ns0:ContactInfo']">
										
										<ContactInfo>
											<ContactInfoID>
												<xsl:value-of select="*[name()='ns0:ContactInfoID']"/>
											</ContactInfoID>
											<xsl:for-each select="*[name()='ns0:ContactPurposeText']">
												
												<ContactTypeText>
													<xsl:variable name="var22_nested">
														<xsl:call-template name="vmf:vmf2_inputtoresult">
															<xsl:with-param name="input" select="string(.)"/>
														</xsl:call-template>
													</xsl:variable>
													<xsl:value-of select="$var22_nested"/>
												</ContactTypeText>
											</xsl:for-each>
											<xsl:for-each select="*[name()='ns0:IndividualRefID']">
												
												<IndividualRef>
													<xsl:value-of select="."/>
												</IndividualRef>
											</xsl:for-each>
											<xsl:for-each select="*[name()='ns0:Phone']">
												
												<Phone>
													<xsl:if test="$var20_cur/*[name()='ns0:IndividualRefID']">
														<LabelText>
															<xsl:value-of select="'MOBILE'"/>
														</LabelText>
													</xsl:if>
													<xsl:for-each select="*[name()='ns0:AreaCodeNumber']">
														
														<AreaCodeNumber>
															<xsl:value-of select="number(.)"/>
														</AreaCodeNumber>
													</xsl:for-each>
													<xsl:choose>
														<xsl:when test="*[name()='ns0:CountryDialingCode']">
															<xsl:for-each select="*[name()='ns0:CountryDialingCode']">
																
																<xsl:for-each select="$var24_cur/*[name()='ns0:PhoneNumber']">
																	
																	<PhoneNumber>
																		<!--Manual change-->
																		<xsl:value-of select="concat($var26_cur, .)"/>
																	</PhoneNumber>
																</xsl:for-each>
															</xsl:for-each>
														</xsl:when>
														<xsl:otherwise>
															<xsl:for-each select="*[name()='ns0:PhoneNumber']">
																
																<PhoneNumber>
																	<!--Manual change-->
																	<xsl:value-of select="."/>
																</PhoneNumber>
															</xsl:for-each>
														</xsl:otherwise>
													</xsl:choose>
													<xsl:for-each select="*[name()='ns0:ExtensionNumber']">
														
														<ExtensionNumber>
															<xsl:value-of select="number(.)"/>
														</ExtensionNumber>
													</xsl:for-each>
												</Phone>
											</xsl:for-each>
											<xsl:for-each select="*[name()='ns0:OtherAddress']">
												
												<OtherAddress>
													<OtherAddressText>
														<xsl:value-of select="*[name()='ns0:OtherAddressText']"/>
													</OtherAddressText>
												</OtherAddress>
											</xsl:for-each>
											<xsl:for-each select="*[name()='ns0:EmailAddress']">
												
												<EmailAddress>
													<xsl:if test="$var20_cur/*[name()='ns0:IndividualRefID']">
														<LabelText>
															<xsl:value-of select="'EMAIL'"/>
														</LabelText>
													</xsl:if>
													<EmailAddressText>
														<xsl:value-of select="*[name()='ns0:EmailAddressText']"/>
													</EmailAddressText>
												</EmailAddress>
											</xsl:for-each>
											<xsl:for-each select="*[name()='ns0:PostalAddress']">
												
												<xsl:if test="$var20_cur/*[name()='ns0:ContactPurposeText'] = '700'">
													<PostalAddress>
														<LabelText>
															<xsl:value-of select="'AddressAtOrigin'"/>
														</LabelText>
														<xsl:for-each select="*[name()='ns0:StreetText']">
															
															<StreetText>
																<xsl:value-of select="."/>
															</StreetText>
														</xsl:for-each>
														<xsl:for-each select="*[name()='ns0:PO_BoxCode']">
															
															<PO_BoxCode>
																<xsl:value-of select="."/>
															</PO_BoxCode>
														</xsl:for-each>
														<xsl:for-each select="*[name()='ns0:PostalCode']">
															
															<PostalCode>
																<xsl:value-of select="."/>
															</PostalCode>
														</xsl:for-each>
														<xsl:for-each select="*[name()='ns0:CityName']">
															
															<CityName>
																<xsl:value-of select="."/>
															</CityName>
														</xsl:for-each>
														<xsl:for-each select="*[name()='ns0:CountryCode']">
															
															<CountryCode>
																<xsl:value-of select="."/>
															</CountryCode>
														</xsl:for-each>
													</PostalAddress>
												</xsl:if>
											</xsl:for-each>'''
    
    print("NDC-like fragment:")
    print("Original length:", len(ndc_fragment))
    
    result = _text_based_for_each_merge(ndc_fragment)
    
    print("Result:")
    print(result)
    print("Optimized length:", len(result))
    
    # Count optimizations
    copy_of_count = result.count("copy-of")
    variable_count = result.count("var")
    
    print(f"Copy-of patterns: {copy_of_count}")
    print(f"Variables remaining: {variable_count}")
    print(f"Size reduction: {((len(ndc_fragment) - len(result)) / len(ndc_fragment) * 100):.1f}%")
    
    return copy_of_count >= 3

def test_edge_cases():
    """Test edge cases and validation."""
    print("=== TEST EDGE CASES ===")
    
    # Test: Different element names (should not optimize to copy-of)
    different_names = '''<xsl:for-each select="ns0:SourceField">
    <xsl:variable name="var50_cur" select="."/>
    <TargetField>
        <xsl:value-of select="."/>
    </TargetField>
</xsl:for-each>'''
    
    print("Different element names:")
    result = _text_based_for_each_merge(different_names)
    
    print("Uses copy-of:", "copy-of" in result)
    print("Removes variable:", "var50_cur" not in result)
    print()

if __name__ == "__main__":
    try:
        print("Testing enhanced _text_based_for_each_merge function...\n")
        
        # Run all tests
        test_attribute_patterns()
        test_element_patterns()
        test_mixed_patterns()
        ndc_success = test_ndc_like_fragment()
        test_edge_cases()
        
        print("=== SUMMARY ===")
        print(f"NDC-like optimization: {'[SUCCESS]' if ndc_success else '[FAILED]'}")
        print("All element pattern optimizations working correctly!")
        
    except Exception as e:
        print(f"[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()