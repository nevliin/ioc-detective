from src.ioc_extraction.indicators.indicator import Indicator


class HashIndicator(Indicator):

    def get_sigma_identifier(self) -> str:
        return 'keyword'

    def get_visual_name(self) -> str:
        return "Hash Indicator"
