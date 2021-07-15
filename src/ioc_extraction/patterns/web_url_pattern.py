import re
from typing import List

from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.indicators.web_url_indicator import WebURLIndicator
from src.ioc_extraction.patterns.dot_preprocessor import DotPreprocessor
from src.ioc_extraction.patterns.http_preprocessor import HTTPPreprocessor
from src.ioc_extraction.patterns.indicator_pattern import IndicatorPattern
from src.ioc_extraction.patterns.preprocessor import Preprocessor
from src.ioc_extraction.patterns.regex_pattern import RegexPattern

from src.text_mining.classes import Paragraph


class WebURLPattern(IndicatorPattern, HTTPPreprocessor, DotPreprocessor):
    result_type = WebURLIndicator

    def _find_in_paragraph(self, paragraph: Paragraph) -> List[Indicator]:
        results = []
        regex = re.compile("(http|ftp|https)://([\\w_-]+(?:(?:\\.[\\w_-]+)+))([\\w.,@?^=%&:/~+#-]*[\\w@?^=%&/~+#-])?")
        for match in regex.finditer(paragraph.get_text()):
            for i in Preprocessor.modified_indices[paragraph]:
                if match.start() <= i <= match.start() + len(match.group()):
                    results.append(self.result_type(
                        value=match.group(),
                        paragraph=paragraph,
                        start_index=match.start()
                    ))
                    break
        return results

    @staticmethod
    def postprocessing(indicators: List[Indicator]) -> List[Indicator]:
        for indicator in indicators:
            if (indicator.value[-1] in ["-", "/", "?"]) and (indicator.start_index + len(indicator.value) < len(indicator.paragraph)-1) \
                    and (indicator.paragraph.get_text()[indicator.start_index + len(indicator.value)] == "\n"):
                newline_split = indicator.paragraph.get_text()[indicator.start_index + len(indicator.value) + 1:].split("\n")
                for newline_block in newline_split:
                    whitespace_split = newline_block.split()
                    if len(whitespace_split) > 0:
                        if any(c in whitespace_split[0] for c in [".", "/"]):
                            indicator.value += whitespace_split[0]
                        else:
                            break
                        if len(whitespace_split) > 1:
                            break
                    else:
                        break
        return indicators
