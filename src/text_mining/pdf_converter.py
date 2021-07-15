import os
import zlib
from functools import cmp_to_key
from typing import Union, List

import pytesseract
from PIL import Image
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextContainer, LTAnno, LTPage, LTFigure, LTImage, LTTextBoxHorizontal, \
    LTTextLineHorizontal
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdffont import PDFFont
from pdfminer.pdfparser import PDFParser

from src.text_mining.classes import Document, DocumentType, Character, Paragraph, FakeDescriptor, Section
from src.text_mining.converter import Converter


class PDFConverter(Converter):
    paragraph_distance_modifier = 0.90
    filtered_chars = ['\n']
    language_to_pytesseract = {
        'de': 'deu',
        'en': 'eng'
    }

    def convert(self, path, filename) -> Document:
        document = Document(name=filename, doc_type=DocumentType.PDF)
        pages = self.load_pages(path)

        # split into paragraphs
        paragraphs = []
        for page_layout in pages:
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    # create a new section and fill it
                    paragraphs.extend(PDFConverter.assign_to_paragraphs(element))

        for i in range(len(paragraphs) - 1, -1, -1):
            if len(paragraphs[i]) == 0:
                del paragraphs[i]

        # split into sections
        sections = PDFConverter.assign_to_sections(paragraphs)
        document.extend(sections)

        return document

    # Derived indicators can override this to alter the converted pages
    def load_pages(self, path) -> List[LTPage]:
        pages = list(extract_pages(path))
        # pages = PDFConverter.detect_and_convert_images(pages, path)
        return pages

    @staticmethod
    def assign_to_sections(paragraphs: List[Paragraph]) -> List[Section]:
        sections = []
        current_section = None
        for i in range(0, len(paragraphs) - 1):
            if round(paragraphs[i].get_font_size(), 2) > round(paragraphs[i + 1].get_font_size(), 2) \
                    and len(paragraphs[i]) < 80:
                if current_section is not None:
                    sections.append(current_section)
                current_section = Section(title=paragraphs[i].get_text())
            else:
                if current_section is None:
                    # Create a Pre-Section if necessary
                    current_section = Section()
            current_section.add(paragraphs[i])

        current_section.add(paragraphs[-1])
        sections.append(current_section)

        # Merge sections with duplicated title (likeli header/footer)
        section_titles = [section.title for section in sections]
        duplicated_titles = set([title for title in section_titles if section_titles.count(title) > 1])
        for i in range(len(sections) - 1, 0, -1):
            if sections[i].title in duplicated_titles:
                sections[i - 1].extend(sections[i])
                del sections[i]

        return sections

    @staticmethod
    def assign_to_paragraphs(element: LTTextContainer) -> List[Paragraph]:
        # create a new section and fill it
        paragraphs = []

        previous_distance = None
        previous_size = None
        previous_y = None
        curr_paragraph = Paragraph(None, None)
        for text_line in element:
            # Skip text lines with no content
            text_line_content = text_line.get_text()
            text_line_content = text_line_content.replace('\n', ' ').strip()
            if len(text_line_content.strip()) == 0:
                continue

            characters = PDFConverter.convert_lttexts_to_chars(text_line)

            # Initialize previous size
            if previous_size is None:
                previous_size = characters[0].size

            # Initialize coordinates
            if curr_paragraph.x0 is None or curr_paragraph.y0 is None:
                curr_paragraph.x0 = text_line.x0
                curr_paragraph.y0 = text_line.y0

            # Initialize y
            if previous_y is None:
                previous_y = text_line.y0
                curr_paragraph.extend(characters)
                continue

            # Check for different size
            if round(characters[0].size, 2) != round(previous_size, 2):
                # New paragraph
                paragraphs.append(curr_paragraph)
                curr_paragraph = Paragraph(None, None)
                previous_size = characters[0].size

            # Initialize previous distance
            if previous_distance is None:
                previous_distance = previous_y - text_line.y0
                previous_y = text_line.y0
                curr_paragraph.extend(characters)
                continue

            curr_distance = (previous_y - text_line.y0) * PDFConverter.paragraph_distance_modifier
            if curr_distance > previous_distance:
                # New paragraph
                paragraphs.append(curr_paragraph)
                curr_paragraph = Paragraph(None, None)

            curr_paragraph.extend(characters)

            # Update previous distance
            previous_distance = previous_y - text_line.y0
            previous_y = text_line.y0

        if len(curr_paragraph) > 0:
            curr_paragraph.trimr()
            paragraphs.append(curr_paragraph)

        return paragraphs

    @staticmethod
    def convert_lttexts_to_chars(lttexts: List[Union[LTChar, LTAnno]], add_linebreak=True) -> List[Character]:

        characters = []
        lttext = None
        for lttext in lttexts:
            if lttext.get_text() not in PDFConverter.filtered_chars:
                if isinstance(lttext, LTChar):
                    characters.append(Character(lttext.get_text(), lttext.fontname, lttext.size))
                if isinstance(lttext, LTAnno):
                    characters.append(Character(lttext.get_text(), None, None))
        if add_linebreak and lttext is not None:
            if isinstance(lttext, LTAnno):
                characters.append(Character('\n', None, None))
            else:
                characters.append(Character('\n', lttext.fontname, lttext.size))

        return characters
