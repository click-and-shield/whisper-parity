from typing import Tuple, Optional, cast
from typing import Generator
import re

class SentenceDetector:

    def __init__(self) -> None:
        self.sentence: str = ''
        self.counter: int = 0

    def detect(self, character: Optional[str], last: bool = False) -> Tuple[bool, Optional[str]]:

        if last:
            # we reached the end of the string
            if self.counter != 0 and self.counter != 1 and self.counter != 3:
                # A sentence may ends with ".","...", "?", "!" or "nothing"
                raise ValueError("Invalid character '{}' (dot counter={})".format(character, self.counter))
            last_sentence: str = re.sub(r'[\n ]+', ' ', self.sentence.strip(' \n\t'))
            self.sentence = ''
            if last_sentence != '':
                return True, last_sentence
            return False, None

        if character == '?' or character == '!':
            sentence = re.sub(r'[\n ]+', ' ', (self.sentence + cast(str, character)).strip(' \n\t'))
            self.sentence = ''
            return True, sentence
        if character == '.':
            self.counter += 1
            self.sentence += cast(str, character)
            return False, None
        if character == '\n':
            if self.counter > 0:
                return False, None
            self.sentence += cast(str, character)

        if self.counter > 0: # processing "." or "..." as "end of sentence" (OES) markers
            if self.counter != 1 and self.counter != 3:
                raise ValueError("Invalid character '{}' (dot counter={})".format(character, self.counter))
            self.counter = 0
            sentence = re.sub(r'[\n ]+', ' ', self.sentence.strip(' \n\t'))
            self.sentence = cast(str, character)
            return True, sentence
        self.sentence += cast(str, character)
        return False, None

def read_sentences_from_sting(text: str) -> Generator[str, None, None]:
    detector = SentenceDetector()
    for c in text:
        found, sentence = detector.detect(character=c)
        if found:
            yield cast(str, sentence)
    found, sentence = detector.detect(character=None, last=True)
    if found:
        yield cast(str, sentence)

def extract_sentences_from_string(text: str) -> list[str]:
    sentences: list[str] = []
    for s in read_sentences_from_sting(text):
        sentences.append(s)
    return sentences

def read_sentences_from_file(path: str) -> Generator[str, None, None]:
    detector = SentenceDetector()
    with open(path, 'r') as f:
        while True:
            character: str = f.read(1)
            if character == '': # the end of the file as been reached
                found, sentence = detector.detect(character=None, last=True)
                if found:
                    yield cast(str, sentence)
                return
            found, sentence = detector.detect(character=character)
            if found:
                yield cast(str, sentence)
