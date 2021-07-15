import re
from typing import List

from src.ioc_extraction.indicators.domain_indicator import DomainIndicator
from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.patterns.dot_preprocessor import DotPreprocessor
from src.ioc_extraction.patterns.indicator_pattern import IndicatorPattern
from src.ioc_extraction.patterns.preprocessor import Preprocessor
from src.text_mining.classes import Paragraph


class DomainPattern(IndicatorPattern, DotPreprocessor):
    result_type = DomainIndicator
    # regex_pattern = re.compile("(<(\w| |-)+>|\w+)(\.(<(\w| |-)+>|\w+))+")

    regex_pattern = re.compile("(<(\w| |-|-\n)+>|(\w|-|-\n)+)(\.(<(\w| |-|-\n)+>|(\w|-\n|-)+))+")

    def _find_in_paragraph(self, paragraph: Paragraph) -> List[Indicator]:
        results = []
        for match in self.regex_pattern.finditer(paragraph.get_text()):
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
            indicator.value = indicator.value.replace("\n", "")
        return indicators
