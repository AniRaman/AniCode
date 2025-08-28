"""
Test file processing functionality for agentic XSLT processor
"""

import os
import sys
import io
sys.path.append(os.path.abspath(os.getcwd()))

from genie_core.llm.agentic_xslt_processor import process_file_content

class MockUploadedFile:
    def __init__(self, name, content):
        self.name = name
        self.content = content.encode('utf-8') if isinstance(content, str) else content
        
    def read(self):
        return self.content

def test_html_processing():
    """Test HTML file processing"""
    print("Testing HTML file processing...")
    
    html_content = """<html>
    <body>
        <table>
            <tr><th>Field</th><th>Value</th></tr>
            <tr><td>TaxAmount</td><td>100.00</td></tr>
        </table>
    </body>
    </html>"""
    
    mock_file = MockUploadedFile("test.html", html_content)
    result_content, filename = process_file_content(mock_file)
    
    if result_content and result_content == html_content:
        print("✓ HTML processing successful")
        print(f"  Filename: {filename}")
    else:
        print("✗ HTML processing failed")

def test_csv_processing():
    """Test CSV file processing"""
    print("\nTesting CSV file processing...")
    
    csv_content = """Field,Value,Type
TaxAmount,100.00,Currency
ProductName,Widget,String
Quantity,5,Integer"""
    
    mock_file = MockUploadedFile("test.csv", csv_content)
    result_content, filename = process_file_content(mock_file)
    
    if result_content and "<table" in result_content and "TaxAmount" in result_content:
        print("✓ CSV processing successful")
        print(f"  Filename: {filename}")
        print(f"  HTML Table created: {len(result_content)} characters")
    else:
        print("✗ CSV processing failed")

def test_markdown_processing():
    """Test Markdown file processing"""
    print("\nTesting Markdown file processing...")
    
    md_content = """# Specifications

| Field | Description | Type |
|-------|-------------|------|
| TaxAmount | Tax value | Currency |
| ProductName | Product identifier | String |
"""
    
    mock_file = MockUploadedFile("test.md", md_content)
    result_content, filename = process_file_content(mock_file)
    
    if result_content and "TaxAmount" in result_content:
        print("✓ Markdown processing successful")
        print(f"  Filename: {filename}")
        print(f"  HTML content created: {len(result_content)} characters")
    else:
        print("✗ Markdown processing failed")

def test_unsupported_file():
    """Test unsupported file type"""
    print("\nTesting unsupported file type...")
    
    mock_file = MockUploadedFile("test.txt", "Some text content")
    result_content, filename = process_file_content(mock_file)
    
    if result_content is None and filename == "test.txt":
        print("✓ Unsupported file handling successful")
        print(f"  Filename: {filename}")
    else:
        print("✗ Unsupported file handling failed")

def main():
    print("FILE PROCESSING TEST SUITE")
    print("=" * 50)
    print("Testing file processing functionality for agentic XSLT processor")
    
    try:
        test_html_processing()
        test_csv_processing() 
        test_markdown_processing()
        test_unsupported_file()
        
        print("\n" + "=" * 50)
        print("FILE PROCESSING TESTS COMPLETED")
        print("=" * 50)
        
    except Exception as e:
        print(f"\nTEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()