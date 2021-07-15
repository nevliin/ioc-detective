from typing import Optional

from src.ioc_extraction.indicators.indicator import Indicator


class HTTPRequestMethodIndicator(Indicator):

    standalone = False

    def get_sigma_identifier(self) -> str:
        return 'cs-method'

    def get_sigma_value(self) -> Optional[str]:
        if len(self.value) == 1:
            return self.value[0]
        else:
            return self.value

    def get_visual_name(self) -> str:
        return "HTTP-Request-Method Indicator"
