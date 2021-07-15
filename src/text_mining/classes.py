from dataclasses import dataclass, field
from enum import Enum
from typing import List, Iterable, Dict, Optional

import nltk


class DocumentType(Enum):
    PDF = 1
    BSI_PDF = 2
    TXT = 3
    HTML = 4


@dataclass
class TextAnalysisResult:
    fonts: Dict[str, int] = field(default_factory={})
    sizes: Dict[float, int] = field(default_factory={})
    chars: int = 0
    average_size: float = None


class Text:
    parent = None
    """Interface for things that have text"""

    def __repr__(self):
        return repr(self.get_text())

    def get_text(self):
        """Text contained in this object"""
        raise NotImplementedError


class TextContainer(Text):
    """Object that can contain other text objects"""

    def __init__(self):
        self._objs: List[Text] = []
        return

    def __iter__(self):
        return iter(self._objs)

    def __len__(self):
        return len(self._objs)

    def add(self, obj: Text):
        obj.parent = self
        self._objs.append(obj)

    def extend(self, objs: Iterable[Text]):
        for obj in objs:
            self.add(obj)

    def get_index_of(self, obj: Text):
        return self._objs.index(obj)

    def get_index(self, index):
        if len(self._objs) > index:
            return self._objs[index]
        else:
            return None

    def get_range(self, start_index, end_index):
        return self._objs[start_index:end_index]

    def remove_index(self, index):
        self._objs[index].parent = None
        del self._objs[index]

    def remove_range(self, start_index, end_index):
        for obj in self._objs[start_index:end_index]:
            obj.parent = None
        del self._objs[start_index:end_index]

    def has_children(self):
        return len(self._objs) > 0

    def clear_children(self):
        for obj in self._objs:
            obj.parent = None
        self._objs.clear()

    def get_text(self):
        return ''.join(obj.get_text() for obj in self._objs
                       if isinstance(obj, Text))

    def analyse(self) -> TextAnalysisResult:
        result = TextAnalysisResult()
        self._analyse_text(self, result)

        sum_sizes = 0
        for size in result.sizes:
            sum_sizes += size * result.sizes[size]
            result.chars += result.sizes[size]

        result.average_size = sum_sizes / result.chars
        return result

    @staticmethod
    def _analyse_text(text, result):
        for obj in text:
            if isinstance(obj, Character):
                if obj.font not in result.fonts:
                    result.fonts[obj.font] = 0
                result.fonts[obj.font] += 1

                if obj.size not in result.sizes:
                    result.sizes[obj.size] = 0
                result.sizes[obj.size] += 1
            elif isinstance(obj, TextContainer):
                obj._analyse_text(obj, result)


class Document(TextContainer):
    locale: str = None

    def __init__(self, name, doc_type, title=None):
        TextContainer.__init__(self)
        self.name = name
        self.doc_type = doc_type
        self.title = title


class Section(TextContainer):
    def __init__(self, title=None):
        TextContainer.__init__(self)
        self.title = title


class Paragraph(TextContainer):
    def __init__(self, x0=None, y0=None):
        TextContainer.__init__(self)
        self.global_position = 0
        self.x0 = x0
        self.y0 = y0

    def get_sentences(self) -> List[str]:
        # break section text into sentences
        locale = self.parent.parent.locale
        paragraph_text = self.get_text()
        locale_mappings = {
            'de': 'german',
            'en': 'english',
        }

        if locale in locale_mappings:
            language = locale_mappings[locale]
        else:
            language = 'german'

        return nltk.sent_tokenize(paragraph_text, language=language)

    def trimr(self):
        # delete ending space characters
        for i in range(len(self._objs) - 1, 0, -1):
            if self._objs[i].get_text() == ' ':
                del self._objs[i]
            else:
                break

    def get_font_size(self):
        if len(self._objs) > 0:
            first_char = self._objs[0]
            return first_char.size


class Character(Text):
    default_text_size = 11

    def __init__(self, text, font=None, size=default_text_size):
        self._text = text
        self.font = font
        self.size = size

    def get_text(self):
        return self._text

    def set_text(self, text):
        self._text = text


@dataclass
class DenyItem:
    value: str
    precision: Optional[int] = None  # hamming distance to the value that should still be removed


class Denylist:

    def __iter__(self):
        return iter(self.items)

    def __init__(self, items: List[DenyItem], base_precision):
        self.items = items
        self.base_precision = base_precision


class FakeDescriptor:
    def get(self, key, fallback):
        return fallback
