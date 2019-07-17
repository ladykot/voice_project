import configparser
import json
import logging
import requests

import datetime
from datetime import timedelta


PATH = 'settings.ini'


def read_config(name_settings):
    """ функция парсит .ini

    :param name_settings: имя элемента в .ini (str)
    :return значение элемента списка Settings (str)

    """
    config = configparser.ConfigParser()
    config.read(PATH)
    return config.get('Settings', name_settings)


def check_time(iam_token):
    """ функция проверки срока действия iam_token

    :return True, если время вышло

    """

    datetime_token = datetime.datetime.strptime(read_config("expires_iam_token"),
                                                '%Y-%m-%dT%H:%M:%S.%fZ')
    datetime_today = datetime.datetime.today()
    delta12 = timedelta(hours=12)  # генерируем продолжительность в 12 часов
    continue_time = datetime_today - datetime_token
    if continue_time >= delta12:
        return None
    else:
        return iam_token


def write_ini(name_settings, name):
    """ Функция записывает новые значения в конфиг .ini

    :param name_settings: имя параметра в .ini (str)
    :param name: значение параметра, которое будет записано в .ini (str)

    """
    config = configparser.ConfigParser()  # создаем конфиг-парсер
    config.read(PATH)  # просим его прочесть конфиг
    config.set('Settings', name_settings, name)
    with open(PATH, 'w') as config_file:  # записываем изменения в settings.ini
        config.write(config_file)


def create_token():
    """ Функция проверяет срок iam_token по .ini,
    генерирует и записывает новый токен и дату его смерти в .ini,
    если срок текущего токена истек:

    if срок check_time(iam_token) прошел (True):
        :return iam_new (str)
    else:
        :return iam_token

    """
    iam_token = read_config('iam_token')  # читаем iam_token из .ini
    check_time(iam_token)

    if check_time(iam_token) is None:  # если пришло время, генерим новый токен и записывавем его в .ini
        logging.info('Время iam_token истекло. Отправка запроса ...')
        oauth_token = read_config("oauth_token")  # прочитали oauth_token из конфига
        params = {
            'yandexPassportOauthToken': oauth_token  # указали oauth_token в параметрах запроса
        }
        response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens',
                                 params=params)
        decode_response = response.content.decode('UTF-8')  # декодируем бинарник
        text = json.loads(decode_response)  # загружаем в json
        iam_new = text.get('iamToken')  # iam_token << json по ключу iamToken
        expires_iam_token = text.get('expiresAt')

        write_ini('iam_token', iam_new)  # запись токена в .ini
        write_ini('expires_iam_token', expires_iam_token)  # запись даты смерти iam_token в .ini
        logging.info("А вот и Милена")
        return iam_new
    else:
        logging.info('Токен еще жив, а вот и Милена ...')
        return iam_token


if __name__ == '__main__':
    create_token()
