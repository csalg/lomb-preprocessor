from translators_old.DeepLTranslator import DeepLTranslator, ChineseInteractionAgent


def create_translator(source_language, target_language):
    return DeepLTranslator(source_language,target_language,ChineseInteractionAgent)
