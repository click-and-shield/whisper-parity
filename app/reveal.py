# Usage:
#   python3 -u reveal.py --verbose ../test-data/murmur.txt message.txt

import argparse
import sys
import os

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.whisperer import Revealer


if __name__ == '__main__':

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Reveal a text file hidden within another text file')
    parser.add_argument('--verbose',
                        dest='verbose_flag',
                        action='store_true',
                        help='activate verbose output')
    parser.add_argument('murmur',
                        type=str,
                        help='path to the text file used as hiding place')
    parser.add_argument('output',
                        type=str,
                        help='path to the output file')

    args = parser.parse_args()
    verbose_flag: bool = args.verbose_flag
    murmur_path: str = args.murmur
    output_path: str = args.output

    revealer = Revealer(murmur_path, output_path, verbose_flag)
    revealer.reveal()

