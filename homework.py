import sys
import time
import json
import logging

import requests

import telegram

from config import (
    LOGGING_FORMAT,
    PRACTICUM_TOKEN,
    TELEGRAM_TOKEN,
    TELEGRAM_CHAT_ID,
    RETRY_PERIOD,
    ENDPOINT,
    HEADERS,
    HOMEWORK_VERDICTS,
)


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


def check_tokens():
    """
    Проверка на наличие токенов:
    PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID.
    """

    try:
        assert PRACTICUM_TOKEN, 'PRACTICUM_TOKEN'
        assert TELEGRAM_TOKEN, 'TELEGRAM_TOKEN'
        assert TELEGRAM_CHAT_ID, 'TELEGRAM_CHAT_ID'
    except AssertionError as err:
        logging.critical(
            msg=f'Токен \'{err}\' из окружения переменных не загрузился.'
        )
        raise SystemExit()


def send_message(bot, message):
    """Функция для отправки сообщения в телеграм."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logging.debug(
            msg='Отправка сообщения прошла успешно'
        )
    except Exception as err:
        logging.error(
            msg=f'Ошибка при отправке сообщения: {err}'
        )


def get_api_answer(timestamp):
    """
    Функция делает запрос к yandex-API.
    Если запрос успешный - возвращает тело ответа.
    Иначе вызываеи TypeError.
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
    raise TypeError('Ошибка при отправке.')


def write_in_json():
    with open('resp.json', 'w', encoding='utf-8') as f:
        json.dump(get_api_answer(0), f, ensure_ascii=False)


def check_response(response):
    """
    Функция валидатор данных для парсинга.
    Проверяет что тело ответа приоразовано из json в словарь;
    что в это словаре есть ключ homeworks;
    что значением ключа homewirks будет список.
    """
    if not isinstance(response, dict):
        raise TypeError('Данные должны быть приобразованы из json в словарь.')
    if 'homeworks' not in response:
        raise TypeError('В словаре response должен быть ключ \'homeworks.\'')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Значением \'homeworks\' должен быть список.')
    return response['homeworks']




def parse_status(homework):
    """
    Функция подготавливает сообщения для отправки в чат,
    или вызывает TypeError если есть ошибки.
    """
    try:
        new_status = homework['status']
        verdict = HOMEWORK_VERDICTS[new_status]
        homework_name = homework['homework_name']
    except KeyError as err:
        raise TypeError('Ошибка связанная с ключём.') from err
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""

    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    status = 'reviewing'
    while True:
        try:
            data_json = get_api_answer(timestamp)
            timestamp = data_json['current_date']
            homeworks = check_response(data_json)
            if homeworks:
                text = parse_status(data_json['homeworks'][0])
                actual_status = data_json['homeworks'][0]['status']
                if actual_status != status:
                    status = actual_status
                    send_message(
                        bot=bot,
                        message=text
                    )
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            raise SystemExit()
        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
