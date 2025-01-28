# rae2anki

## Description

`rae2anki` is a tool designed to download definitions from the Real Academia Española (RAE) and format the results into Anki flashcards. This project aims to help Pasapalabra (Spanish TV show) contestants to automatically generate flashcards with the definitions of the words that appear in the show.

## Features
- Download definitions from the RAE.
- Filter and process definitions.
- Format definitions into Anki flashcards.
- Support for synonyms.

## Requirements

- Python 3.9 or higher.
- Scrapy 2.9.0 or higher.

## Installation

1. Clone this repository:

    ```sh
    git clone https://github.com/USERNAME/rae2anki.git
    cd rae2anki
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

## Usage

In order to use `rae2anki`, you need to provide a list of words to search for. You can download the latest version in [ListadosPalabrasRAE](https://github.com/rubenperezm/ListadosPalabrasRAE). It is recommended to create a `data` directory to store all the files there.

Once you have downloaded the list, you can run the following command:

```sh
python3 rae2anki.py -i INPUT_FILE -e EXCEPTIONS_FILE -o OUTPUT_FILE -d DEFINITIONS_FILE -x
```

Where:
- `INPUT_FILE` is the path to the TXT file with list of words to search for. Ignored if `-x` is not present.
- `EXCEPTIONS_FILE` is the path to the TXT file that will contain the exceptions found while processing the words.
- `OUTPUT_FILE` is the path to the TXT file that will contain the flashcards in a CSV format.
- `DEFINITIONS_FILE` is the path to the JSON file that will contain the definitions of the words. If default, it will be `words.json`.
- `-x` is an optional flag that will enable the extraction of definitions. If you have already extracted the definitions and have the JSON file, you can skip this option.

### Example

Full process:
```sh
python3 rae2anki.py -i 23-8.txt -e exceptions.txt -o flashcards.csv -x
```

If you have already extracted the definitions:
```sh
python3 rae2anki.py -d words.json -e exceptions.txt -o flashcards.csv -d words.json
```
