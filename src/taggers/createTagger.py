from taggers.taggers.GermanTagger import GermanTagger
from taggers.taggers.SpacyTaggers import SpanishTagger, EnglishTagger

langToTagger = {
    'de': GermanTagger,
    'en': EnglishTagger,
    'es': SpanishTagger,
}

def createTagger(language):
        return langToTagger[language]
