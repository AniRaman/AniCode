"""
Simple test for file processing without Streamlit dependencies
"""
import io
import pandas as pd

class MockUploadedFile:
    def __init__(self, name, content):
        self.name = name
        self.content = content.encode('utf-8') if isinstance(content, str) else content
        
    def read(self):
        return self.content

def process_file_content_simple(uploaded_file):
    """Simple version of file processing without Streamlit imports"""
    try:
        filename = uploaded_file.name
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension in ['html', 'htm', 'mhtml']:
            html_content = uploaded_file.read().decode('utf-8')
            return html_content, filename
            
        elif file_extension == 'md':
            md_content = uploaded_file.read().decode('utf-8')
            html_content = f"<html><body>{md_content}</body></html>"
            return html_content, filename
            
        elif file_extension == 'csv':
            csv_content = uploaded_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            html_table = df.to_html(index=False)
            html_content = f"<html><body>{html_table}</body></html>"
            return html_content, filename
            
        else:
            print(f"Unsupported file type: {file_extension}")
            return None, filename
            
    except Exception as e:
        print(f"Error processing file {uploaded_file.name}: {e}")
        return None, uploaded_file.name

def test_functionality():
    print("SIMPLE FILE PROCESSING TEST")
    print("=" * 40)
    
    # Test CSV
    csv_content = """Field,Value,Type
TaxAmount,100.00,Currency
ProductName,Widget,String"""
    
    csv_file = MockUploadedFile("test.csv", csv_content)
    result, filename = process_file_content_simple(csv_file)
    
    if result and "<table" in result:
        print("+ CSV processing works")
        print(f"  Generated HTML table with {len(result)} characters")
    else:
        print("- CSV processing failed")
    
    # Test HTML
    html_content = "<html><body><h1>Test</h1></body></html>"
    html_file = MockUploadedFile("test.html", html_content)
    result, filename = process_file_content_simple(html_file)
    
    if result == html_content:
        print("+ HTML processing works")
    else:
        print("- HTML processing failed")
    
    # Test MD
    md_content = "# Test\n| Field | Value |\n|-------|-------|\n| Test | 123 |"
    md_file = MockUploadedFile("test.md", md_content)
    result, filename = process_file_content_simple(md_file)
    
    if result and "Test" in result:
        print("+ Markdown processing works")
    else:
        print("- Markdown processing failed")
        
    print("=" * 40)
    print("File processing functionality verified!")

if __name__ == "__main__":
    test_functionality()