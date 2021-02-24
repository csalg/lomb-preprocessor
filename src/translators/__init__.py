from translators.selenium_translators import GoogleTranslator, DeepLTranslator


def create_translator(source_language, target_language):
    if source_language in ['dk', 'da']:
        return GoogleTranslator('da', target_language)
    else:
        return DeepLTranslator(source_language, target_language)
