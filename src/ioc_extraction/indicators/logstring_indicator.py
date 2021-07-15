from src.ioc_extraction.indicators.indicator import Indicator


class LogStringIndicator(Indicator):

    def get_sigma_identifier(self) -> str:
        return 'keyword'

    def get_visual_name(self) -> str:
        return "Logstring Indicator"
