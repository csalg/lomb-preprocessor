import json

from .SerializerABC import SerializerABC
from serial.util import text_to_chunks

class TextPackageSerializer(SerializerABC):
    def __init__(self, metadata, filenames):
        self.metadata = metadata

        self.chapters_in_chunks = []
        self.populate_chapters_in_chunks_from_book(filenames)

        self.chunks_dictionary = {}
        self.populate_chunks_dictionary()

    def populate_chapters_in_chunks_from_book(self, filenames):
        for filename in filenames:
            with open(filename) as file:
                chunks = text_to_chunks(file.read())
                self.chapters_in_chunks.append(chunks)

    def populate_chunks_dictionary(self):
        for chapter in self.chapters_in_chunks:
            for chunk in chapter:
                self.chunks_dictionary[chunk] = ""

    def get_dictionary(self):
        return self.chunks_dictionary

    def set_dictionary(self, new_dictionary):
        print(self.chunks_dictionary)
        for key, val in new_dictionary.items():
            if key in self.chunks_dictionary:
                self.chunks_dictionary[key] = val
            else:
                raise Exception(f'Wrong key found trying to set dictionary to ePubSerializer: {key, val}')

    def save_to_file(self, output_filename):
        with open(output_filename + '.json', 'w') as file:
            json.dump({
                "metadata": self.metadata,
                "dictionary": self.chunks_dictionary,
                "chapters": [{'chunks': chunks} for chunks in self.chapters_in_chunks]
                },
                file)