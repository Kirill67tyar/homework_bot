import os
import time
import json
from pprint import pprint as pp

import requests

import telegram
from telegram import Bot

from dotenv import load_dotenv

load_dotenv()


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

# Функция check_tokens() проверяет доступность переменных окружения,
# которые необходимы для работы программы.
# Если отсутствует хотя бы одна переменная окружения — продолжать работу бота нет смысла.


def check_tokens():
    try:
        assert PRACTICUM_TOKEN, 'PRACTICUM_TOKEN'
        assert TELEGRAM_TOKEN, 'TELEGRAM_TOKEN'
        assert TELEGRAM_CHAT_ID, 'TELEGRAM_CHAT_ID'
    except AssertionError as err:
        print('Not determine token:')
        print(err)
        raise SystemExit


# Функция send_message() отправляет сообщение в Telegram чат, определяемый переменной окружения TELEGRAM_CHAT_ID.
# Принимает на вход два параметра: экземпляр класса Bot и строку с текстом сообщения.
def send_message(bot, message):
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
    )


# Функция get_api_answer() делает запрос к единственному эндпоинту API-сервиса.
# В качестве параметра в функцию передается временная метка.
# В случае успешного запроса должна вернуть ответ API, приведя его из формата JSON к типам данных Python.


def get_api_answer(timestamp):
    params = {
        'from_date': timestamp,
    }
    response = requests.get(
        ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if response.ok:
        return response.json()
    return 'no data'
# pp(get_api_answer(int(time.time())))


def write_in_json():
    with open('resp.json', 'w', encoding='utf-8') as f:
        json.dump(get_api_answer(0), f, ensure_ascii=False)


# Функция check_response() проверяет ответ API на соответствие документации
# из урока API сервиса Практикум.Домашка.
# В качестве параметра функция получает ответ API, приведенный к типам данных Python.
def check_response(response):
    ...

# # !-----------------------------
# # Функция parse_status() извлекает из информации о конкретной домашней работе статус этой работы.
# # В качестве параметра функция получает только один элемент из списка домашних работ.
# # В случае успеха, функция возвращает подготовленную для отправки в Telegram строку,
# # содержащую один из вердиктов словаря HOMEWORK_VERDICTS.
# * HOMEWORK_VERDICTS = {
# *     'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
# *     'reviewing': 'Работа взята на проверку ревьюером.',
# *     'rejected': 'Работа проверена: у ревьюера есть замечания.'
# * }


def last_status(homework):
    return homework.get('status')


def parse_status(homework):
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS.get(status)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    ...

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - RETRY_PERIOD
    return get_api_answer(RETRY_PERIOD)
    # send_message(bot)
    # homework = 'asd'
    # status = last_status(homework)
    ...

    # while True:
    #     try:

    #         ...

    #     except Exception as error:
    #         message = f'Сбой в работе программы: {error}'
    #         ...
    #     ...


if __name__ == '__main__':
    # main()
    pp(main())
