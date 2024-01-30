import os
import sys
import time
import json
import logging

from pprint import pprint as pp

import requests

import telegram
from telegram import Bot

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(
    stream=sys.stdout
)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

"""
Каждое сообщение в журнале логов должно состоять как минимум из
даты и времени события,
уровня важности события,
описания события.

 -- Где:
    asctime — время события,
    levelname — уровень важности,
    message — текст сообщения,
    name — имя логгера.
"""

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# bot = Bot(token=TELEGRAM_TOKEN)

# bot.send_message(
#     chat_id=TELEGRAM_CHAT_ID,
#     text='asdasdasd',
# )


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
MONTH_IN_SECONDS = 60 * 60 * 24 * 30

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
# status = 'reviewing'
# Функция check_tokens() проверяет доступность переменных окружения,
# которые необходимы для работы программы.
# Если отсутствует хотя бы одна переменная окружения — продолжать работу бота нет смысла.


def check_tokens():
    """_summary_

    Raises:
        ValueError: _description_
    """
    # if not all(
    #     [
    #         PRACTICUM_TOKEN,
    #         TELEGRAM_TOKEN,
    #         TELEGRAM_CHAT_ID,
    #         None,
    #     ]
    # ):
    #     raise ValueError('asd')

    try:
        assert PRACTICUM_TOKEN, 'PRACTICUM_TOKEN'
        assert TELEGRAM_TOKEN, 'TELEGRAM_TOKEN'
        assert TELEGRAM_CHAT_ID, 'TELEGRAM_CHAT_ID'
    except AssertionError as err:
        logging.critical(
            msg='Всё упало! Зовите админа!1!111'
        )
        print('Not determine token:')
        print(err)
        raise ValueError('value-error')


# Функция send_message() отправляет сообщение в Telegram чат, определяемый переменной окружения TELEGRAM_CHAT_ID.
# Принимает на вход два параметра: экземпляр класса Bot и строку с текстом сообщения.
def send_message(bot, message):
    """_summary_

    Args:
        bot (_type_): _description_
        message (_type_): _description_
    """
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logging.debug(
            msg='Всё упало! Зовите админа!1!111'
        )
    except Exception:
        logging.error(
            msg='Всё упало! Зовите админа!1!111'
        )

# Функция get_api_answer() делает запрос к единственному эндпоинту API-сервиса.
# В качестве параметра в функцию передается временная метка.
# В случае успешного запроса должна вернуть ответ API, приведя его из формата JSON к типам данных Python.


def get_api_answer(timestamp):
    """_summary_

    Args:
        timestamp (_type_): _description_

    Raises:
        TypeError: _description_

    Returns:
        _type_: _description_
    """
    params = {
        'from_date': timestamp,
    }
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
        if response.status_code == 200:
            return response.json()
    except requests.RequestException:
        pass
    raise TypeError('лалалала')
# pp(get_api_answer(int(time.time())))


def write_in_json():
    with open('resp.json', 'w', encoding='utf-8') as f:
        json.dump(get_api_answer(0), f, ensure_ascii=False)


# Функция check_response() проверяет ответ API на соответствие документации
# из урока API сервиса Практикум.Домашка.
# В качестве параметра функция получает ответ API, приведенный к типам данных Python.
def check_response(response):
    """_summary_

    Args:
        response (_type_): _description_

    Raises:
        TypeError: _description_
        TypeError: _description_
        TypeError: _description_

    Returns:
        _type_: _description_
    """
    if not isinstance(response, dict):
        raise TypeError('Response must be dictionary')
    if 'homeworks' not in response:
        raise TypeError('тратата')
    if not isinstance(response['homeworks'], list):
        raise TypeError('тратата № 2')
    return response['homeworks']

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
    """_summary_

    Args:
        homework (_type_): _description_

    Raises:
        TypeError: _description_

    Returns:
        _type_: _description_
    """
    try:
        new_status = homework['status']
        verdict = HOMEWORK_VERDICTS[new_status]
        # homework_name = homework['lesson_name']
        homework_name = homework['homework_name']
    except KeyError:
        raise TypeError('ой бой')
    # if new_status != status:
        # return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'

# Функция main(): в ней описана основная логика работы программы.
# Все остальные функции должны запускаться из неё.
# Последовательность действий в общем виде должна быть примерно такой:
    # Сделать запрос к API.
    # Проверить ответ.
    # Если есть обновления — получить статус работы из обновления и отправить сообщение в Telegram.
    # Подождать некоторое время и вернуться в пункт 1.


def main():
    """Основная логика работы бота."""

    check_tokens()
    # ?----------------------------------------- 1
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # timestamp = int(time.time())
    timestamp = int(time.time()) - MONTH_IN_SECONDS
    # ?----------------------------------------- 1
    # status = last_status(homework)
    # ?----------------------------------------- 2
    status = 'reviewing'
    while True:
        try:
            data_json = get_api_answer(timestamp)
            timestamp = data_json['current_date']
            homeworks = check_response(data_json)
            if homeworks:
                text = parse_status(data_json['homeworks'][0])
                # global status
                actual_status = data_json['homeworks'][0]['status']
                if actual_status != status:
                    status = actual_status
                    # bot.send_message(
                    #     chat_id=TELEGRAM_CHAT_ID,
                    #     text=text,
                    # )
                    send_message(
                        bot=bot,
                        message=text
                    )

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            raise SystemExit()
            # break
        time.sleep(RETRY_PERIOD)
        # time.sleep(10)

    # ?----------------------------------------- 2


if __name__ == '__main__':
    main()
    # pp(main())
