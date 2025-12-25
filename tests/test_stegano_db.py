# Usage:
# python3 -m unittest -v test_stegano_db.py

from typing import Optional, List, Tuple
import unittest
import os
import sys
import tempfile

# Set the Python search path...
CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
INPUT_PATH: str = os.path.join(tempfile.gettempdir(), 'needle.txt')
sys.path.insert(0, SEARCH_PATH)

from whisper.stegano_db import SteganoDb, SentenceData

def set_input_file(path: str, content: str) -> None:
    with open(path, 'w') as f:
        f.write(content)

class TestSteganoDb(unittest.TestCase):

    def test_file_db(self):
        db_path = os.path.abspath(os.path.join(CURRENT_DIR, 'db.sqlite3'))
        inputs: List[Tuple[str, Optional[str], Optional[str]]] = [
            ("sentence1", "prompt1", None),
            ("sentence2", None, None),
        ]
        with SteganoDb(db_path) as file_db:
            for i in range(len(inputs)):
                file_db.add_sentence(inputs[i][0], i)
            self.assertEqual(len(file_db), len(inputs))
            for i in range(len(inputs)):
                sentence: SentenceData = file_db.get_sentence_by_position(i)
                self.assertEqual(sentence.position, i)
                self.assertEqual(str(sentence.sentence), inputs[i][0])
                self.assertIsNone(sentence.prompt)

            for i in range(len(inputs)):
                file_db.set_prompt_by_position(i, inputs[i][1])
            for i in range(len(inputs)):
                sentence: SentenceData = file_db.get_sentence_by_position(i)
                self.assertEqual(sentence.position, i)
                self.assertEqual(str(sentence.sentence), inputs[i][0])
                self.assertEqual(sentence.prompt, inputs[i][1])

            self.assertEqual(file_db.get_number_of_sentences_to_reformulate(), 1)

            reformulation: str = "reformulated sentence1"
            file_db.set_reformulation_by_position(0, reformulation)
            sentence: SentenceData = file_db.get_sentence_by_position(0)
            self.assertEqual(sentence.position, 0)
            self.assertEqual(sentence.reformulation, reformulation)
            self.assertIsNotNone(sentence.prompt)
            sentence: SentenceData = file_db.get_sentence_by_position(1)
            self.assertEqual(sentence.position, 1)
            self.assertIsNone(sentence.prompt)
            self.assertIsNone(sentence.reformulation)

    def test_load_file_1(self):
        input="""This is a test."""
        set_input_file(INPUT_PATH, input)
        with SteganoDb(None) as db:
            count = db.load_file(INPUT_PATH)
            self.assertEqual(count, 1)
            self.assertEqual(len(db), 1)
            sentence = db.get_sentence_by_position(0)
            self.assertEqual(sentence.position, 0)
            self.assertEqual(str(sentence.sentence), input)
            self.assertIsNone(sentence.prompt)
            self.assertIsNone(sentence.reformulation)

    def test_load_file_2(self):
        input: list[str] = ['This is a test.', 'And the rest...']
        set_input_file(INPUT_PATH, "\n".join(input))
        with SteganoDb(None) as db:
            count = db.load_file(INPUT_PATH)
            self.assertEqual(len(db), 2)
            self.assertEqual(count, 2)
            sentence0 = db.get_sentence_by_position(0)
            self.assertEqual(sentence0.position, 0)
            self.assertEqual(str(sentence0.sentence), 'This is a test.')
            self.assertIsNone(sentence0.prompt)
            self.assertIsNone(sentence0.reformulation)
            sentence1 = db.get_sentence_by_position(1)
            self.assertEqual(sentence1.position, 1)
            self.assertEqual(str(sentence1.sentence), 'And the rest...')
            self.assertIsNone(sentence1.prompt)
            self.assertIsNone(sentence1.reformulation)

    def test_load_file_3(self):
        input: list[str] = ['This is a test.', '.']
        set_input_file(INPUT_PATH, "\n".join(input))
        with SteganoDb(None) as db:
            self.assertRaises(ValueError, db.load_file, INPUT_PATH)

    def test_load_file_4(self):
        input: list[str] = ['This is a test..', '.']
        set_input_file(INPUT_PATH, "\n".join(input))
        with SteganoDb(None) as db:
            count = db.load_file(INPUT_PATH)
            self.assertEqual(len(db), 1)
            self.assertEqual(count, 1)
            sentence0 = db.get_sentence_by_position(0)
            self.assertEqual(sentence0.position, 0)
            self.assertEqual(str(sentence0.sentence), 'This is a test...')
            self.assertIsNone(sentence0.prompt)
            self.assertIsNone(sentence0.reformulation)

    def test_load_file_5(self):
        input: list[str] = ['This is a test! This is a second line. Is this a third line ? The response is... Yes']
        set_input_file(INPUT_PATH, "\n".join(input))
        with SteganoDb(None) as db:
            count = db.load_file(INPUT_PATH)
            self.assertEqual(len(db), 5)
            self.assertEqual(count, 5)
            sentence = db.get_sentence_by_position(0)
            self.assertEqual(sentence.position, 0)
            self.assertEqual(str(sentence.sentence), 'This is a test!')
            self.assertIsNone(sentence.prompt)
            self.assertIsNone(sentence.reformulation)
            sentence = db.get_sentence_by_position(1)
            self.assertEqual(sentence.position, 1)
            self.assertEqual(str(sentence.sentence), 'This is a second line.')
            self.assertIsNone(sentence.prompt)
            self.assertIsNone(sentence.reformulation)
            sentence = db.get_sentence_by_position(2)
            self.assertEqual(sentence.position, 2)
            self.assertEqual(str(sentence.sentence), 'Is this a third line ?')
            self.assertIsNone(sentence.prompt)
            self.assertIsNone(sentence.reformulation)
            sentence = db.get_sentence_by_position(3)
            self.assertEqual(sentence.position, 3)
            self.assertEqual(str(sentence.sentence), 'The response is...')
            self.assertIsNone(sentence.prompt)
            self.assertIsNone(sentence.reformulation)
            sentence = db.get_sentence_by_position(4)
            self.assertEqual(sentence.position, 4)
            self.assertEqual(str(sentence.sentence), 'Yes')
            self.assertIsNone(sentence.prompt)
            self.assertIsNone(sentence.reformulation)



if __name__ == '__main__':
    unittest.main()
