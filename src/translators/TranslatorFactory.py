from translators.DeepLTranslator import DeepLTranslator, InteractionAgentABC, ChineseInteractionAgent


def create_translator(source_language, target_language):
    return DeepLTranslator(source_language,target_language,ChineseInteractionAgent)
