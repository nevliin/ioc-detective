import json
import os

import jellyfish
from langdetect import detect

from src.text_mining.classes import Document, Denylist, TextContainer, DenyItem
from src.util import LogCollector


class Converter:

    config_file = os.path.join(os.path.dirname(__file__), '../config.json')

    def __init__(self, log_collector: LogCollector):
        self.log_collector = log_collector
        with open(self.config_file) as f:
            config = json.load(f)
        self.denylist = [DenyItem(item) for item in config["denylist_paragraphs"]]

    def run(self, path: str, filename: str) -> Document:
        document = self.convert(path, filename)
        document = self.filter(document)
        document.locale = detect(document.get_text())
        return document

    def convert(self, path: str, filename: str) -> Document:
        raise NotImplementedError

    def filter(self, document: Document) -> Document:
        paragraph_indices = []
        for i in range(len(document)):
            if Converter.is_in_denylist(list(document)[i], self.get_denylist()):
                paragraph_indices.append(i)
            else:
                sentence_indices = []
                paragraph = document.get_index(i)
                for j in range(len(paragraph)):
                    if Converter.is_in_denylist(list(paragraph)[j], self.get_denylist()):
                        sentence_indices.append(i)
                for index in reversed(sentence_indices):
                    paragraph.remove_index(index)

        for index in reversed(paragraph_indices):
            document.remove_index(index)
        return document

    @staticmethod
    def is_in_denylist(text_container: TextContainer, denylist: Denylist):
        for item in denylist:
            if Converter.is_similar(text_container, item, denylist.base_precision):
                return True
        return False

    @staticmethod
    def is_similar(text_container: TextContainer, deny_item: DenyItem, base_precision) -> bool:
        precision = base_precision if deny_item.precision is None else deny_item.precision
        levenshtein_distance = jellyfish.levenshtein_distance(text_container.get_text(), deny_item.value)
        return levenshtein_distance < precision

    def get_denylist(self) -> Denylist:
        return Denylist(self.denylist, 1)
