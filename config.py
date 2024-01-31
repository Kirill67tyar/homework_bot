import os
import sys
import logging

from dotenv import load_dotenv


load_dotenv()

LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)d - %(message)s'

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


HANDLER = logging.StreamHandler(
    stream=sys.stdout
)

formatter = logging.Formatter(
    LOGGING_FORMAT
)

HANDLER.setFormatter(formatter)
