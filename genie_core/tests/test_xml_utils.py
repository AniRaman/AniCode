import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from unittest.mock import patch, MagicMock
sys.modules['saxonche'] = MagicMock()

from genie_core.xml_processing.xml_utils import process_xml, verify_prerequisite, copy_text

class TestXmlUtils(unittest.TestCase):
    def test_process_xml(self):
        # TODO: Implement test cases for process_xml function
        pass

    def test_verify_prerequisite(self):
        self.assertEqual(verify_prerequisite("", ""), "Upload input XML & upload output XML")
        self.assertEqual(verify_prerequisite("input", ""), "Upload output XML")
        self.assertEqual(verify_prerequisite("", "output"), "Upload input XML")
        self.assertEqual(verify_prerequisite("input", "output"), "")

    def test_copy_text(self):
        self.assertEqual(copy_text("test"), "test")

if __name__ == '__main__':
    unittest.main()