import re

def convert_to_key(chunk):
    return chunk.replace('\n', ' ').replace('   ', ' ').replace('  ', ' ')

def format_caption(text):
    if len(text)<=30:
        return text
    
    i = int(len(text)/2)

    while text[i] != ' ' and i!=0:
        i -= 1
    
    return f'{text[:i]}\n{text[i+1:]}'

regex_that_breaks_into_chunks = re.compile("([;\?\.!\n])")
def text_to_chunks(text):
    global regex_that_breaks_into_chunks
    splits = regex_that_breaks_into_chunks.split(text)
    previous_split = ''
    splits_merged = []
    for split in splits:
        if len(split) <= 1:
            previous_split += split
        else:
            splits_merged.append(previous_split)
            previous_split = split
    splits_merged.append(previous_split)

    return splits_merged


