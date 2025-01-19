
from rae2json.rae2json.utils.words_utils import *
from create_csv import CSVCreator
import argparse


if __name__ == "__main__":
    #words = read_words("data/23-8.txt")
    # words = clean_words(words)
    # write_words(words, "data/23-7-clean.txt")

    # run command scrapy crawl raespiderdefinitions   -s OUTPUT_FILE=words.json

    # read input file from command line
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input-file", help="Input file with words and definitions")
    parser.add_argument("-e", "--exceptions-file", help="File with exceptions")

    input_file = parser.parse_args().input_file
    exceptions_file = parser.parse_args().exceptions_file

    definitions = read_definitions(input_file)
    csv_creator = CSVCreator(definitions)

    write_words(csv_creator.exception_words, exceptions_file)

    # for m in CSVCreator.merged_definitions.values():
    #     print(m)
    