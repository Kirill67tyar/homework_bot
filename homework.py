import sys
import time
import logging
from http import HTTPStatus

import requests
import telegram

from config import (
    ENDPOINT, HEADERS, HOMEWORK_VERDICTS,
    PRACTICUM_TOKEN, RETRY_PERIOD, TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN, LOGGING_FORMAT,
)


handler = logging.StreamHandler(
    stream=sys.stdout
)
formatter = logging.Formatter(
    LOGGING_FORMAT
)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def check_tokens():
    """
    Проверка на наличие токенов.
    Токены: PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID.
    """
    ENVIRON_VARIABLES = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
    }
    env_variables_have_null = [
        k for k, v in ENVIRON_VARIABLES.items() if not v
    ]
    if env_variables_have_null:
        output_for_error = ', '.join(env_variables_have_null)
        msg = (
            f'Токены: \'{output_for_error}\' '
            'из окружения переменных не загрузились.'
        )
        logger.critical(
            msg=msg
        )
        raise SystemExit(msg)


def send_message(bot, message):
    """Функция для отправки сообщения в телеграм."""
    logger.debug(
        msg=(
            f'Начало отправки сообщения "{message}" '
            f'в чат телеграма {TELEGRAM_CHAT_ID}'
        )
    )
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logger.debug(
            msg=(
                f'Сообщение "{message}" '
                f'успешно отправлено в чат телеграма {TELEGRAM_CHAT_ID}'
            )
        )
    except telegram.TelegramError as err:
        logger.error(
            msg=(
                f'Ошибка при отправке сообщения "{message}"'
                'о состоянии проекта, в чат телеграма'
                f'{TELEGRAM_CHAT_ID}: {err}'
            )
        )


def output_logging_for_http_request(main_msg, params):
    """
    Функция выводит сообщения для логирования.
    В функции get_api_answer.
    """
    return (
        f'{main_msg}\n'
        f'Адрес: {ENDPOINT}\n'
        f'Параметры: {params}'
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
        logger.debug(
            msg=output_logging_for_http_request(
                main_msg='Начало GET запроса',
                params=params
            )
        )
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.RequestException:
        raise ConnectionError(
            output_logging_for_http_request(
                main_msg=(
                    'Ошибка при запросе,'
                    f'статус код {response.reason}'
                ),
                params=params)
        )
    if response.status_code != HTTPStatus.OK:
        raise ValueError(
            output_logging_for_http_request(
                main_msg=f'Ошибка при запросе, статус код {response.reason}',
                params=params)
        )
    logger.debug(
        msg=output_logging_for_http_request(
            main_msg='Запрос успешно выполнен',
            params=params
        )
    )
    return response.json()


def check_response(response):
    """
    Функция валидатор данных для парсинга.
    Проверяет что тело ответа приоразовано из json в словарь;
    что в это словаре есть ключ homeworks;
    что значением ключа homewirks будет список.
    """
    logger.debug(
        msg='Начало выполнения функции check_response для валидации данных.'
    )
    if not isinstance(response, dict):
        raise TypeError(
            ('Данные должны быть приобразованы из json в словарь.'
             f'Пришёл тип данных {type(response)}.')
        )
    if 'current_date' not in response:
        raise KeyError(
            'В словаре response должен быть ключ current_date.')
    if 'homeworks' not in response:
        raise KeyError(
            'В словаре response должен быть ключ homeworks.')
    if not isinstance(response['homeworks'], list):
        raise TypeError(
            ('Значением \'homeworks\' должен быть список.'
             f'Пришёл тип данных {type(response["homeworks"])}.')
        )
    logger.debug(
        msg='Данные в функции check_response успешно провалидированы.'
    )
    return response['homeworks']


def parse_status(homework):
    """
    Функция подготавливает сообщения для отправки в чат.
    Или вызывает TypeError если есть ошибки.
    """
    logger.debug(
        'Начало выполнения функции parse_status для парсинга данных.')
    if 'homework_name' not in homework:
        raise KeyError('В homework нет ключа \'homework_name\'.')
    if 'status' not in homework:
        raise KeyError('В homework нет ключа \'status\'.')
    new_status = homework['status']
    if new_status not in HOMEWORK_VERDICTS:
        raise KeyError(f'В HOMEWORK_VERDICTS нет ключа \'{new_status}\'.')
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[new_status]
    logger.debug('Функция parse_status успешно отработала.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    message = None
    while True:
        try:
            data_json = get_api_answer(timestamp)
            homeworks = check_response(data_json)
            if homeworks:
                text = parse_status(data_json['homeworks'][0])
                send_message(
                    bot=bot,
                    message=text
                )
            else:
                logger.debug('Обновлений домашней работы пока ещё нет.')
            timestamp = data_json['current_date']
        except Exception as error:
            new_message = f'Сбой в работе программы: {error}'
            if message != new_message:
                send_message(
                    bot=bot,
                    message=new_message
                )
                message = new_message
            logger.error(new_message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
