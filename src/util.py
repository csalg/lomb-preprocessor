import os
import chardet

from config import LANGUAGES_MAP, LANGUAGES
from logging_ import logger




def infer_language(language):
    language = language.lower()
    if language in LANGUAGES:
        return language
    if language in LANGUAGES_MAP:
        return LANGUAGES_MAP[language]
    raise Exception(f"Could not infer language from '{language}'")

def parse_title_source_language_and_extension_from_filename(filename):
    title_and_source_language, extension = os.path.splitext(filename)
    title, source_language = os.path.splitext(title_and_source_language)
    return title, source_language[1:], extension[1:]

def convert_to_utf8(filename):
    logger.debug('Detecting character set.')
    with open(filename, 'rb') as file:
        raw_bytes = file.read()
    detected_character_set = chardet.detect(raw_bytes)
    logger.debug(f'Character set is {detected_character_set["encoding"]}.')
    if detected_character_set['encoding'] == 'utf-8':
        logger.debug("Skipping character set conversion.")
        return
    try:
        text_as_string = raw_bytes.decode(detected_character_set['encoding'])
    except:
        return

    with open(filename+'.bak', 'wb') as file:
        file.write(raw_bytes)
    
    with open(filename, 'w') as file:
        file.write(text_as_string)

def get_rid_of_empty_lines_after_time_in_vtt(filename):
    pass

# Print iterations progress
def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    From https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

class LombPreprocessorException(Exception):
    pass