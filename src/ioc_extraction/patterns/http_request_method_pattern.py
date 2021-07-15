import re

from src.ioc_extraction.indicators.http_request_method_indicator import HTTPRequestMethodIndicator
from src.ioc_extraction.patterns.regex_pattern import RegexPattern


class HTTPRequestMethodPattern(RegexPattern):
    result_type = HTTPRequestMethodIndicator
    regex_patterns = [
        re.compile("(GET|HEAD|POST|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH)")
    ]