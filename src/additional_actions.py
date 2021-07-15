import logging
import re
from typing import Optional, List

from src.text_mining.classes import Paragraph, Document
from src.util import LogCollector

SIGMA_RULE_REPO = "https://github.com/SigmaHQ/sigma"


def find_rule_links(log_collector: LogCollector, document: Document):
    for section in document:
        for paragraph in section:
            find_sigma_rules(log_collector, paragraph)


def find_sigma_rules(log_collector: LogCollector, paragraph: Paragraph):
    if 'sigma' in paragraph.get_text().lower():
        regex = re.compile("(http|ftp|https)://([\\w_-]+(?:(?:\\.[\\w_-]+)+))([\\w.,@?^=%&:/~+#-]*[\\w@?^=%&/~+#-])?")
        for match in regex.finditer(paragraph.get_text()):
            if SIGMA_RULE_REPO in match.group():
                log_collector.add('Rule Link Detection', f'Link to Sigma Rule detected: {match.group()}', logging.INFO)
