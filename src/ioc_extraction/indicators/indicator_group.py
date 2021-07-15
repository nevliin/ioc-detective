from typing import List

from src.ioc_extraction.indicators.indicator import Indicator


class IndicatorGroup:
    indicators: List[Indicator] = []

    def __init__(self, indicators: List[Indicator]) -> None:
        super().__init__()
        self.indicators = indicators

    def __iter__(self):
        return iter(self.indicators)

    def __len__(self):
        return len(self.indicators)

    def append(self, indicator: Indicator):
        self.indicators.append(indicator)

    def extract_sigma_selection(self) -> dict:
        result = {}
        for indicator in self.indicators:
            if indicator.get_sigma_identifier() not in result:
                result[indicator.get_sigma_identifier()] = []
            result[indicator.get_sigma_identifier()].append(indicator.get_sigma_value())

        return result
