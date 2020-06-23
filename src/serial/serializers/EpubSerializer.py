import json
from dataclasses import dataclass, asdict
from functools import reduce
from statistics import mean, stdev

from bs4 import BeautifulSoup,NavigableString
import ebooklib
from ebooklib import epub

from .SerializerABC import SerializerABC
from serial.util import regex_that_breaks_into_chunks, text_to_chunks


open_tag = lambda i: f'<span data-chunk-id={i} data-support-text="" class="lomb-chunk">'
close_tag = '</span>'


class EpubSerializer(SerializerABC):
    def __init__(self, filename):

        self.book = ebooklib.epub.read_epub(filename)

        self.chunks_array = {}
        self.chunks_dictionary = {}

        self.cursor = 0
        self._parse_book()
        self._fake_translate()
        self._update_tags()
    
    def _parse_book(self):
        for document in self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            doc = document.get_content().decode('utf-8')
            new_content = self._parse_document(doc)
            document.set_content(new_content.encode('utf-8'))

    def _parse_document(self, xml_document):
        soup = BeautifulSoup(xml_document)
        soup = self._add_chunk_tags_to(soup, ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'])
        return soup

    def _add_chunk_tags_to(self, soup, elements):
        for tag in soup.find_all(elements, text=True):
            updated_tag =  self._add_chunk_tags_to_tag(tag)
            tag.replace_with(updated_tag)
        return soup
    
    def _add_chunk_tags_to_tag(self,tag):
        # buffer = ""
        # sentence = ""
        # inside_tag = False
        # first_sentence_seen = True
        # tag_is_open = False
        open_tag = lambda i: f'<span data-chunk-id={i} data-support-text="" class="lomb-chunk">'
        close_tag = '</span>'

        contents = tag.text
        tag.string = ""

        for sentence in text_to_chunks(contents):
            if sentence:
                self.cursor += 1
                self._add_sentence(self.cursor, sentence)
                tag_to_append = open_tag(self.cursor) + sentence + close_tag
                print(tag_to_append)
                tag.append(BeautifulSoup(tag_to_append))

        return tag


    #
    #     for i, character in enumerate(contents):
    #         buffer += character
    #         if character == '<':
    #             # End of a
    #             close_sentence()
    #             inside_tag = not inside_tag
    #             continue
    #         if inside_tag:
    #             continue
    #         if first_sentence_seen:
    #             buffer = self._append_first_tag(open_tag, buffer, character)
    #             self.cursor += 1
    #             first_sentence_seen = False
    #         if regex_that_breaks_into_chunks.match(character):
    #             sentence += character
    #             if self._is_sentence(sentence):
    #                 buffer += close_tag + open_tag(self.cursor)
    #                 self.cursor += 1
    #                 self.add_sentence(self.cursor,sentence)
    #             sentence = ""
    #             continue
    #         sentence += character
    #
    #     buffer = self._close_off_buffer(close_tag, buffer)
    #
    #     return buffer
    #
    # def _append_first_tag(self, open_tag, buffer, character):
    #     buffer = buffer[:-1]
    #     buffer += open_tag(self.cursor)
    #     buffer += character
    #     return buffer
    #
    # def _is_sentence(self, sentence):
    #     return sentence and sentence.strip("\n ") and not regex_that_breaks_into_chunks.match(sentence)
    #
    # def _close_off_buffer(self, close_tag, buffer):
    #     return buffer[:-7]+close_tag+'<body>'
    #
    def _add_sentence(self, id, sentence):
        self.chunks_array[id] = sentence
        self.chunks_dictionary[sentence] = ""

    def _fake_translate(self):
        for key, val in self.chunks_dictionary.items():
            self.chunks_dictionary[key] = key

    def _update_tags(self):
        print('Updating tags')
        for document in self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            try:
                doc = document.get_content().decode('utf-8')
                new_content = self._update_document_tags(doc)
                document.set_content(new_content.encode('utf-8'))
            except:
                pass

    def _update_document_tags(self, xml_document):
        soup = BeautifulSoup(xml_document, 'html.parser')
        query = soup.find_all("span", {'class':'lomb-chunk'})
        if query:
            for chunk_tag in query:
                id = chunk_tag['data-chunk-id']
                soup = self._update_support_text(soup, id)
        else:
            raise Exception('No valid content found')
        return soup

    def _update_support_text(self, soup, id):
        if int(id) in self.chunks_array:
            sentence = self.chunks_array[int(id)]
            support_text = self.chunks_dictionary[sentence]
            query = {'class':'lomb-chunk', 'data-chunk-id': id}
            soup.find('span',query)['data-support-text'] = support_text
            if not query:
                assert False
        return soup

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
        ebooklib.epub.write_epub(output_filename, self.book)
        # update the span tags to include chunk data
        # save as epub
        pass





@dataclass
class Chunk:
    source : str
    support : str
    tokens_to_lemmas : list

    def to_dict(self):
        return asdict(self)
