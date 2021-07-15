import re

from src.ioc_extraction.patterns.preprocessor import Preprocessor
from src.text_mining.classes import Paragraph


class HTTPPreprocessor(Preprocessor):

    def preprocessing(self, paragraph: Paragraph) -> Paragraph:
        regex_pattern = re.compile("(hxxp|hxxps)+(://)")

        for match in regex_pattern.finditer(paragraph.get_text().lower()):
            paragraph.get_index(match.start() + 1).set_text("t")
            paragraph.get_index(match.start() + 2).set_text("t")

            Preprocessor.modified_indices[paragraph].append(match.start() + 1)
            Preprocessor.modified_indices[paragraph].append(match.start() + 2)

        return paragraph
