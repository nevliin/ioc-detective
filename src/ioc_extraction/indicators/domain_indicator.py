from src.ioc_extraction.indicators.indicator import Indicator


class DomainIndicator(Indicator):

    def get_sigma_identifier(self) -> str:
        return 'c-uri|contains'

    def get_visual_name(self) -> str:
        return "Domainname Indicator"
