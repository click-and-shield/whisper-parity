# Usage:
#   python3 -u chat-gpt-tester.py --token="/home/dev/.token" ../test-data/messages.json

from typing import Union
import argparse
from pathlib import Path
import sys
import os
import json
from openai.types.chat import ChatCompletion

CURRENT_DIR=os.path.dirname(os.path.abspath(__file__))
SEARCH_PATH=os.path.abspath(os.path.join(CURRENT_DIR, os.path.pardir, 'src'))
sys.path.insert(0, SEARCH_PATH)

from whisper.chat_gpt import ChatGPT
from whisper.api_tools import load_token

if __name__ == '__main__':
    script_dir: Path = Path(CURRENT_DIR)
    default_tokens_path: str = script_dir.joinpath(".token").__str__()
    default_model: str = 'gpt-5.1'

    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Send a request to the ChatGPT API.')
    parser.add_argument('--model',
                        dest='model',
                        type=str,
                        required=False,
                        default=default_model,
                        help='name of the model to use (ex: "gpt-5.1", "gpt-4.1", "gpt-4.1-mini"...) - default: "{}"'.format(default_model))
    parser.add_argument('--token',
                        dest='token',
                        type=str,
                        required=False,
                        default=default_tokens_path,
                        help='path to the file containing the token to use for ChatGPT API (default: "{}")'.format(default_tokens_path))
    parser.add_argument('input',
                        type=str,
                        help='path to the input file')

    args = parser.parse_args()
    model: str = args.model
    token_path: str = args.token
    input_path: str = args.input

    # Load the API token and create the ChatGPT client
    token: str = load_token(token_path)
    client: ChatGPT = ChatGPT(model, token)

    # Load the JSON file
    with open(input_path, 'r') as f:
        input_json = f.read()

    # Send the request and print the response
    messages: list[dict[str, str]] = json.loads(input_json.strip())
    response: str = client.call(messages)
    print(response)

