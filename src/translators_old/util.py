languages = ['en', 'es', 'de', 'zh', 'fr', 'da']
languages_map = {
    'deu': 'de',
    'esp': 'es',
    'eng': 'en',
    'en-us': 'en',
    'en-US': 'en'
}

deepl_languages = {
    'en': 'en-US'
}

to_deepl_language = lambda lang : deepl_languages[lang] if lang in deepl_languages else f"{lang.lower()}-{lang.upper()}"

is_recognized_language = lambda language : language in languages or language in languages_map

def infer_language(language):
    language = language.lower()
    if language in languages:
        return language
    if language in languages_map:
        return languages_map[language]
    raise Exception(f"Could not infer language from '{language}'")
    