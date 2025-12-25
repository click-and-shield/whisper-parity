# Usage:
# python3 -u -m unittest -v test_text_file_tool.py

import unittest
import os
import sys
import tempfile
from typing import cast

# Set the Python search path...
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
INPUT_PATH: str = os.path.join(tempfile.gettempdir(), 'needle.txt')
sys.path.insert(0, SEARCH_PATH)

from whisper import text_file_tool

def set_input_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

class TestFileTool(unittest.TestCase):

    def test_sentence_detection_1(self):
        inputs = ['Sentence1 is first.',
                  'Is sentence2 second ?',
                  'Sentence3 is next ...',
                  "Test's is processed.",
                  'This is a unit-test.']
        text = ' '.join(inputs)
        detector = text_file_tool.SentenceDetector()
        sentences: list[str] = []
        for c in text:
            found, sentence = detector.detect(character=c)
            if found:
                sentences.append(cast(str, sentence))
        found, sentence = detector.detect(character=None, last=True)
        if found:
            sentences.append(cast(str, sentence))
        self.assertEqual(len(sentences), len(inputs))
        for i in range(len(sentences)):
            self.assertEqual(sentences[i], inputs[i].strip(' '))

    def test_sentence_detection_2(self):
        inputs = ['Sentence1 is first\n',
                  'Is sentence2 second ?',
                  'Sentence3 is next\n\n',
                  "Test's is processed.",
                  'Sentence3 is next\n\n',
                  "Test's is processed..."]
        text = ' '.join(inputs)
        detector = text_file_tool.SentenceDetector()
        sentences: list[str] = []
        for c in text:
            found, sentence = detector.detect(character=c)
            if found:
                sentences.append(cast(str, sentence))
        found, sentence = detector.detect(character=None, last=True)
        if found:
            sentences.append(cast(str, sentence))
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], 'Sentence1 is first Is sentence2 second ?')
        self.assertEqual(sentences[1], "Sentence3 is next Test's is processed.")
        self.assertEqual(sentences[2], "Sentence3 is next Test's is processed...")

    def test_read_sentences_from_sting_1(self):
        inputs = ['Sentence1 is first.',
                  'Is sentence2 second ?',
                  'Sentence3 is next ...',
                  "Test's is processed.",
                  'This is a unit-test.']
        text = ' '.join(inputs)
        sentences: list[str] = []
        for s in text_file_tool.read_sentences_from_sting(text):
            sentences.append(s)
        self.assertEqual(len(sentences), len(inputs))
        for i in range(len(sentences)):
            self.assertEqual(sentences[i], inputs[i].strip(' '))

    def test_read_sentences_from_sting_2(self):
        inputs = ['Sentence1 is first\n',
                  'Is sentence2 second ?',
                  'Sentence3 is next\n\n',
                  "Test's is processed.",
                  'Sentence3 is next\n\n',
                  "Test's is processed..."]
        text = ' '.join(inputs)
        sentences: list[str] = []
        for s in text_file_tool.read_sentences_from_sting(text):
            sentences.append(s)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], 'Sentence1 is first Is sentence2 second ?')
        self.assertEqual(sentences[1], "Sentence3 is next Test's is processed.")
        self.assertEqual(sentences[2], "Sentence3 is next Test's is processed...")

    def test_extract_sentences_from_string(self):
        inputs = ['Sentence1 is first.',
                  'Is sentence2 second ?',
                  'Sentence3 is next ...',
                  "Test's is processed.",
                  'This is a unit-test.']
        text = ' '.join(inputs)
        sentences: list[str] = text_file_tool.extract_sentences_from_string(text)
        self.assertEqual(len(sentences), len(inputs))
        for i in range(len(sentences)):
            self.assertEqual(sentences[i], inputs[i].strip(' '))

    def test_read_lines_from_file_1(self):
        inputs = ['Sentence1 is first.',
                  'Is sentence2 second ?',
                  'Sentence3 is next ...',
                  "Test's is processed.",
                  'This is a unit-test.']
        set_input_file(INPUT_PATH, "\n".join(inputs))
        sentences: list[str] = []
        for sentence in text_file_tool.read_sentences_from_file(INPUT_PATH):
            sentences.append(sentence)
        self.assertEqual(len(sentences), len(inputs))
        for i in range(len(sentences)):
            self.assertEqual(sentences[i], inputs[i].strip(' '))

    def test_read_lines_from_file_2(self):
        inputs = ['Sentence1 is first.',
                  '',
                  'Is sentence2 second ?',
                  '',
                  'Sentence3 is next ...',
                  '',
                  "Test's is processed.",
                  '',
                  'This is a unit-test.',
                  '']
        set_input_file(INPUT_PATH, "\n".join(inputs))
        sentences: list[str] = []
        for sentence in text_file_tool.read_sentences_from_file(INPUT_PATH):
            sentences.append(sentence)
        self.assertEqual(len(sentences), int(len(inputs) / 2))
        for i in range(len(sentences)):
            self.assertEqual(sentences[i], inputs[i*2].strip(' '))

    # Need be fixed...
    def test_read_lines_from_file_3(self):
        inputs = ['Sentence1 is first\n',
                  'Is sentence2 second ?',
                  'Sentence3 is next\n\n',
                  "Test's is processed.",
                  'Sentence3 is next\n\n',
                  "Test's is processed..."]
        set_input_file(INPUT_PATH, "\n".join(inputs))
        sentences: list[str] = []
        for sentence in text_file_tool.read_sentences_from_file(INPUT_PATH):
            sentences.append(sentence)
        self.assertEqual(len(sentences), 3)
        self.assertEqual(sentences[0], 'Sentence1 is first Is sentence2 second ?')
        self.assertEqual(sentences[1], "Sentence3 is next Test's is processed.")
        self.assertEqual(sentences[2], "Sentence3 is next Test's is processed...")

if __name__ == '__main__':
    unittest.main()
