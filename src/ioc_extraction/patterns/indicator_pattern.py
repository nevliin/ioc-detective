from __future__ import annotations

from typing import List

from src.ioc_extraction.indicators.indicator import Indicator
from src.text_mining.classes import Paragraph


class IndicatorPattern:
    supporting_evidence: List[str] = []
    negating_evidence: List[str] = []

    denylist_values: List[str] = []

    __denylist_values_includes: List[str] = []
    __denylist_values_starts_with: List[str] = []
    __denylist_values_ends_with: List[str] = []
    __denylist_values_is: List[str] = []

    def __init__(self):
        deny_values = list(self.denylist_values)

        for deny_value in list(deny_values):
            if deny_value.startswith('*') and deny_value.endswith('*'):
                self.__denylist_values_includes.append(deny_value.replace('*', ''))
                deny_values.remove(deny_value)

        for deny_value in list(deny_values):
            if deny_value.endswith('*'):
                self.__denylist_values_starts_with.append(deny_value.replace('*', ''))
                deny_values.remove(deny_value)

        for deny_value in list(deny_values):
            if deny_value.startswith('*'):
                self.__denylist_values_ends_with.append(deny_value.replace('*', ''))
                deny_values.remove(deny_value)

        self.__denylist_values_is = deny_values

    def find_in_paragraph(self, paragraph: Paragraph, previous_indicators: List[Indicator]) -> List[
        Indicator]:
        indicators = self._find_in_paragraph(paragraph)
        indicators = self.postprocessing(indicators)
        result = []

        for indicator in indicators:
            if not IndicatorPattern.was_indicator_previously_found(indicator, previous_indicators) \
                    and not self.indicator_in_denylist(indicator):
                result.append(indicator)

        return result

    def _find_in_paragraph(self, paragraph: Paragraph) -> List[Indicator]:
        raise NotImplementedError

    @staticmethod
    def was_indicator_previously_found(indicator, previous_indicators: List[Indicator]) -> bool:
        for curr_indicator in previous_indicators:
            if curr_indicator.paragraph.__hash__() == indicator.paragraph.__hash__():
                end_index = curr_indicator.start_index + len(curr_indicator.value)
                if curr_indicator.start_index <= indicator.start_index <= end_index:
                    return True
        return False

    @staticmethod
    def postprocessing(indicators: List[Indicator]) -> List[Indicator]:
        return indicators

    def indicator_in_denylist(self, indicator: Indicator):
        if len(self.denylist_values) == 0:
            return False

        for deny_value in self.__denylist_values_includes:
            if deny_value in indicator.value:
                return True
        for deny_value in self.__denylist_values_starts_with:
            if indicator.value.startswith(deny_value):
                return True
        for deny_value in self.__denylist_values_ends_with:
            if indicator.value.endswith(deny_value):
                return True
        for deny_value in self.__denylist_values_is:
            if deny_value == indicator.value:
                return True

        return False
