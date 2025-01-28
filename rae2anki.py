
from rae2json.rae2json.utils.words_utils import *
from create_csv import CSVCreator
import argparse
import subprocess
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-file", help="Input file with words and definitions")
    parser.add_argument("-e", "--exceptions-file", required=True, help="File with exceptions")
    parser.add_argument("-o", "--output-file", required=True, help="Output file")
    parser.add_argument("-x", "--extract-words", action="store_true", help="Extract words from input file. If false, the input file is considered to have the words already extracted.")
    parser.add_argument("-d", "--definitions-file", default="words.json", help="File with definitions")

    args = parser.parse_args()
    input_file = args.input_file
    exceptions_file = args.exceptions_file
    output_file = args.output_file
    extract_words = args.extract_words
    definitions_file = args.definitions_file

    if extract_words:
        command = ["scrapy", "crawl", "raespiderdefinitions", 
                   "-s", f"OUTPUT_FILE={os.path.abspath(definitions_file)}",
                   "-a", f"INPUT_FILE={os.path.abspath(input_file)}",
                   ]
        process = subprocess.Popen(command, text=True, cwd="rae2json")
        process.wait()

    definitions = read_definitions(definitions_file)
    csv_creator = CSVCreator(definitions, output_file)

    write_words(csv_creator.exception_words, exceptions_file)
    