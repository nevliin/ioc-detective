import uuid
from abc import abstractmethod
from typing import List, Optional

from src.text_mining.classes import Paragraph


class Indicator:
    value: str

    paragraph: Paragraph
    start_index: int

    secondary_indicator_types: List = []
    secondary_indicators_max_distance = 2

    standalone = True

    def __init__(self, value: str, paragraph: Paragraph, start_index: int):
        self.value = value
        self.paragraph = paragraph
        self.start_index = start_index
        self.uuid = str(uuid.uuid4())

    def get_sigma_value(self) -> Optional[str]:
        result = self.postprocessing(self.value)
        # e. g. 'POST'
        return result

    @abstractmethod
    def get_sigma_identifier(self) -> str:
        pass

    @abstractmethod
    def get_visual_name(self) -> str:
        pass

    def postprocessing(self, value) -> str:
        return value
