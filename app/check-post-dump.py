# Usage:
#    python3 check-post-dump.py debug/haystack-post-processing.txt
#    python3 check-post-dump.py debug/haystack-post-processing.txt | grep -e "^E"
#    python3 check-post-dump.py debug/haystack-post-processing.txt | grep -e "^S"

from typing import Optional
import argparse
import os
import sys

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.sentence import Sentence


if __name__ == '__main__':

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Check a DEBUG file "haystack-post-processing.txt"')
    parser.add_argument('input',
                        type=str,
                        help='path to the file to check')
    args = parser.parse_args()
    input_path: str = args.input

    with open(input_path, 'r') as f:
        content: str = f.read()
    lines = content.split('\n')
    for line in lines:
        if line.strip() == '':
            continue
        fields = line.split('|')
        if len(fields) != 5:
            print('Invalid line: "{}"'.format(line))
        position: int = int(fields[0].strip())
        original_sentence: Sentence = Sentence(fields[1].strip())
        action: str = fields[2].strip()
        reformulation_index: Optional[int] = int(fields[3].strip()) if fields[3].strip() != '' else None
        reformulation: Sentence = Sentence(fields[4].strip())

        if 'N' == action:
            continue

        original_parity: int = 0 if len(original_sentence.get_words()) % 2 == 0 else 1
        reformulation_parity: int = 0 if len(reformulation.get_words()) % 2 == 0 else 1
        if original_parity == reformulation_parity:
            print('E {}'.format(line))
        else:
            print('S {}'.format(line))



