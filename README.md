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

1. Run the Scrapy spider to download definitions from the RAE:

    ```sh
    scrapy crawl raespiderdefinitions -s OUTPUT_FILE=output/words.json
    ```

    Note that the file and the path should exist before running the spider.

2. Process the definitions and generate Anki flashcards:

    ```sh
    python rae2anki.py
    ```
