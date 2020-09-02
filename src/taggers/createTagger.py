from taggers.taggers.GermanTagger import GermanTagger
from taggers.taggers.SpacyTaggers import SpanishTagger, EnglishTagger, FrenchTagger

langToTagger = {
    'de': GermanTagger,
    'en': EnglishTagger,
    'es': SpanishTagger,
    'fr': FrenchTagger,
}

def createTagger(language):
        return langToTagger[language]
