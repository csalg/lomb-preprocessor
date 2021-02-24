from .parsers import ParserABC, NewlineParser

ids_and_sentences_to_translate = {
    1000: "Something something.",
    1001: "Another sentence.",
    1002: "Two lines, and the second one \n55 starts with a number"
}

def parser_tester(parser_constructor):
    parser = parser_constructor()
    buffer = "\n\n hfdlasf \n"
    for id, sentence in ids_and_sentences_to_translate.items():
        buffer += parser.encode_sentence(id,sentence)

    # We will not translate the buffer, so we should be able to parse
    # the same sentences we gave it.
    translated_dictionary = parser.parse_translated_buffer(ids_and_sentences_to_translate, buffer)
    print(translated_dictionary)
    assert len(translated_dictionary) == len(ids_and_sentences_to_translate)
    for sentence in ids_and_sentences_to_translate.values():
        assert translated_dictionary[sentence] == sentence

def test_newline_parser():
    return parser_tester(NewlineParser)