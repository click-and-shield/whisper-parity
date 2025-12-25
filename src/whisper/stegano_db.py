# Usage:
#   python3 ../src/whisper/stegano_db.py debug/stegano-db.sqlite debug/stegano-db.txt

from typing import Optional, List
import os
import sqlite3
from pathlib import Path
from dataclasses import dataclass

if __name__ == '__main__':
    import sys
    CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
    SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir))
    sys.path.insert(0, SEARCH_PATH)
    from whisper.sentence import Sentence
    from whisper.text_file_tool import read_sentences_from_file
    from whisper.rand_tools import RandTools
else:
    from .sentence import Sentence
    from .text_file_tool import read_sentences_from_file
    from .rand_tools import RandTools

@dataclass
class SentenceData:
    idx: int
    position: int
    sentence: Sentence
    prompt: Optional[str] = None
    reformulation: Optional[str] = None

class SteganoDb:

    def __init__(self, db_path: Optional[str] = None, init: bool = True):
        if db_path is None:
            db_path = 'file-db-' + RandTools.random_string(10) + '.sqlite'
        self.db_file_path: Path = Path(db_path)
        self.db = sqlite3.connect(db_path)
        if init:
            cursor = self.db.cursor()
            try:
                cursor.execute("""CREATE TABLE IF NOT EXISTS t ("idx" INTEGER PRIMARY KEY,
                                                                "position" INTEGER NOT NULL,
                                                                "sentence" TEXT NOT NULL,
                                                                "prompt" TEXT DEFAULT NULL,
                                                                "reformulation" TEXT DEFAULT NULL)""")
            finally:
                cursor.close()
        self.db.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()

    def close(self):
        self.db.close()
        self.db = None

    def destroy(self):
        if not self.db_file_path.exists():
            return
        self.db.close()
        try:
            os.remove(self.db_file_path)
        except PermissionError:
            print("Unable to remove file: " + str(self.db_file_path), flush=True)
        self.db = None

    def load_file(self, path: str) -> int:
        line_count: int = 0
        for sentence in read_sentences_from_file(path):
            self.add_sentence(sentence, line_count)
            line_count += 1
        return line_count

    def add_sentence(self, sentence: str, position: int):
        cursor = self.db.cursor()
        try:
            cursor.execute('INSERT INTO t("position", "sentence") VALUES (?, ?)', (position, sentence,))
        finally:
            cursor.close()
        self.db.commit()

    def get_sentence_by_position(self, position: int) -> SentenceData:
        cursor = self.db.cursor()
        try:
            row = cursor.execute('SELECT "idx", "position", "sentence", "prompt", "reformulation" FROM t WHERE "position"=?', (position,)).fetchone()
            if row is None:
                raise ValueError("Invalid position: {}".format(position))
        finally:
            cursor.close()
        return SentenceData(idx=row[0], position=row[1], sentence=Sentence(row[2]), prompt=row[3], reformulation=row[4])

    def get_number_of_sentences_to_reformulate(self) -> int:
        cursor = self.db.cursor()
        try:
            count: int = cursor.execute('SELECT COUNT(*) FROM t WHERE "prompt" IS NOT NULL').fetchone()[0]
        finally:
            cursor.close()
        return count

    def get_batch_of_sentences_to_reformulate(self, batch_size: int, offset: int) -> List[SentenceData]:
        sentences: List[SentenceData] = []
        cursor = self.db.cursor()
        try:
            rows = cursor.execute('SELECT "idx", "position", "sentence", "prompt", "reformulation" FROM t WHERE "prompt" IS NOT NULL ORDER BY "idx" LIMIT ?, ?', (offset, batch_size,)).fetchall()
            for row in rows:
                sentences.append(SentenceData(idx=row[0], position=row[1], sentence=Sentence(row[2]), prompt=row[3], reformulation=row[4]))
        finally:
            cursor.close()
        return sentences

    def set_prompt_by_position(self, position: int, prompt: Optional[str]):
        cursor = self.db.cursor()
        try:
            cursor.execute('UPDATE t SET "prompt"=? WHERE "position"=?', (prompt, position))
            if cursor.rowcount != 1:
                raise ValueError("Invalid position: {}".format(position))
        finally:
            cursor.close()
        self.db.commit()

    def set_reformulation_by_position(self, position: int, reformulation: str):
        cursor = self.db.cursor()
        try:
            cursor.execute('UPDATE t SET "reformulation"=? WHERE "position"=?', (reformulation, position))
            if cursor.rowcount != 1:
                raise ValueError("Invalid position: {}".format(position))
        finally:
            cursor.close()
        self.db.commit()

    def __len__(self) -> int:
        cursor = self.db.cursor()
        try:
            count: int = cursor.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        finally:
            cursor.close()
        return count

    def get_sentences_max_length(self) -> int:
        cursor = self.db.cursor()
        try:
            m: int = cursor.execute('SELECT max(length("sentence")) FROM t').fetchone()[0]
        finally:
            cursor.close()
        return m

    def get_prompt_max_length(self) -> int:
        cursor = self.db.cursor()
        try:
            m: int = cursor.execute('SELECT max(length("promp")) FROM t').fetchone()[0]
        finally:
            cursor.close()
        return m

    def get_reformulation_max_length(self) -> int:
        cursor = self.db.cursor()
        try:
            m: int = cursor.execute('SELECT max(length("reformulation")) FROM t').fetchone()[0]
        finally:
            cursor.close()
        return m

    def dump(self, path: str):
        max_sentence_length: int = self.get_sentences_max_length()
        max_reformulation_length: int = self.get_reformulation_max_length()
        cursor = self.db.cursor()
        counter: int = 0
        try:
            with open(path, 'w') as f:
                res = cursor.execute('SELECT "position", "sentence", "prompt", "reformulation" FROM t ORDER BY "position"')
                while True:
                    row = res.fetchone()
                    if row is None:
                        break
                    position: int = row[0]
                    sentence: str = row[1]
                    prompt: Optional[str] = row[2]
                    reformulation: Optional[str] = row[3]

                    if prompt is not None:
                        r: str = reformulation if reformulation is not None else ''
                        counter += 1
                        print('%-*d | %-*s | Y | %-*d | %-*s' % (5, position, max_sentence_length, sentence, 5, counter, max_reformulation_length, r), file=f)
                    else:
                        print('%-*d | %-*s | N | %-*s | %-*s' % (5, position, max_sentence_length, sentence, 5, ' ', max_reformulation_length, reformulation), file=f)
        finally:
            cursor.close()


if __name__ == '__main__':
    import argparse

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Dump a steganographic database')
    parser.add_argument('database',
                        type=str,
                        help='path to the database file')
    parser.add_argument('output',
                        type=str,
                        help='path to the output file')

    args = parser.parse_args()
    database_path: str = args.database
    output_path: str = args.output
    db = SteganoDb(db_path=database_path, init=False)
    print('Generating dump into "{}"'.format(output_path))
    db.dump(output_path)
