import math

from src.ioc_extraction.indicators.ip_indicator import IPv4Indicator


class IPv4MaskIndicator(IPv4Indicator):

    def get_sigma_value(self) -> str:
        ip_address, mask = self.value.split('/')
        variable_index = int(mask) / 8

        # construct sigma value
        if variable_index is None:
            sigma_value = ip_address
        else:
            sigma_value = ip_address[0:variable_index].join('.') + '.*'

        return sigma_value

    def get_visual_name(self) -> str:
        return "IPv4 Indicator"
