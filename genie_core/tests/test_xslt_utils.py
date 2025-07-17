import unittest
import sys
import os
import shutil
from unittest.mock import patch, MagicMock
from  pathlib import Path

sys.modules['saxonche'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['dotenv'] = MagicMock()
sys.modules['gradio'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['chromadb.utils'] = MagicMock()
sys.modules['rich'] = MagicMock()
sys.modules['rich.console'] = MagicMock()
sys.modules['rich.syntax'] = MagicMock()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from xslt.xslt_utils import apply_xslt, save_generated_xslt, save_generated_xml, compare_xslt

class TestXsltUtils(unittest.TestCase):
    def test_apply_xslt(self):
        # TODO: Implement test cases for apply_xslt function
        pass

    def test_save_generated_xslt(self):
        expected_filename = "generated_xslt.xslt"
        test_dir = os.path.join(os.path.dirname(__file__), 'tests_data')

        try:
            shutil.rmtree(expected_filename)
            save_generated_xslt(expected_filename, test_dir)
            self.assertTrue(Path(test_dir+"/"+expected_filename))
        except OSError as e:
            print(f"Error: {test_dir} : {e.strerror}")

    def test_save_generated_xml(self):
        expected_filename = "generated_xml.xml"
        test_dir = os.path.join(os.path.dirname(__file__), 'tests_data')

        try:
            shutil.rmtree(test_dir)
            save_generated_xml(expected_filename, test_dir)
            self.assertTrue(Path(test_dir+"/"+expected_filename))
        except OSError as e:
            print(f"Error: {test_dir} : {e.strerror}")

    def test_compare_xslt(self):
        # TODO: Implement test cases for compare_xslt function
        pass

if __name__ == '__main__':
    unittest.main()