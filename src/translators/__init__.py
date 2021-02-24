from translators.agents import GoogleTranslateAgent, DeeplAgent
from translators.parsers import NewlineParser
from translators.selenium_translators import SeleniumTranslator


def create_translator(source_language, target_language):
    agent = DeeplAgent
    if source_language in ['dk', 'da']:
        source_language = 'da'
        agent = GoogleTranslateAgent
    return SeleniumTranslator(source_language, target_language, NewlineParser, agent)
