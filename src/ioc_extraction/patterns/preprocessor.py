from abc import abstractmethod

from src.text_mining.classes import Paragraph


class Preprocessor:
    modified_indices = {}

    @abstractmethod
    def preprocessing(self, paragraph: Paragraph) -> Paragraph:
        pass
