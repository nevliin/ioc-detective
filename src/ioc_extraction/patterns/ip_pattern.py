import re

from src.ioc_extraction.indicators.ip_indicator import IPv4Indicator
from src.ioc_extraction.patterns.dot_preprocessor import DotPreprocessor
from src.ioc_extraction.patterns.regex_pattern import RegexPattern


class IPv4Pattern(RegexPattern, DotPreprocessor):
    result_type = IPv4Indicator
    regex_patterns = [
        # Single IP address with optional port
        re.compile(
            "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(:\d{1,5})?")
    ]
    denylist_values = [
        '0.0.0.0',
        '0.0.0.0:*',
        '127.0.0.1',
        '127.0.0.1:*'
    ]
