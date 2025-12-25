# Whisper parity

## Introduction

This project explores the intersection of Large Language Models (LLMs) and steganography.

It implements a straightforward algorithm designed to conceal a secret message, referred to as the **needle**, within a larger body of text known as the **haystack**. The resulting output, seamlessly weaving the needle into the haystack, is distinctively named the **murmur**.

## Limitations

This project is a proof of concept and currently has known limitations. Most notably, the algorithms used to segment text into sentences—and sentences into words—lack robustness. Consequently, the scripts are best suited for "simple texts" acting as "haystacks."

For instance, the following text cannot be correctly split into sentences:

> When on board H.M.S. ‘Beagle,’ as naturalist, I was much struck with certain facts in the distribution of the inhabitants of South America, and in the geological relations of the present to the past inhabitants of that continent. These facts seemed to me to throw some light on the origin of species—that mystery of mysteries, as it has been called by one of our greatest philosophers. On my return home, it occurred to me, in 1837, that something might perhaps be made out on this question by patiently accumulating and reflecting on all sorts of facts which could possibly have any bearing on it. After five years’ work I allowed myself to speculate on the subject, and drew up some short notes; these I enlarged in 1844 into a sketch of the conclusions, which then seemed to me probable: from that period to the present day I have steadily pursued the same object. I hope that I may be excused for entering on these personal details, as I give them to show that I have not been hasty in coming to a decision.

The current algorithm identifies a sentence boundary strictly by the presence of a period (`.`), a question mark (`?`), an exclamation mark (`!`), or an ellipsis (`...`). The issue with processing the text above becomes immediately apparent given these constraints.

## How it works

### Overview

The algorithm employed to conceal the needle within the haystack is straightforward:

1. **Binary Conversion**: The needle is first converted into its binary representation (a sequence of bits).
2. **Sentence Reformulation**: For each bit of the needle, the corresponding sentence in the haystack is adjusted:
    - **Bit 0**: Matches a sentence with an **even** number of words. If the sentence has an odd word count, the LLM is prompted to rephrase it to achieve an even count.
    - **Bit 1**: Matches a sentence with an **odd** number of words. If the sentence has an even word count, the LLM is prompted to rephrase it to achieve an odd count.

> **Note**: The haystack must contain at least as many sentences as there are bits in the needle's binary representation.

### Details description

Let's take an example:
* **needle**: "`Hello World!`"
* **haystack**: [test-data/haystack.txt](test-data/haystack.txt)

#### Conversion of the needle into a binary representation

First, we convert the needle is converted into a binary representation:

```
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1
```

The 64 first bits of the binary representation represent the length, in bytes, of the needle.

```
0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0
```

The length of the needle is: `2^0*0 + 2^1*0 + 2^2*1 + 2^3*1 = 12 bytes`.

> Indeed, the string of characters "Hello World!" is 12 bytes long.
 
Then, the remaining (`12*8 = 96`) bits of the binary representation represent the needle itself.

| *byte*  | *binary representation*  | *char* |
|---------|--------------------------|--------|    
| byte 8  | [0, 1, 0, 0, 1, 0, 0, 0] | 'H'    |
| byte 9  | [0, 1, 1, 0, 0, 1, 0, 1] | 'e'    |
| byte 10 | [0, 1, 1, 0, 1, 1, 0, 0] | 'l'    |
| byte 11 | [0, 1, 1, 0, 1, 1, 0, 0] | 'l'    |
| byte 12 | [0, 1, 1, 0, 1, 1, 1, 1] | 'o'    |
| byte 13 | [0, 0, 1, 0, 0, 0, 0, 0] | ' '    |
| byte 14 | [0, 1, 0, 1, 0, 1, 1, 1] | 'W'    |
| byte 15 | [0, 1, 1, 0, 1, 1, 1, 1] | 'o'    |
| byte 16 | [0, 1, 1, 1, 0, 0, 1, 0] | 'r'    |
| byte 17 | [0, 1, 1, 0, 1, 1, 0, 0] | 'l'    |
| byte 18 | [0, 1, 1, 0, 0, 1, 0, 0] | 'd'    |
| byte 19 | [0, 0, 1, 0, 0, 0, 0, 1] | '!'    |

#### Reformulation of the haystack sentences

- **Step 1:** Pair the first bit of the needle with the associated haystack sentence.
    - **Bit:** `0`
    - **Sentence:** `The car moves forward slowly.`
      *Action:* The sentence has an odd word count. We instruct the LLM to reformulate it into an even-length sentence.
      *Result:* `The automobile proceeds ahead, moving slowly.`

- **Step 2:** Pair the second bit with the next sentence.
    - **Bit:** `0`
    - **Sentence:** `The engine runs well.`
      *Action:* The sentence already meets the length criteria. No change is required.

- **Continue:** Repeat this loop until the last bit of the needle has been processed.


This document shows the entire process: [haystack-post-processing-8.txt](doc/example1/haystack-post-processing-8.txt) 

> - The first column represents the position of the bit in the needle
> - The second column represents the associated sentence from the haystack.
> - The third column tells whether the sentence needs to be reformulated or not (`Y`: "Yes", `N`: "No"). 
> - The fourth column represents a counter that count the number of requests that will be sent to the LLM.
> - The fifth column represents the response received from the LLM (the reformulated sentence).

#### Important note

As you may know, LLMs are non-deterministic systems (unless the temperature is set to 0) and are prone to errors. You might observe this behavior when running the example above.

The script implementing the algorithm outlined earlier verifies the LLM's output against specific criteria:
- If the input sentence has an odd word count, the script validates that the reformulated response also contains an odd number of words.
- Conversely, if the input sentence has an even word count, it ensures the response follows suit.

We observe that the LLM occasionally yields incorrect responses. Whenever an invalid reformulation is detected, the script automatically prompts the LLM to retry those specific sentences.

The list below details the LLM's responses at each stage of this error correction process:
 
- [pass 1](doc/example1/haystack-post-processing-0.txt)
- [pass 2](doc/example1/haystack-post-processing-1.txt)
- [pass 3](doc/example1/haystack-post-processing-2.txt)
- [pass 4](doc/example1/haystack-post-processing-3.txt)
- [pass 5](doc/example1/haystack-post-processing-4.txt)
- [pass 6](doc/example1/haystack-post-processing-5.txt)
- [pass 7](doc/example1/haystack-post-processing-6.txt)
- [pass 8](doc/example1/haystack-post-processing-7.txt)
- [pass 9](doc/example1/haystack-post-processing-8.txt)

## Run the example

### Requirements

You need:
- Python 3.10.12 or higher.
- A [OpenAI API key](https://platform.openai.com/account/api-keys).
- [pipenv](https://pipenv.pypa.io/en/latest/) (`pip install --user pipenv`)

### Prepare the environment

- Create a virtual environment: `python -m venv .venv`
- Activate the virtual environment:
    * linux: `source .venv/bin/activate`
    * windows: `.venv\Scripts\activate.bat`
- Install the dependencies: `pip install -e .`.
- Verify that everything is working fine: `python -m unittest discover tests/`

> *Note*:
> - Create the file "requirements.txt": `pip freeze > requirements.txt`

### Run the scripts

*Hide the needle in the haystack:*

```
cd app
python3 -u hide.py --debug --verbose --token="/home/dev/.token" ../test-data/needle.txt ../test-data/haystack.txt murmur.txt
```

> - The file `/home/dev/.token` contains your OpenAI API key.
> - The file `../test-data/needle.txt` contains the text that you want to hide (that is: the needle).
> - The file `../test-data/haystack.txt` contains the text that will be used to hide the needle (that is: the haystack).
> - The file `murmur.txt` will contain the resulting murmur.

- needle: [needle.txt](test-data/needle.txt)
- haystack: [haystack](test-data/haystack.txt)
- murmur: [murmur.txt](test-data/murmur.txt)

*Reveal the needle from the murmur:*

```
cd app
python3 -u reveal.py --verbose ../test-data/murmur.txt message.txt
```

> - The file `../test-data/murmur.txt` contains the message that you want to reveal (that is: the murmur).
> - The file `message.txt` will contain the resulting message.
