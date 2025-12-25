# Usage:
# python3 -m unittest -v test_sentence.py

import unittest
import os
import sys

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper import sentence

class TestOperations(unittest.TestCase):

    def test_split_1(self):
        inputs: list[str]=["This is a test.", "This is a test!", "This is a test?", " This  is  a  test ", "This, is a, test?", "This, is a, test ?"]
        for i in inputs:
            s: sentence.Sentence = sentence.Sentence(i)
            words: list[str] = s.get_words()
            self.assertEqual(len(words), 4)
            self.assertEqual(words[0], 'This')
            self.assertEqual(words[1], 'is')
            self.assertEqual(words[2], 'a')
            self.assertEqual(words[3], 'test')

    def test_split_2(self):
        input = "C'est l'aventure."
        s: sentence.Sentence = sentence.Sentence(input)
        words: list[str] = s.get_words()
        self.assertEqual(len(words), 2)
        self.assertEqual(words[0], "C'est")
        self.assertEqual(words[1], "l'aventure")


if __name__ == '__main__':
    unittest.main()
