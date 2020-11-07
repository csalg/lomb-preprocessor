from taggers.taggers.GermanTagger import GermanTagger
from taggers.taggers.SpacyTaggers import SpanishTagger, EnglishTagger, FrenchTagger, DanishTagger

langToTagger = {
    'de': GermanTagger,
    'en': EnglishTagger,
    'es': SpanishTagger,
    'fr': FrenchTagger,
    'da': DanishTagger,
}

def createTagger(language):
        return langToTagger[language]
