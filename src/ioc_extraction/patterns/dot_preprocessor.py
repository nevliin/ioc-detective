import re

from src.ioc_extraction.patterns.preprocessor import Preprocessor
from src.text_mining.classes import Paragraph


# Removes escaping chars around dots in IP addresses and domains
class DotPreprocessor(Preprocessor):

    def preprocessing(self, paragraph: Paragraph) -> Paragraph:
        regex_pattern1 = re.compile("[^ ](\\[\\.)[^ ]")
        regex_pattern2 = re.compile("[^ ](\\.\\])[^ ]")
        regex_pattern3 = re.compile("[^ ](\\[\\:)[^ ]")
        regex_pattern4 = re.compile("[^ ](\\:\\])[^ ]")

        indices_to_remove = []
        # for match in regex_pattern.finditer(paragraph.get_text()):
        #     indices_to_remove.append(match.start() + 1)
        #     indices_to_remove.append(match.start() + 3)

        for match in regex_pattern1.finditer(paragraph.get_text()):
            indices_to_remove.append(match.start() + 1)

        for match in regex_pattern2.finditer(paragraph.get_text()):
            indices_to_remove.append(match.start() + 2)

        for match in regex_pattern3.finditer(paragraph.get_text()):
            indices_to_remove.append(match.start() + 1)

        for match in regex_pattern4.finditer(paragraph.get_text()):
            indices_to_remove.append(match.start() + 2)

        for i in sorted(indices_to_remove, reverse=True):
            paragraph.remove_index(i)
            Preprocessor.modified_indices[paragraph] = [j - 1 for j in Preprocessor.modified_indices[paragraph] if j > i]
            Preprocessor.modified_indices[paragraph].append(i)

        return paragraph
