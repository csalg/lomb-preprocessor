from taggers._taggers.german_tagger import GermanTagger
from taggers._taggers.spacy_taggers import EnglishTagger, SpanishTagger, FrenchTagger, DanishTagger


def create_tagger(language):
    language_to_tagger = {
        'de': GermanTagger,
        'en': EnglishTagger,
        'es': SpanishTagger,
        'fr': FrenchTagger,
        'da': DanishTagger,
    }
    return language_to_tagger[language]()