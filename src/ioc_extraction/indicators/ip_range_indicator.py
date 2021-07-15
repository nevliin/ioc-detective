from typing import Optional

from src.ioc_extraction.indicators.ip_indicator import IPv4Indicator


class IPv4RangeIndicator(IPv4Indicator):

    def get_sigma_value(self) -> Optional[str]:
        ip_address1, ip_address2 = [value.split('.') for value in [value.strip() for value in self.value.split('-')]]

        # find at which part the ip addresses vary
        variable_index = None
        for i in range(3, -1, -1):
            if ip_address1[i] != ip_address2[i]:
                variable_index = i

        # construct sigma value
        if variable_index is None:
            sigma_value = ip_address1
        # Only include more specific ip address ranges
        elif variable_index > 1:
            sigma_value = '.'.join(ip_address1[0:variable_index]) + '.*'
        else:

            return None

        return sigma_value

    def get_visual_name(self) -> str:
        return "IPv4 Indicator"