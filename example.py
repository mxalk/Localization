import Localization
import logging

logger = logging.getLogger('Localization.Localization')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)

Localization.LocalizationServer(2001)