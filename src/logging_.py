import logging
import sys

from config import LOGGING_LEVEL

logger = logging.getLogger('lomb_preprocessor')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(LOGGING_LEVEL)
logger.debug('Logger works')
