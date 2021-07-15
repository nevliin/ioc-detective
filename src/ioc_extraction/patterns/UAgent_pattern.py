import re
from typing import List

from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.indicators.useragent_indicator import UAgentIndicator
from src.ioc_extraction.patterns.regex_pattern import RegexPattern
from src.ioc_extraction.indicators.indicator import Indicator
from src.ioc_extraction.indicators.web_url_indicator import WebURLIndicator
from src.ioc_extraction.patterns.dot_preprocessor import DotPreprocessor
from src.ioc_extraction.patterns.http_preprocessor import HTTPPreprocessor
from src.ioc_extraction.patterns.indicator_pattern import IndicatorPattern
from src.ioc_extraction.patterns.preprocessor import Preprocessor
from src.ioc_extraction.patterns.regex_pattern import RegexPattern

from src.text_mining.classes import Paragraph

class UserAgentPattern(RegexPattern):
    result_type = UAgentIndicator
    regex_patterns = [
        #alte
        re.compile("[a-zA-Z]+[-]?[a-zA-Z]+[\/][a-zA-Z]?((?:\d{1,4}\.){1,4}\d{1,4})+[ ]?[(,{,+,;].*"),
        re.compile("[a-zA-Z]+[-]?[a-zA-Z]+\/[a-zA-Z]?((?:\d{1,4}\.){2,4}\d{1,4})[ ][^(,{,+,;]"),  # File Path
        re.compile("[a-zA-Z]+[-]?[a-zA-Z]+\/[a-zA-Z]{1}[0-9,\.]+[ ]?[ ][^(,{,+,;]"),  # File Path
        re.compile("^\w+\/[a-zA-Z]?((?:\d{1,4}\.){1,4}\d{1,4})"),



    ]





    @staticmethod
    def postprocessing(indicators: List[Indicator]) -> List[Indicator]:
        pattern = re.compile(r'\s+')

        for i in indicators:
            i.value =  re.sub(pattern, '', i.value)

        return indicators