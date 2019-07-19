import configparser
import json
import logging
import requests


PATH = 'settings.ini'
URL_REC = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"


def read_config(name_settings):
    """ функция парсит .ini

    :param name_settings: имя элемента в .ini (str)
    :return значение элемента списка Settings (str)

    """
    config = configparser.ConfigParser()
    config.read(PATH)
    return config.get('Settings', name_settings)


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
    """ Функция проверяет срок iam_token.
    Если при попытке аторизации c настоящим токеном приходит ошибка,
    то генерируется новый iam_token и записывается в .ini

    if text.get("error_code") is not 'UNAUTHORIZED':
        :return iam_token (str)
    else:
        :return iam_new (str

    """
    iam_token = read_config('iam_token')  # читаем iam_token из .ini
    id_folder = read_config('id_folder')
    headers = {'Authorization': 'Bearer ' + iam_token}  # iam_token >> headers
    params = {
        'lang': 'ru-RU',
        'folderId': id_folder,
        'sampleRateHertz': 48000,
    }
    response = requests.post(URL_REC, params=params, headers=headers)  # отправка post-запроса на проверку
    decode_resp = response.content.decode('UTF-8')  # декодируем
    text = json.loads(decode_resp)  # загружаем в json

    if text.get("error_code") is not 'UNAUTHORIZED':
        logging.info('Срок действия токена еще не истек')
        return iam_token

    else:
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
        logging.info("Новый iam_token успешно сгенерирован. "
                     f"Срок жизни: до {expires_iam_token}")
        return iam_new


if __name__ == '__main__':
    # iam_token = read_config('iam_token')  # читаем iam_token из .ini
    # print(iam_token)
    create_token()
