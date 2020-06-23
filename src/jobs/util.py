import json
import os


def get_dictionary_from_json(input_json):
    with open(input_json, 'r') as file:
        json_contents = json.load(file)
    if 'dictionary' not in json_contents:
        raise Exception('Provided json file does not have a dictionary field.')
    return json_contents['dictionary']

def get_metadata(filename):
    abs_path = os.path.abspath(filename)
    folder = os.path.dirname(abs_path)
    with open(folder+'/metadata.json', 'r') as file:
        metadata = json.load(file)
    return metadata
