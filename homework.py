import time
import logging
from http import HTTPStatus

import requests
import telegram

from config import (
    ENDPOINT, HANDLER, HEADERS, HOMEWORK_VERDICTS,
    PRACTICUM_TOKEN, RETRY_PERIOD, TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(HANDLER)


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
        logging.critical(
            msg=msg
        )
        raise SystemExit(msg)


def send_message(bot, message):
    """Функция для отправки сообщения в телеграм."""
    logging.debug(
        msg='Начало отправки сообщения в чат телеграма'
    )
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logging.debug(
            msg='Сообщение успешно отправлено в чат телеграма'
        )
    except telegram.TelegramError as err:
        logging.error(
            msg=(
                'Ошибка при отправке сообщения'
                f'о состояния проекта в чат телеграма: {err}'
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
        logging.debug(
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
                    f'статус код {response.status_code}'
                ),
                params=params)
        )
    if response.status_code == HTTPStatus.OK:
        logging.debug(
            msg=output_logging_for_http_request(
                main_msg='Запрос успешно выполнен',
                params=params
            )
        )
        return response.json()
    logging.error(
        msg=output_logging_for_http_request(
            main_msg=f'Ошибка при запросе, статус код {response.status_code}',
            params=params
        )
    )
    raise ValueError(
        output_logging_for_http_request(
            main_msg=f'Ошибка при запросе, статус код {response.status_code}',
            params=params)
    )


def check_response(response):
    """
    Функция валидатор данных для парсинга.
    Проверяет что тело ответа приоразовано из json в словарь;
    что в это словаре есть ключ homeworks;
    что значением ключа homewirks будет список.
    """
    logging.debug(
        msg='Начало выполнения функции check_response для валидации данных.'
    )
    if not isinstance(response, dict):
        raise TypeError(
            ('Данные должны быть приобразованы из json в словарь.'
             f'Пришёл тип данных {type(response)}.')
        )
    if ('homeworks' or 'current_date') not in response:
        raise KeyError(
            'В словаре response должен быть ключ homeworks/current_date.')
    if not isinstance(response['homeworks'], list):
        raise TypeError(
            ('Значением \'homeworks\' должен быть список.'
             f'Пришёл тип данных {type(response["homeworks"])}.')
        )
    logging.debug(
        msg='Данные в функции check_response успешно провалидированы.'
    )
    return response['homeworks']


def parse_status(homework):
    """
    Функция подготавливает сообщения для отправки в чат.
    Или вызывает TypeError если есть ошибки.
    """
    logging.debug(
        'Начало выполнения функции parse_status для парсинга данных.')
    if 'homework_name' not in homework:
        raise TypeError('В homework нет ключа \'homework_name\'.')
    if 'status' not in homework:
        raise TypeError('В homework нет ключа \'status\'.')
    new_status = homework['status']
    if new_status not in HOMEWORK_VERDICTS:
        raise TypeError(f'В HOMEWORK_VERDICTS нет ключа \'{new_status}\'.')
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[new_status]
    logging.debug('Функция parse_status успешно отработала.')
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
                logging.debug('Обновлений домашней работы пока ещё нет.')
            timestamp = data_json['current_date']
        except Exception as error:
            new_message = f'Сбой в работе программы: {error}'
            if message != new_message:
                logging.error(new_message)
                message = new_message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
