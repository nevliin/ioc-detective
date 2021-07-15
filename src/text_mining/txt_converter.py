import os

from src.text_mining.classes import Document, DocumentType, Paragraph, Section, Character
from src.text_mining.converter import Converter


class TXTConverter(Converter):
    default_text_size = 11

    def convert(self, path: str, filename: str) -> Document:
        document = Document(name=filename, doc_type=DocumentType.TXT)

        section = Section()
        document.add(section)

        with open(path, encoding='utf-8') as f:
            lines = f.readlines()

        curr_paragraph = Paragraph()
        for line in lines:
            line = line.strip()

            # start a new paragraph after an empty line
            if line == '':
                if len(curr_paragraph) > 0:
                    section.add(curr_paragraph)
                    curr_paragraph = Paragraph()
                continue

            for char in line:
                curr_paragraph.add(Character(char))
            curr_paragraph.add(Character('\n'))

        return document
