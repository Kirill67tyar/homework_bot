import sys
import logging

from config import LOGGING_FORMAT


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(
    stream=sys.stdout
)
formatter = logging.Formatter(
    LOGGING_FORMAT
)
handler.setFormatter(formatter)
logger.addHandler(handler)
