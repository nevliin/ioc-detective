from src.ioc_extraction.indicators.indicator import Indicator

class UAgentIndicator(Indicator):

    def get_sigma_identifier(self) -> str:
        return 'c-useragent'

    def get_visual_name(self) -> str:
        return "User-Agent Indicator"