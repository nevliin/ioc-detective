from typing import Optional, List

from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.patterns.indicator_pattern import IndicatorPattern
from src.text_mining.classes import Paragraph


class RegexPattern(IndicatorPattern):
    regex_patterns = []
    result_type = Indicator

    def _find_in_paragraph(self, paragraph: Paragraph) -> List[Indicator]:
        results = []
        for regex_pattern in self.regex_patterns:
            for match in regex_pattern.finditer(paragraph.get_text()):
                results.append(self.result_type(
                    value=match.group(),
                    paragraph=paragraph,
                    start_index=match.start()
                ))
        return results
