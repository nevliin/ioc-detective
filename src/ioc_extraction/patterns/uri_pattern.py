import re
from typing import List

from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.indicators.uri_indicator import URIIndicator
from src.ioc_extraction.patterns.indicator_pattern import IndicatorPattern
from src.ioc_extraction.patterns.regex_pattern import RegexPattern
from src.text_mining.classes import Paragraph


class URIPattern(IndicatorPattern):
    result_type = URIIndicator
    # regex_pattern = re.compile("((/|<(\w| )+>/)+(<(\w| )+>|\w+))+")
    regex_pattern = re.compile("([A-Z]:|%\w+%)?(((/|\\\)|(/|\\\)((\w|-|\?|\=|\%|\.)+(/|\\\))+|<([^<])+>(/|\\\))+((\w|\?|\=|-|\.|\%)+(/|\\\|\?|\=|-)\n|<([^<])+>|((\.)?(\w|-|\?|\=|\%))+))+(//|/|\\\)?")
        # re.compile("[\\\\/].*\\.[\\w:]+"),  # File Path old

        # re.compile("[\\\\/].*\\.")

    def _find_in_paragraph(self, paragraph: Paragraph) -> List[Indicator]:
        results = []
        for match in self.regex_pattern.finditer(paragraph.get_text()):
            if match.start() == 0 and len(match.group()) > 3:
                results.append(self.result_type(
                    value=match.group(),
                    paragraph=paragraph,
                    start_index=match.start()
                ))
            else:
                char_before_match = paragraph.get_text()[match.start()-1]
                if char_before_match in [" ", "\n"] and len(match.group()) > 3:
                    results.append(self.result_type(
                        value=match.group(),
                        paragraph=paragraph,
                        start_index=match.start()
                    ))
        return results
