from src.text_mining.classes import Paragraph, Character, Section, Document


def create_mock_document(text):
    paragraph = create_mock_paragraph(text)
    section = Section()
    section.add(paragraph)
    document = Document('Test Document', 'PDF')
    document.add(section)
    return document


def create_mock_paragraph(text):
    paragraph = Paragraph(0, 0)
    for char in text:
        paragraph.add(Character(char, 'MockFont', 11))
    return paragraph
