
def _remove_first_complete_tag_block(content: str, tag_name: str) -> str:
    """Remove first duplicate closing tag and all closing tags until next opening tag."""
    import re
    
    print(f"Removing first duplicate closing tag {tag_name} and subsequent closing tags")
    
    lines = content.split('\n')
    closing_pattern = f'</{tag_name}>'
    
    # Find the first occurrence of the duplicate closing tag
    first_closing_line = -1
    for i, line in enumerate(lines):
        if closing_pattern in line:
            first_closing_line = i
            print(f"Found first closing {tag_name} at line {i + 1}: {line.strip()[:100]}")
            break
    
    if first_closing_line >= 0:
        # Starting from this closing tag, remove all closing tags until we find an opening tag
        lines_to_remove = []
        
        for i in range(first_closing_line, len(lines)):
            line = lines[i].strip()
            
            # Check if this line contains an opening tag (but not self-closing)
            if re.search(r'<[^/!][^>]*[^/]>', line) and not line.startswith('</'):
                print(f"Found opening tag at line {i + 1}, stopping removal: {line[:100]}")
                break
            
            # Check if this line contains a closing tag
            if re.search(r'</[^>]+>', line):
                lines_to_remove.append(i)
                print(f"Marking closing tag for removal at line {i + 1}: {line[:100]}")
        
        # Remove the marked lines (in reverse order to maintain indices)
        for line_idx in reversed(lines_to_remove):
            print(f"Removing line {line_idx + 1}: {lines[line_idx].strip()[:100]}")
            lines.pop(line_idx)
        
        print(f"Removed {len(lines_to_remove)} closing tag lines")
        return '\n'.join(lines)
    else:
        print(f"Could not find first closing {tag_name}")
        return content

def _extract_structural_tag_names(content: str) -> list:
    """Extract non-XSL tag names in order (opening and closing)."""
    import re
    tag_list = []
    
    # Find all tags that don't start with xsl:
    for match in re.finditer(r'<(/?(?!xsl:)\w+)[^>]*>', content):
        tag_name = match.group(1)
        if tag_name.startswith('/'):
            tag_list.append('/' + tag_name[1:])  # closing tag like "/TaxAmount"
        else:
            tag_list.append(tag_name)  # opening tag like "TaxAmount"
    
    return tag_list

def _validate_chunk_structure(input_chunk: str, refined_chunk: str) -> str:
    """Compare structural tags and fix discrepancies."""
    input_tags = _extract_structural_tag_names(input_chunk)
    output_tags = _extract_structural_tag_names(refined_chunk)
    
    print(f"Input tags: {input_tags}")
    print(f"Output tags: {output_tags}")
    
    if input_tags == output_tags:
        print("Tag lists match perfectly")
        return refined_chunk
    else:
        print("Tag lists differ - fixing discrepancies")
        return _fix_tag_discrepancies(refined_chunk, input_tags, output_tags)

def _fix_tag_discrepancies(refined_chunk: str, input_tags: list, output_tags: list) -> str:
    """Remove extra tags from refined chunk until it matches input structure."""
    current_content = refined_chunk
    
    # Find extra tags in output that aren't in input
    extra_tags = []
    for tag in output_tags:
        if tag not in input_tags:
            extra_tags.append(tag)
    
    print(f"Extra tags found in output: {extra_tags}")
    
    # Remove each extra tag
    for extra_tag in extra_tags:
        print(f"Removing extra tag: {extra_tag}")
        
        if extra_tag.startswith('/'):
            # It's a closing tag, extract the tag name
            tag_name = extra_tag[1:]  # Remove the '/'
        else:
            # It's an opening tag
            tag_name = extra_tag
        
        # Apply the removal logic
        current_content = _remove_first_complete_tag_block(current_content, tag_name)
    
    return current_content

# Test chunk validation functions
if __name__ == "__main__":
    print("=== Testing Chunk Validation Functions ===\n")
    
    # Test case 1: Matching tags
    input_chunk = '''<xsl:for-each select="ns0:VehAvailCore/ns0:DropOffLocation">
														
														<DropOffLocation>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</DropOffLocation>
													</xsl:for-each><xsl:for-each select="ns0:VehAvailCore/ns0:Discount">
														
														<Discount>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</Discount>
													</xsl:for-each><xsl:for-each select="ns0:VehAvailCore/ns0:TPA_Extensions">
														
														<TPA_Extensions>
															<xsl:for-each select="ns0:ExtendedVehicle">
																
																<ExtendedVehicle>
																	<xsl:for-each select="@KeylessAccess">
																		
																		<xsl:attribute name="KeylessAccess" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																</ExtendedVehicle>
															</xsl:for-each>
														</TPA_Extensions>
													</xsl:for-each>
												</VehAvailCore>
												<xsl:for-each select="ns0:VehAvailInfo">
													
													<VehAvailInfo>
														<xsl:for-each select="@ChargeablePeriod">
															
															<xsl:attribute name="ChargeablePeriod" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each><xsl:for-each select="ns0:PricedCoverages">
															
															<PricedCoverages>
																<xsl:for-each select="ns0:PricedCoverage">
																	
																	<PricedCoverage>
																		<xsl:for-each select="@Required">
																			
																			<xsl:attribute name="Required" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<Coverage>
																			<xsl:attribute name="CoverageType" namespace="">
																				<xsl:value-of select="ns0:Coverage/@CoverageType"/>
																			</xsl:attribute>
																			<xsl:for-each select="ns0:Coverage/@Code">
																				
																				<xsl:attribute name="Code" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="ns0:Coverage/ns0:Details">
																				
																				<Details>
																					<xsl:attribute name="CoverageTextType" namespace="">
																						<xsl:value-of select="@CoverageTextType"/>
																					</xsl:attribute>
																					<xsl:for-each select="@Formatted">
																						
																						<xsl:attribute name="Formatted" namespace="">
																							<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																						</xsl:attribute>
																					</xsl:for-each><simpletag1/><simpletag2/>
																					<xsl:value-of select="."/>
																				</Details>
																			</xsl:for-each>
																		</Coverage>
																		<Charge>
																			<xsl:for-each select="ns0:Charge/@CurrencyCode">
																				
																				<xsl:attribute name="CurrencyCode" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><simpletag3/><simpletag4/><xsl:for-each select="ns0:Charge/@TaxInclusive">
																				
																				<xsl:attribute name="TaxInclusive" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>'''

    refined_chunk = '''<xsl:for-each select="ns0:VehAvailCore/ns0:DropOffLocation">
														
														<DropOffLocation>
															<xsl:copy-of select="@*"/>
															<xsl:copy-of select="node()"/>
														</DropOffLocation>
													</xsl:for-each><xsl:for-each select="ns0:VehAvailCore/ns0:Discount">
														
														<Discount>
															<xsl:copy-of select="@*"/>
															<xsl:copy-of select="node()"/>
														</Discount>
													</xsl:for-each><xsl:for-each select="ns0:VehAvailCore/ns0:TPA_Extensions">
														
														<TPA_Extensions>
															<xsl:for-each select="ns0:ExtendedVehicle">
																
																<ExtendedVehicle>
																	<xsl:for-each select="@*[name()='KeylessAccess']">
																		
																		<xsl:attribute name="KeylessAccess" namespace="">
																			<xsl:value-of select="."/>
																		</xsl:attribute>
																	</xsl:for-each>
																</ExtendedVehicle>
															</xsl:for-each>
														</TPA_Extensions>
													</xsl:for-each>
												</VehAvailCore>
												<xsl:for-each select="ns0:VehAvailInfo">
													
													<VehAvailInfo>
														<xsl:for-each select="@*[name()='ChargeablePeriod']">
															
															<xsl:attribute name="ChargeablePeriod" namespace="">
																<xsl:value-of select="."/>
															</xsl:attribute>
														</xsl:for-each><xsl:for-each select="ns0:PricedCoverages">
															
															<PricedCoverages>
																<xsl:for-each select="ns0:PricedCoverage">
																	
																	<PricedCoverage>
																		<xsl:for-each select="@*[name()='Required']">
																			
																			<xsl:attribute name="Required" namespace="">
																				<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																			</xsl:attribute>
																		</xsl:for-each>
																		<Coverage>
																			<xsl:attribute name="CoverageType" namespace="">
																				<xsl:value-of select="ns0:Coverage/@*[name()='CoverageType']"/>
																			</xsl:attribute>
																			<xsl:for-each select="ns0:Coverage/@*[name()='Code']">
																				
																				<xsl:attribute name="Code" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="ns0:Coverage/ns0:Details">
																				
																				<Details>
																					<xsl:attribute name="CoverageTextType" namespace="">
																						<xsl:value-of select="@CoverageTextType"/>
																					</xsl:attribute>
																					<xsl:for-each select="@*[name()='Formatted']">
																						
																						<xsl:attribute name="Formatted" namespace="">
																							<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																						</xsl:attribute>
																					</xsl:for-each><simpletag1/><simpletag2/>
																					<xsl:value-of select="."/>
																				</Details>
																			</xsl:for-each>
																		</Coverage>
																		<Charge>
																			<xsl:for-each select="ns0:Charge/@*[name()='CurrencyCode']">
																				
																				<xsl:attribute name="CurrencyCode" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><simpletag3/><simpletag4/><xsl:for-each select="ns0:Charge/@*[name()='TaxInclusive']">
																				
																				<xsl:attribute name="TaxInclusive" namespace="">
																					<xsl:value-of select="boolean(translate(normalize-space(string(.)), ' 0false', ''))"/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</Charge>
																	</PricedCoverage>
																</xsl:for-each>
															</PricedCoverages>
														</xsl:for-each>
													</VehAvailInfo>
												</xsl:for-each>'''

    print("###################### Test 1: Matching tags ###########################")
    result1 = _validate_chunk_structure(input_chunk, refined_chunk)
    print("XML repaired : ", result1)
    print(f"Result length: {len(result1)}")
    
    # Test case 2: Extra tags in output
    input_chunk2 = '''<xsl:for-each select="@MinCharge">
																				
																				<xsl:attribute name="MinCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@MaxChargeDays">
																				
																				<xsl:attribute name="MaxChargeDays" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</MinMax>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:Calculation">
																		
																		<Calculation>
																			<xsl:for-each select="@UnitCharge">
																				
																				<xsl:attribute name="UnitCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@UnitName">
																				
																				<xsl:attribute name="UnitName" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Quantity">
																				
																				<xsl:attribute name="Quantity" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Percentage">
																				
																				<xsl:attribute name="Percentage" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Applicability">
																				
																				<xsl:attribute name="Applicability" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@MaxQuantity">
																				
																				<xsl:attribute name="MaxQuantity" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Total">
																				
																				<xsl:attribute name="Total" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</Calculation>
																	</xsl:for-each>
																</Fee>
															</xsl:for-each>
														</Fees>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Reference">
														
														<Reference>
															<xsl:attribute name="Type" namespace="">
																<xsl:value-of select="@Type"/>
															</xsl:attribute>
															<xsl:attribute name="ID" namespace="">
																<xsl:value-of select="@ID"/>
															</xsl:attribute>
															<simpletag1/><simpletag2/><simpletag3/><simpletag4/><xsl:for-each select="ns0:CompanyName">
																
																<CompanyName>
																	<xsl:copy-of select="@node()"/>
																	<xsl:copy-of select="node()"/>
																</CompanyName>
															</xsl:for-each><xsl:for-each select="ns0:TPA_Extensions">
																
																<TPA_Extensions>
																	<xsl:copy-of select="@node()"/>
																	<xsl:copy-of select="node()"/>
																</TPA_Extensions>
															</xsl:for-each>
														</Reference>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Vendor">
														
														<Vendor>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</Vendor>
													</xsl:for-each><xsl:for-each select="ns0:VehAvailCore/ns0:VendorLocation">
														
														<VendorLocation>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</VendorLocation>
													</xsl:for-each>'''

    refined_chunk2 = '''<xsl:for-each select="@MinCharge">
																				
																				<xsl:attribute name="MinCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@MaxChargeDays">
																				
																				<xsl:attribute name="MaxChargeDays" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</MinMax>
																	</xsl:for-each>
																	<xsl:for-each select="ns0:Calculation">
																		
																		<Calculation>
																			<xsl:for-each select="@UnitCharge">
																				
																				<xsl:attribute name="UnitCharge" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@UnitName">
																				
																				<xsl:attribute name="UnitName" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Quantity">
																				
																				<xsl:attribute name="Quantity" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Percentage">
																				
																				<xsl:attribute name="Percentage" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Applicability">
																				
																				<xsl:attribute name="Applicability" namespace="">
																					<xsl:value-of select="."/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@MaxQuantity">
																				
																				<xsl:attribute name="MaxQuantity" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each><xsl:for-each select="@Total">
																				
																				<xsl:attribute name="Total" namespace="">
																					<xsl:value-of select="number(.)"/>
																				</xsl:attribute>
																			</xsl:for-each>
																		</Calculation>
																	</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Reference">
														
														<Reference>
															<xsl:attribute name="Type" namespace="">
																<xsl:value-of select="@Type"/>
															</xsl:attribute>
															<xsl:attribute name="ID" namespace="">
																<xsl:value-of select="@ID"/>
															</xsl:attribute>
															<simpletag1/><simpletag2/><simpletag3/><simpletag4/><xsl:for-each select="ns0:CompanyName">
																
																<CompanyName>
																	<xsl:copy-of select="@node()"/>
																	<xsl:copy-of select="node()"/>
																</CompanyName>
															</xsl:for-each><xsl:for-each select="ns0:TPA_Extensions">
																
																<TPA_Extensions>
																	<xsl:copy-of select="@node()"/>
																	<xsl:copy-of select="node()"/>
																</TPA_Extensions>
															</xsl:for-each>
														</Reference>
													</xsl:for-each>
													<xsl:for-each select="ns0:VehAvailCore/ns0:Vendor">
														
														<Vendor>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</Vendor>
													</xsl:for-each><xsl:for-each select="ns0:VehAvailCore/ns0:VendorLocation">
														
														<VendorLocation>
															<xsl:copy-of select="@node()"/>
															<xsl:copy-of select="node()"/>
														</VendorLocation>
													</xsl:for-each>'''

    print("###################### Test 2: Extra tags in output ###########################")
    result2 = _validate_chunk_structure(input_chunk2, refined_chunk2)
    print("XML repaired : ", result2)
    print(f"Result length: {len(result2)}")
    print()
    