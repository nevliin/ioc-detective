import re

from src.ioc_extraction.indicators.ip_range_indicator import IPv4RangeIndicator
from src.ioc_extraction.patterns.dot_preprocessor import DotPreprocessor
from src.ioc_extraction.patterns.ip_pattern import IPv4Pattern
from src.ioc_extraction.patterns.regex_pattern import RegexPattern


class IPv4RangePattern(IPv4Pattern):
    result_type = IPv4RangeIndicator
    regex_patterns = [
        re.compile(
            "((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?) - (?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))")
    ]
