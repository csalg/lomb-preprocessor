from translators.selenium_translators import GoogleTranslator

translation_dictionary = {
    "Roses are red": "",
    "Violets are blue": ""
}

def test_google_translate():
    translator = GoogleTranslator(source_language='en', target_language='da')
    translations = translator.translate(translation_dictionary)
    for target_sentence in translations.values():
        assert  target_sentence
