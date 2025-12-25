import json
import re

from typing import Optional, cast, Tuple, Union
from pathlib import Path
from dataclasses import dataclass

from .conversion import Conversion
from .types import Vector
from .message import Message
from .prompt_builder import PromptBuilder
from .stegano_db import SteganoDb, SentenceData
from .llm import calculate_tokens
from .disk_list import DiskList
from .request_data import RequestData
from .chat_gpt import ChatGPT
from .sentence import Sentence
from .text_file_tool import read_sentences_from_file
from whisper import Bit, Int64


PROMPTS_PER_REQUEST: int = 50
PROMPT_HIDE_SYSTEM = "Tu es un assistant expert en stéganographie textuelle."
PROMPT_HIDE_ASSISTANT = "Le style doit rester naturel, discret et humain. Un mot est toute séquence de lettres, de chiffres, d'apostrophes ou de traits d'union, séparée par un espace."
PROMPT_HIDE_USER = 'Reformule, en anglais, la phrase suivante pour générer une phrase contenant un nombre **{PARITY}** de mots : "{SENTENCE}"'
PROMPT_HIDE_LAST_USER = """Réponds STRICTEMENT en JSON valide.  
Utilise ce format exact et rien d'autre :

{
  "results": ["...", "...", "..."]
}

Le tableau "results" doit contenir N éléments, dans le même ordre que les messages ayant la structure : "Reformule … : <texte>".

Aucun texte en-dehors du JSON.  
Pas de commentaire.  
Pas de préface.  
Pas d’explication.
"""


@dataclass
class HiderConfiguration:
    model: str
    token: str
    debug_path: Optional[Path] = None
    verbose: bool = False
    dry_run: bool = False


class Hider:

    def __init__(self, needle: str, haystack: str, murmur: str, config: HiderConfiguration) -> None:
        """
        Hide a text file (called the "needle") into another text file (called the "haystack").
        The resulting text file is called the "murmur".

        :param needle: The message to hide.
        :param haystack: The message used to hide the needle.
        :param murmur: The generated message that hides the needle.
        :param config: The options used to control the behavior of the hider.
                        - model: the LLM model to use.
                        - token: the token used to authenticate the request to the LLM.
                        - debug_path: the path to the directory where debug files will be written.
                        - verbose: activate verbose mode.
                        - dry_run: if True, the hider will not call the LLM, but will instead generate debug files.
        """
        self.needle: str = needle
        self.haystack: str = haystack
        self.murmur: str = murmur
        self.options: HiderConfiguration = config
        self.current_line: int = 0
        # Initialize the paths to the databases
        if config.debug_path is not None:
            stegano_db_path = config.debug_path.joinpath('stegano-db.sqlite')
            requests_db_path = config.debug_path.joinpath('requests-db.sqlite')
        else:
            stegano_db_path = None
            requests_db_path = None
        # Create the database used to store the requests to the LLM
        self.requests_db: DiskList = DiskList(requests_db_path.__str__())
        # Load the text used to hide the needle (the haystack) as a series of lines
        self.stegano_db: SteganoDb = SteganoDb(stegano_db_path.__str__())
        self.line_count = self.stegano_db.load_file(haystack)
        # Load the message to hide (the needle) as a series of bits
        self.message_bits: Vector = Message.load_text_file_as_vector(needle)
        self.chat_gpt_client = ChatGPT(config.model, config.token)
        self.call_count: int = 0
        self.create_requests_count: int = 0

        if config.verbose:
            print("Hiding text file '{}' into '{}'".format(self.needle, self.haystack))
            print('- needle (to be hidden):       {}'.format(self.needle))
            print('- haystack (the hiding place): {}'.format(self.haystack))
            print('- murmur:                      {}'.format(self.murmur))
            print('- model:                       {}'.format(config.model))
            print('- debug path:                  {}'.format(config.debug_path if config.debug_path is not None else ''))
            print('- dry run:                     {}'.format(config.dry_run))
            print('- needle bits count:           {}'.format(len(self.message_bits)))
            print('- haystack lines count:        {}\n'.format(self.line_count))
        if len(self.message_bits) > self.line_count:
            raise ValueError("The haystack is not wide enough to conceal the needle! It should contain at least {} sentences!".format(len(self.message_bits)))

    def destroy(self):
        self.stegano_db.destroy()
        self.requests_db.destroy()

    @staticmethod
    def keep_phrase(response: str) -> str:
        matches = re.findall(r'[^.?!]*[.?!]', response)
        if matches:
            return matches[-1].strip()
        else:
            return response.strip()

    def dump_stegano_db_pre_process_to_file(self) -> None:
        """Dump the stegano database before the LLM is called for debugging purposes."""
        if self.options.debug_path is None:
            return
        debug_path = self.options.debug_path.joinpath('haystack-pre-processing.txt')
        self.stegano_db.dump(str(debug_path))

    def dump_stegano_db_post_process_to_file(self) -> None:
        """Dump the stegano database after the LLM has been called for debugging purposes."""
        if self.options.debug_path is None:
            return
        debug_path = self.options.debug_path.joinpath('haystack-post-processing-{}.txt'.format(self.call_count))
        self.stegano_db.dump(str(debug_path))

    def create_prompts(self) -> None:
        """
        Create the prompts to call the LLM.
        """
        prompter: PromptBuilder = PromptBuilder(PROMPT_HIDE_USER)

        position = 0
        # Process the lines that are used to hide the needle
        for bit in self.message_bits:
            # Extract the next line from the message and convert it into a Sentence object
            sentence_data: SentenceData = self.stegano_db.get_sentence_by_position(position)
            words: list[str] = sentence_data.sentence.get_words()
            # Hide the current bit of the message into the current line
            if len(words) % 2 == bit:
                self.stegano_db.set_reformulation_by_position(sentence_data.position, str(sentence_data.sentence))
            else:
                prompt: str = prompter.generate_prompt({'PARITY': "pair" if bit == 0 else "impair", 'SENTENCE': str(sentence_data.sentence)})
                self.stegano_db.set_prompt_by_position(sentence_data.position, prompt)
            position += 1

        # Process the extra lines of that haystack
        for p in range(position, len(self.stegano_db)):
            sentence_data: SentenceData = self.stegano_db.get_sentence_by_position(p)
            self.stegano_db.set_reformulation_by_position(p, str(sentence_data.sentence))
        self.dump_stegano_db_pre_process_to_file()

    def dump_requests_to_file(self) -> None:
        """Dump all requests to disk for debugging purposes."""
        if self.options.debug_path is None:
            return
        for i in range(len(self.requests_db)):
            debug_path = self.options.debug_path.joinpath('request-{}.txt'.format(self.create_requests_count))
            self.create_requests_count += 1
            request_data: RequestData = RequestData.from_json(self.requests_db[i])
            r: str = request_data.messages_to_json()
            with open(debug_path, "w") as fd_debug:
                tokens_count: int = calculate_tokens(r)
                fd_debug.write("tokens count: {}\n".format(tokens_count))
                fd_debug.write("positions:    {}\n".format(json.dumps(request_data.positions)))
                fd_debug.write("request:\n\n{}\n".format(r))

    @staticmethod
    def create_requests_batch(sentences_data: list[SentenceData]) -> RequestData:
        """Create a request for the LLM containing the specified number of lines starting at the specified offset."""
        positions: list[int] = []
        messages: list[dict[str, str]] = [
            {"role": "system", "content": PROMPT_HIDE_SYSTEM},
            {"role": "assistant", "content": PROMPT_HIDE_ASSISTANT}
        ]
        for sentence_data in sentences_data:
            positions.append(sentence_data.position)
            messages.append({"role": "user", "content": cast(str, sentence_data.prompt)})
        messages.append({"role": "user", "content": PROMPT_HIDE_LAST_USER})
        data: dict[str, Union[list[int], list[dict[str, str]]]] = {
            'positions': positions,
            'messages': messages
        }
        return RequestData.from_dict(data)

    def create_requests(self) -> None:
        """Create the requests to call the LLM."""

        # Get the number of sentences that need to be reformulated
        total_count: int = self.stegano_db.get_number_of_sentences_to_reformulate()
        full_batch_count: int = total_count // PROMPTS_PER_REQUEST
        batch_reminder: int = total_count % PROMPTS_PER_REQUEST
        if self.options.verbose:
            print("Creating requests:")
            print('- Number of lines to reformulate: {}'.format(total_count))
            print('- Size of one batch:              {}'.format(PROMPTS_PER_REQUEST))
            print('- Number of full batches:         {}'.format(full_batch_count))
            print('- Reminders:                      {}\n'.format(batch_reminder))
        # Create the requests
        for b in range(full_batch_count):
            sentences_data: list[SentenceData] = self.stegano_db.get_batch_of_sentences_to_reformulate(PROMPTS_PER_REQUEST, b * PROMPTS_PER_REQUEST)
            self.requests_db.append(Hider.create_requests_batch(sentences_data).to_json())
        sentences_data: list[SentenceData] = self.stegano_db.get_batch_of_sentences_to_reformulate(batch_reminder, full_batch_count * PROMPTS_PER_REQUEST)
        self.requests_db.append(Hider.create_requests_batch(sentences_data).to_json())
        self.dump_requests_to_file()

    def dump_llm_response_to_file(self, response: str, request_index: int) -> None:
        """Dump the LLM response to disk for debugging purposes."""
        if self.options.debug_path is None:
            return
        debug_path = self.options.debug_path.joinpath('llm-response-call:{}-req:{}.txt'.format(self.call_count, request_index))
        with open(debug_path, "w") as fd_debug:
            fd_debug.write(response)

    def call_llm(self) -> None:
        """Call the LLM for each request and extract the reformulated sentences from the response."""
        for i in range(len(self.requests_db)):
            # Call the LLM and get the response
            request: dict[str, Union[list[int], list[dict[str, str]]]] = RequestData.from_json(self.requests_db[i]).to_dict()
            messages: list[dict[str, str]] = cast(list[dict[str, str]], request['messages'])
            try:
                response: str = self.chat_gpt_client.call(messages)
            except Exception as e:
                raise RuntimeError("Error calling the LLM: {}".format(str(e)))
            self.dump_llm_response_to_file(response, i)

            # Extract the reformulated sentences from the LLM response
            positions: list[int] = cast(list[int], request['positions'])
            sentences: list[str] = json.loads(response)['results']

            # sentences: list[str] = json.loads(response)['results']
            if len(sentences) != len(positions):
                raise ValueError("Invalid response from the LLM: expected {} sentences, got {} [call:{}, req:{}]\n\n{}\n\n".format(len(positions), len(sentences), self.call_count, i, response))
            for p, s in zip(positions, sentences):
                s = s if s.endswith(".") else s + "."
                self.stegano_db.set_reformulation_by_position(p, s)
        self.dump_stegano_db_post_process_to_file()
        self.call_count += 1

    def check_responses(self) -> list[SentenceData]:
        to_replay: list[SentenceData] = []

        # Build the list of sentences that need to be reformulated again
        for i in range(len(self.stegano_db)):
            sentence_data: SentenceData = self.stegano_db.get_sentence_by_position(i)
            if sentence_data.prompt is None:
                continue
            original_sentence = Sentence(sentence_data.sentence.string)
            reformulated_sentence = Sentence(cast(str, sentence_data.reformulation))
            if (len(original_sentence.get_words()) % 2) == (len(reformulated_sentence.get_words()) % 2):
                print("WARNING: parity for #{} has not been modified! {} [{}/{}]".format(i, original_sentence.string, len(original_sentence.get_words()), len(reformulated_sentence.get_words())))
                to_replay.append(sentence_data)
        return to_replay

    def write_murmur(self):
        with open(self.murmur, "w") as fd_murmur:
            for i in range(len(self.stegano_db)):
                sentence_data: SentenceData = self.stegano_db.get_sentence_by_position(i)
                if sentence_data.reformulation is None:
                    print("WARNING: missing reformulation for sentence #{}".format(i))
                fd_murmur.write(cast(str, sentence_data.reformulation) + "\n")


    def hide(self) -> None:

        # Generate the prompts to call the LLM
        self.create_prompts()

        # Generate the requests to call the LLM
        self.create_requests()
        if self.options.dry_run:
            return

        # Send requests to the LLM
        self.call_llm()
        errors: list[SentenceData] = self.check_responses()
        if len(errors) > 0:
            while True:
                print('LLM made {} errors, retrying...'.format(len(errors)), flush=True)
                request_data: RequestData = Hider.create_requests_batch(errors)
                self.requests_db.reset()
                self.requests_db.append(request_data.to_json())
                self.dump_requests_to_file()
                self.call_llm()
                errors: list[SentenceData] = self.check_responses()
                self.dump_stegano_db_post_process_to_file()
                if len(errors) == 0:
                    break

        # Generate the final murmur
        self.write_murmur()

class Revealer:

    def __init__(self, murmur: str, reveal_path: str, verbose: bool = False) -> None:
        self.murmur: str = murmur
        self.reveal_path: str = reveal_path
        self.verbose: bool = verbose

    @staticmethod
    def load_text_file_as_sentences(path: str) -> DiskList:
        sentences: DiskList = DiskList()
        for sentence in read_sentences_from_file(path):
            sentences.append(sentence)
        return sentences

    def reveal(self) -> None:
        # Load the murmur into a series of lines
        murmur_db: DiskList = Revealer.load_text_file_as_sentences(self.murmur)

        try:
            # Create a vector of bits.
            bits: list[Bit] = []
            for line in murmur_db:
                sentence: Sentence = Sentence(line)
                parity: int = 0 if len(sentence.get_words()) % 2 == 0 else 1
                bits.append(cast(Bit, parity))

            # Make sure that the number of bits is greater than 64.
            if len(bits) < 64:
                raise ValueError("The murmur must contain at least 64 sentences!")
            length_vector: list[Bit] = bits[:64]
            length: Int64 = Conversion.bit_list_to_int64(length_vector)
            body_vector: list[Bit] = bits[64:64+length*8]
            body = Conversion.bit_list_to_bytes(body_vector)
            if self.verbose:
                print("Data: {}".format(bits))
                print("length vector: {}".format(length_vector))
                print("length: {} (characters) => {} bits".format(length, length*8))
                print("body: {}".format(body_vector))
                print('Message: "{}"'.format(self.reveal_path))
            with open(self.reveal_path, 'w') as f:
                f.write(str(body, 'ascii'))
        finally:
            murmur_db.destroy()
