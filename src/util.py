import os
import chardet

def parse_title_source_language_and_extension_from_filename(filename):
    title_and_source_language, extension = os.path.splitext(filename)
    title, source_language = os.path.splitext(title_and_source_language)
    return title, source_language[1:], extension[1:]

def convert_to_utf8(filename):
    with open(filename, 'rb') as file:
        raw_bytes = file.read()
    detected_character_set = chardet.detect(raw_bytes)
    print(detected_character_set)
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
