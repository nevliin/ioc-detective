import re

from src.ioc_extraction.indicators.hash_indicator import HashIndicator
from src.ioc_extraction.patterns.regex_pattern import RegexPattern


class HashPattern(RegexPattern):
    result_type = HashIndicator
    regex_patterns = [
        re.compile("(?:(?<=\\s)|(?<=\\b))([A-Fa-f0-9]{64}|[A-Fa-f0-9]{40}|[A-Fa-f0-9]{32})(?=\\s|$|[,\\.])")
    ]
