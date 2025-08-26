from lxml import etree

def _has_duplicate_closing_tags(content: str, tag_name: str) -> bool:
    """Check if a closing tag appears multiple times in the content."""
    closing_tag = f'</{tag_name}>'
    return content.count(closing_tag) > 1

def _remove_first_complete_tag_block(content: str, tag_name: str) -> str:
    """Remove the first complete tag block (opening + content + closing) and its wrapper."""
    import re
    
    print(f"Removing first complete {tag_name} block")
    
    # Find the first opening tag
    opening_pattern = f'<{tag_name}[^>]*>'
    closing_pattern = f'</{tag_name}>'
    
    lines = content.split('\n')
    
    # Find the first opening tag line
    opening_line = -1
    closing_line = -1
    
    for i, line in enumerate(lines):
        if re.search(opening_pattern, line) and opening_line == -1:
            opening_line = i
            print(f"Found first opening {tag_name} at line {i + 1}: {line.strip()[:100]}")
        elif closing_pattern in line and opening_line >= 0 and closing_line == -1:
            closing_line = i
            print(f"Found first closing {tag_name} at line {i + 1}: {line.strip()[:100]}")
            break
    
    if opening_line >= 0 and closing_line >= 0:
        # Look for wrapper for-each that might contain this block
        wrapper_start = opening_line
        
        # Check if there's a for-each immediately before the opening tag
        for i in range(opening_line - 1, max(opening_line - 5, -1), -1):
            if '<xsl:for-each' in lines[i]:
                wrapper_start = i
                print(f"Found wrapper for-each at line {i + 1}: {lines[i].strip()[:100]}")
                break
            elif lines[i].strip() == '':
                continue  # Skip empty lines
            else:
                break  # Stop if we find non-empty, non-for-each line
        
        # Look for the closing for-each after the closing tag
        wrapper_end = closing_line
        if wrapper_start < opening_line:  # We found a wrapper
            for i in range(closing_line + 1, min(closing_line + 5, len(lines))):
                if '</xsl:for-each>' in lines[i]:
                    wrapper_end = i
                    print(f"Found wrapper closing for-each at line {i + 1}: {lines[i].strip()[:100]}")
                    break
                elif lines[i].strip() == '':
                    continue  # Skip empty lines
                else:
                    break
        
        # Remove the block from wrapper_start to wrapper_end (inclusive)
        print(f"Removing lines {wrapper_start + 1} to {wrapper_end + 1}")
        
        # Show what we're removing
        removed_lines = lines[wrapper_start:wrapper_end + 1]
        print(f"Removing {len(removed_lines)} lines:")
        for i, line in enumerate(removed_lines[:3]):
            print(f"  - {line.strip()[:100]}")
        if len(removed_lines) > 3:
            print(f"  ... and {len(removed_lines) - 3} more lines")
        
        # Create result without the removed block
        result_lines = lines[:wrapper_start] + lines[wrapper_end + 1:]
        result_content = '\n'.join(result_lines)
        
        # Check if we still have orphaned closing tags and add opening tags
        result_content = _add_missing_opening_tags(result_content, tag_name)
        
        return result_content
    else:
        print(f"Could not find complete {tag_name} block, using fallback")
        return content

def _add_missing_opening_tags(content: str, tag_name: str) -> str:
    """Add missing opening tags for orphaned closing tags."""
    import re
    
    lines = content.split('\n')
    opening_pattern = f'<{tag_name}[^>]*>'
    closing_pattern = f'</{tag_name}>'
    
    # Count opening and closing tags
    opening_count = len(re.findall(opening_pattern, content))
    closing_count = content.count(closing_pattern)
    
    print(f"Tag balance check for {tag_name}: {opening_count} opening, {closing_count} closing")
    
    if closing_count > opening_count:
        # We have orphaned closing tags - need to add opening tags
        orphaned_closers = closing_count - opening_count
        print(f"Adding {orphaned_closers} missing opening tags for {tag_name}")
        
        # Find lines with orphaned closing tags
        for i, line in enumerate(lines):
            if closing_pattern in line:
                # Check if this closing tag has a matching opener
                content_before = '\n'.join(lines[:i+1])
                opens_before = len(re.findall(opening_pattern, content_before))
                closes_before = content_before.count(closing_pattern)
                
                if closes_before > opens_before:
                    # This is an orphaned closing tag - add opening tag before it
                    # Find appropriate indentation
                    indent = len(line) - len(line.lstrip())
                    opening_tag = f'{" " * indent}<{tag_name}>'
                    
                    # Insert opening tag before the current line
                    lines.insert(i, opening_tag)
                    print(f"Added opening tag before line {i + 1}: {opening_tag}")
                    break  # Only fix one at a time to maintain proper structure
    
    return '\n'.join(lines)

# Test the specific pattern from the user
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
        <xsl:for-each select="@*[name() = 'MinCharge' or name() = 'MaxChargeDays']">
            <xsl:attribute name="{name()}">
                <xsl:value-of select="number(.)"/>
            </xsl:attribute>
        </xsl:for-each>
    </MinMax>
    </SomeParent>
</xsl:template>'''

print("=== Testing Duplicate Closing Tag Removal ===\n")
print("Original XML:")
print(test_xml)
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