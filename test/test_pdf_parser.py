import os
import unittest
from os.path import dirname

from src.text_mining.pdf_converter import PDFConverter
from src.util import LogCollector

STRUCTURE_TEST_PDF = os.path.join(dirname(__file__), 'pdfs', 'structure_test.pdf')


class TestPDFParser(unittest.TestCase):

    parser = PDFConverter(LogCollector())

    def test_structure_detection(self):
        document = self.parser.convert(STRUCTURE_TEST_PDF, filename='structure_test.pdf')
        assert len(document) == 3
        section_0 = document.get_index(0)
        assert len(section_0) == 3
        assert section_0.title == "My Title \n"
        paragraph_0 = section_0.get_index(1)
        assert len(paragraph_0) == 654
        char_0 = paragraph_0.get_index(0)
        assert char_0.font == 'BCDGEE+Calibri'
        assert char_0.size == 11
        assert char_0.get_text() == 'L'

