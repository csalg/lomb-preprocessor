#! /usr/bin/python3
import argparse
import os
import sys

from jobs.LocalTranslationJob import run_local_translation_job_from_filename
from logging_ import logger


def parse_arguments():
    argument_parser = argparse.ArgumentParser(prog="DeepL Translator",
                                              description="Translate files using DeepL")

    argument_parser.add_argument('-t', '--target', help="Language code for the target language.", required=True)
    argument_parser.add_argument('-s', '--source',
                                 help="Language code for the source language. if not provided will be inferred from file.")
    argument_parser.add_argument('-j', '--json', help="Previous json file to reuse dictionary.")
    argument_parser.add_argument('-p', '--package', help='Package text files as book chapters', action='store_true')

    argument_parser.add_argument(
        'files',
        nargs="+",
        metavar='file',
        type=str,
        help="Files to translate",
    )

    return argument_parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    filenames = "\n\n" + "\n".join(args.files) + "\n"
    logger.info(f'The following files will be processed: {filenames}')

    if args.source is None:
        logger.info("Source language was not provided. The program will attempt to parse it from the filename \n")

    for filename in args.files:
        run_local_translation_job_from_filename(args.source, args.target, filename, args.json)
