from typing import List

import yaml

from src.ioc_extraction.indicators.indicator_group import IndicatorGroup
from src.util import LogCollector


class RuleGenerator:

    def __init__(self, document_name: str, save_path: str, log_collector: LogCollector = None):
        self.document_name = document_name
        self.save_path = save_path
        self.log_collector = log_collector

    def generate(self, indicator_groups: List[IndicatorGroup]):
        # Create Dictionary and add metadata
        selections = {"selection" + str(index + 1): indicator_groups[index].extract_sigma_selection() for index in
                      range(0, len(indicator_groups))}
        selections["condition"] = "1 of them"
        yaml_dict = {
            "title": "Generated Sigma Rule",
            "status": "experimental",
            "description": f"This sigma rule was automatically created from the source file {self.document_name}",
            # "logsource": {"category": "webserver (TBA needed?)"},
            "detection": selections
        }
        with open(self.save_path, "w") as file:
            documents = yaml.dump(yaml_dict, file)
            return "True"
