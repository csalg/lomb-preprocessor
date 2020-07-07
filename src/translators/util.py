languages = ['en', 'es', 'de', 'zh']
languages_map = {
    'deu': 'de',
    'esp': 'es',
    'eng': 'en',
    'en-us': 'en',
    'en-US': 'en'
}

is_recognized_language = lambda language : language in languages or language in languages_map

def infer_language(language):
    language = language.lower()
    if language in languages:
        return language
    if language in languages_map:
        return languages_map[language]
    raise Exception(f"Could not infer language from '{language}'")
    