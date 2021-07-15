from typing import List

from src.ioc_extraction.indicator_utils import combine_indicators, \
    IndicatorCombinationMode, filter_indicator_groups
from src.ioc_extraction.indicators.indicator_group import IndicatorGroup
from src.ioc_extraction.patterns.UAgent_pattern import UserAgentPattern
from src.ioc_extraction.patterns.domain_pattern import DomainPattern
from src.ioc_extraction.patterns.hash_pattern import HashPattern
from src.ioc_extraction.patterns.http_request_method_pattern import HTTPRequestMethodPattern
from src.ioc_extraction.patterns.ip_mask_pattern import IPv4MaskPattern
from src.ioc_extraction.patterns.ip_pattern import IPv4Pattern
from src.ioc_extraction.patterns.logstring_pattern import LogStringPattern
from src.ioc_extraction.patterns.ip_range_pattern import IPv4RangePattern
from src.ioc_extraction.patterns.preprocessor import Preprocessor
from src.ioc_extraction.patterns.uri_pattern import URIPattern
from src.ioc_extraction.patterns.web_url_pattern import WebURLPattern
from src.text_mining.classes import Document
from src.util import LogCollector


class IoCExtractor:
    available_patterns = {
        'IP': [
            IPv4RangePattern(),
            IPv4MaskPattern(),
            IPv4Pattern()
        ],
        'Hash': [
            HashPattern()
        ],
        'WebURL': [
            WebURLPattern(),
            DomainPattern()
        ],
        'URI': [
            URIPattern()
        ],
        'UserAgent': [
            UserAgentPattern()
        ],
        'HTTPRequestMethod': [
            HTTPRequestMethodPattern()
        ],
        'LogString': [
            LogStringPattern()
        ]
    }

    patterns = []

    def __init__(self, log_collector: LogCollector, pattern_filter: List[str] = None,
                 mode: IndicatorCombinationMode = IndicatorCombinationMode.SECTION,
                 use_external_services=True,
                 language='en'):
        self.mode = mode
        self.use_external_services = use_external_services
        self.language = language
        self.log_collector = log_collector
        if pattern_filter is not None:
            for key, value in self.available_patterns.items():
                if key in pattern_filter:
                    self.patterns.extend(value)
        else:
            for key, value in self.available_patterns.items():
                self.patterns.extend(value)

    def extract(self, document: Document) -> List[IndicatorGroup]:
        # Preprocessing
        document = self.preprocess_document(document)

        # IoC Extraction (currently per section)
        indicators_by_section = []
        for section in document:
            indicators = []
            for paragraph in section:
                for pattern in self.patterns:
                    indicators.extend(pattern.find_in_paragraph(paragraph, previous_indicators=indicators))
            indicators_by_section.append(indicators)

        indicator_groups = self.group_indicators(indicators_by_section)

        return indicator_groups

    def preprocess_document(self, document: Document) -> Document:
        global_position = 0
        for section in document:
            for paragraph in section:
                Preprocessor.modified_indices[paragraph] = []
                for pattern in self.patterns:
                    if isinstance(pattern, Preprocessor):
                        paragraph = pattern.preprocessing(paragraph)
                paragraph.global_position = global_position
                global_position += len(paragraph)

        return document

    def group_indicators(self, indicators_by_section: List) -> List[IndicatorGroup]:
        indicator_groups = combine_indicators(indicators_by_section, self.mode)

        # Filter out unwanted indicators, e.g. non standalone
        indicator_groups = filter_indicator_groups(indicator_groups, self.log_collector)

        return indicator_groups
