from lxml import etree

# Read XSLT content from debug_xslt_fragment.xml file
def read_debug_xslt():
    try:
        with open("debug_xslt_fragment.xml", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("❌ Error: debug_xslt_fragment.xml file not found!")
        return None
    except Exception as e:
        print(f"❌ Error reading debug_xslt_fragment.xml: {e}")
        return None

print("=== Reading XSLT from debug_xslt_fragment.xml ===")
xslt_string = read_debug_xslt()

if xslt_string is None:
    print("❌ Could not read XSLT content. Exiting.")
    exit(1)

print(f"✅ Successfully loaded XSLT content ({len(xslt_string)} characters)")

print()

try:
    parser = etree.XMLParser(recover=False)  # Don't try to recover
    xslt_tree = etree.XML(xslt_string.encode(), parser)
    xslt = etree.XSLT(xslt_tree)

except etree.XMLSyntaxError as e:
    print("❌ XML Syntax Error(s):")
    for error in e.error_log:
        print(f"Line {error.line}: {error.message}")

except etree.XSLTParseError as e:
    print("❌ XSLT Parse Error:")
    print(str(e))  # Only the first one