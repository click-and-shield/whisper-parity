from typing import List
import re


class Sentence:

    @staticmethod
    def clean(sentence: str) -> str:
        sentence = re.sub(r'\s+', ' ', sentence)
        sentence = re.sub(r'[!?. \s]*$', '', sentence)
        sentence = re.sub(r'^\s*', '', sentence)
        return sentence

    @staticmethod
    def split(sentence: str) -> List[str]:
        words: list[str] = re.split('[\s,;]+', Sentence.clean(sentence))
        for word in words:
            word.strip()
        return words

    def __init__(self, sentence: str) -> None:
        self.string: str = sentence.strip()
        self.words: List[str] = Sentence.split(sentence)

    def __len__(self) -> int:
        return len(self.words)

    def __str__(self) -> str:
        return self.string

    def get_word(self, index: int) -> str:
        return self.words[index]

    def get_words(self) -> List[str]:
        return self.words
