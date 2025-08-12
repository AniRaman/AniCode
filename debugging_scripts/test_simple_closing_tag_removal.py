from lxml import etree

def _has_duplicate_closing_tags(content: str, tag_name: str) -> bool:
    """Check if a closing tag appears multiple times in the content."""
    closing_tag = f'</{tag_name}>'
    return content.count(closing_tag) > 1

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

# Test with your complex example
test_xml = '''<xsl:template xmlns:xsl="http://www.w3.org/1999/XSL/Transform" match="/">
    <SomeParent>
        <xsl:for-each select="ns0:MinMax">
            <MinMax>
                <xsl:for-each select="@*">
                    <xsl:if test="name() = 'MaxCharge'">
                        <xsl:attribute name="MaxCharge">
                            <xsl:value-of select="number(.)"/>
                        </xsl:attribute>
                    </xsl:if>
                </xsl:for-each>
            </MinMax>
        </xsl:for-each>
        </xsl:for-each>
      </Fee>
    </xsl:for-each>
  </Fees>
</xsl:for-each>
<xsl:for-each select="@*[name() = 'MinCharge' or name() = 'MaxChargeDays']">
    <xsl:attribute name="{name()}">
        <xsl:value-of select="number(.)"/>
    </xsl:attribute>
</xsl:for-each>
    </MinMax>
    </SomeParent>
</xsl:template>'''

print("=== Testing Simple Closing Tag Removal ===\n")
print("Original XML (first 500 chars):")
print(test_xml[:500] + "...")
print("\n" + "="*60 + "\n")

# Check if MinMax has duplicate closing tags
if _has_duplicate_closing_tags(test_xml, 'MinMax'):
    print("Detected duplicate MinMax closing tags")
    fixed_xml = _remove_first_complete_tag_block(test_xml, 'MinMax')
    print("\n" + "="*60 + "\n")
    print("Fixed XML:")
    print(fixed_xml)
    
    # Test if the fixed XML parses correctly
    try:
        etree.fromstring(fixed_xml.encode())
        print("\n[SUCCESS] Fixed XML parses correctly!")
    except Exception as e:
        print(f"\n[ERROR] Fixed XML still has issues: {e}")
else:
    print("No duplicate MinMax closing tags found")