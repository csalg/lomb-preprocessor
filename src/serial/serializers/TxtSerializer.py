import json
import os
from copy import copy

import ebooklib
from bs4 import BeautifulSoup

from util import convert_to_utf8

from .SerializerABC import SerializerABC
from serial.util import text_to_chunks
from ..Chunk import Chunk


class TxtSerializer(SerializerABC):
    def __init__(self, filename, source_language, target_language):
        convert_to_utf8(filename)

        with open(filename) as file:
            source = file.read()
        chunks_as_text = text_to_chunks(source)

        self.__source_language, self.__target_language = source_language, target_language

        self.__chunks                   = list(map(lambda txt : Chunk(txt), chunks_as_text))
        self.__translation_dictionary   = {chunk : "" for chunk in chunks_as_text}
        self.__lemmas_dictionary        = {chunk : "" for chunk in chunks_as_text}

    @classmethod
    def from_epub(cls,filename,*args):
        book = ebooklib.epub.read_epub(filename)
        buffer = ""

        for document in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            try:
                doc = document.get_content().decode('utf-8')
                soup = BeautifulSoup(doc, 'html5lib')
                buffer += soup.get_text()
            except:
                pass

        txt_filename = filename.rsplit('.')[0] + '.txt'

        with open(txt_filename, 'w') as file:
            file.write(buffer)

        return cls(txt_filename,*args)


    def get_translation_dictionary(self):
        return self.__translation_dictionary
    
    def set_translation_dictionary(self, new_dictionary):
        self.__translation_dictionary = new_dictionary
        print(new_dictionary)

    def get_lemmas_dictionary(self):
        return self.__lemmas_dictionary

    def set_lemmas_dictionary(self, new_dictionary):
        self.__lemmas_dictionary = new_dictionary

    def save_to_file(self, output_filename):
        self._add_support_text_to_chunks()
        self._add_lemmas_to_chunks()
        # self._save_as_json(output_filename)
        self._save_as_txt(output_filename)
        self._save_as_html(output_filename)

    def _add_support_text_to_chunks(self):
        for chunk in self.__chunks:
            support_text = self.__translation_dictionary[chunk.text]
            chunk.set_support_text(support_text)

    def _add_lemmas_to_chunks(self):
        for chunk in self.__chunks:
            tokens_to_lemmas = self.__lemmas_dictionary[chunk.text]
            chunk.set_tokens_to_lemmas(tokens_to_lemmas)

    # def _save_as_json(self, output_filename):
    #     with open(output_filename+'.json', 'w') as file:
    #         json.dump({
    #             "dictionary": self._translation_dictionary,
    #             "chunks": self._chunks},
    #             file)

    def _save_as_txt(self, output_filename):
        print(self.__chunks)
        translated_chunks = list(map(lambda chunk : chunk.support_text, self.__chunks))
        translation = ''.join(translated_chunks)

        with open(output_filename, 'w') as file:
            file.write(translation)

    def _save_as_html(self, output_filename):
        translated_chunks =[]
        id = 0
        for chunk in self.__chunks:
            translated_chunks.append(chunk.to_span(id))
            id += 1
        translation = \
        f"""
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <meta name="title" value="{os.path.basename(output_filename)}">
    <meta name="source-language" value="{self.__source_language}">
    <meta name="support-language" value="{self.__target_language}">
</head>
<body>
{''.join(translated_chunks)}
</body>
</html>
        """
        with open(output_filename + '.html', 'w') as file:
            file.write(translation)
