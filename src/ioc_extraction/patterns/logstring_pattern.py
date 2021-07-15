import operator
import re
import spacy
from typing import List

from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.indicators.logstring_indicator import LogStringIndicator
from src.ioc_extraction.patterns.indicator_pattern import IndicatorPattern
from src.text_mining.classes import Paragraph


class LogStringPattern(IndicatorPattern):
    sp = spacy.load('de_core_news_sm')

    def _find_in_paragraph(self, paragraph: Paragraph) -> List[Indicator]:
        results = []

        # Get default font of the paragraph
        fonts = {}
        for char in paragraph:
            if char.font not in fonts:
                fonts[char.font] = 1
            else:
                fonts[char.font] += 1
        default_font = max(fonts.items(), key=operator.itemgetter(1))[0]

        # Get ranges of different font in the paragraph
        different_font_texts = []
        current_font = None
        current_string = ''
        for char in paragraph:
            if current_font is None:
                current_font = char.font
                current_string += char.get_text()
                continue
            if current_font != char.font:
                if current_font != default_font:
                    different_font_texts.append(current_string)
                current_font = char.font
                current_string = ''
            current_string += char.get_text()

        # Check for named entities
        # Todo locale prediction
        sentences = paragraph.get_sentences()
        # python -m spacy download de_core_news_sm

        entity_approved_ioc = set()
        for sentence in sentences:
            sen = self.sp(sentence)
            for font_split in different_font_texts:
                for ent in sen.ents:
                    if ent.text in font_split:
                        entity_approved_ioc.add(font_split)

        # Check if there are keywords that indicate a log string ioc
        if any(keyword in paragraph.get_text().lower() for keyword in ["string", ]):
            results.extend(
                [LogStringIndicator(ioc, paragraph, paragraph.get_text().find(ioc)) for ioc in entity_approved_ioc if not "string" in ioc.lower()])
        return results
