import configparser
import json
import requests
import subprocess

import datetime
from datetime import timedelta
from collections import OrderedDict

import simpleaudio as sa
import speech_recognition as sr

URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"

replies = {  # создаем словарь вопрос-ответ в случае ответа пациента "да"
    "у вас что-то болит?": "доктор принесёт лекарство",
    "вы хотите в туалет?": "медсестра уже идёт к вам на помощь",
    "вы хотите пить?": "медсестра позаботится о вас, ожидайте",
    "вы хотите поговорить с родными?": "я уже решаю этот вопрос",
    "вы хотите продолжить диалог?": "хорошо, попробуем снова"
}

replies_order = OrderedDict(zip(replies.keys(), replies.values()))  # сохраним порядок


def read_config(name_settings):
    """ функция парсит .ini

    :param name_settings: имя элемента в .ini (str)
    :return значение элемента списка Settings (str)

    """
    config = configparser.ConfigParser()
    config.read(path)
    return config.get("Settings", name_settings)  # config.get("Settings", "iam_token")


def write_ini(name_settings, name):
    """ Функция записывает новые значения в конфиг .ini

    :param name_settings: имя параметра в .ini (str)
    :param name: значение параметра, которое будет записано в .ini (str)

    """
    config = configparser.ConfigParser()  # создаем конфиг-парсер
    config.read(path)  # просим его прочесть конфиг
    config.set("Settings", name_settings, name)
    with open(path, "w") as config_file:  # записываем изменения в settings.ini
        config.write(config_file)


def create_token():
    """ Функция генерирует и записывает новый токен и дату его смерти в .ini,
    если срок текущего токена истек

    :return iam (str)

    """
    oauth_token = read_config("oauth_token")  # прочитали oaiuth_token из конфига
    params = {
        "yandexPassportOauthToken": oauth_token  # указали oaiuth_token в параметрах запроса
    }
    response = requests.post("https://iam.api.cloud.yandex.net/iam/v1/tokens",
                             params=params)
    decode_response = response.content.decode('UTF-8')  # декодируем бинарник
    text = json.loads(decode_response)  # загружаем в json
    iam = text.get("iamToken")  # iam_token << json по ключу iamToken
    expires_iam_token = text.get("expiresAt")
    write_ini('iam_token', iam)  # запись токена в .ini
    write_ini('expires_iam_token', expires_iam_token)  # запись даты смерти iam_token в .ini
    return iam


def check_time():
    """ функция проверки срока действия iam_token

    :return True, если время вышло

    """
    datetime_token = datetime.datetime.strptime(read_config("expires_iam_token"),
                                                '%Y-%m-%dT%H:%M:%S.%fZ')
    datetime_today = datetime.datetime.today()
    delta12 = timedelta(hours=12)  # генерируем продолжительность в 12 часов
    continue_time = datetime_today - datetime_token
    if continue_time >= delta12:
        return True


def milena(say_something):
    """ функция голоса Milena озвучивает текст

    :param say_something: (str)

    """
    subprocess.call(["say", "-v", "Milena", say_something])


def recognize(data_sound):
    """ функция распознавания русской речи

    :param data_sound: ответ пациента (flac)
    :return text: (str)

    """

    id_folder = read_config("id_folder")  # читаем с конфига id_folder
    headers = {'Authorization': 'Bearer ' + iam_token}  # новый токен >> headers
    params = {
        'lang': 'ru-RU',
        'folderId': id_folder,
        'sampleRateHertz': 48000,
    }
    response = requests.post(URL, params=params, headers=headers, data=data_sound)  # отправка post-запроса
    decode_resp = response.content.decode('UTF-8')  # декодируем
    text = json.loads(decode_resp)  # загружаем в json
    if text.get("error_code") is None:
        text = text.get("result")  # забираем текст из json по ключу result
        print(text)
    else:
        print(text.get("error_code"))
        print("Милена недоступна. Попробуйте позже")
        return False
    return text


def signal(trek):
    """ функция включения звукового сигнала

    :param: trek (wav)

    """
    wave_obj = sa.WaveObject.from_wave_file(trek)
    play_obj = wave_obj.play()
    play_obj.wait_done()

def dialogue():
    """ Функция итерируется по ключам(question) в replies,
    Милена задает вопросы: milena(question)
    Пациент отвечает: listen() -> data_sound - ответ пациента (br)
    Yandex SpeechKit распознает: recognize(data_sound) -> текст (str)

    """
    recognizer = sr.Recognizer()
    while True:
        for question in replies_order.keys():  # итерируемся по вопросам по порядку
            milena(question)
            with sr.Microphone() as source:  # слушаем ответ пациента
                recognizer.adjust_for_ambient_noise(source,
                                                    duration=0.3)  # настройка микрофона
                data = recognizer.listen(source, phrase_time_limit=7)  # записываем ответ пациента
                data_sound = data.get_flac_data()  # ответ -> flac
                recognize_text = recognize(data_sound)  # распознавание ответа

            if recognize_text == "нет":
                if question == list(replies_order.items())[-1][0]:  # если уже последний вопрос
                    return
                else:
                    continue

            elif recognize_text == "да":
                milena(replies_order[question])
                continue


if __name__ == "__main__":
    path = "settings.ini"  # определяем путь к конфигу
    iam_token = read_config("iam_token")
    if check_time():  # если пришло время, генерим новый токен и записывавем его в .ini
        print("Время iam_token истекло. Отправка запроса ...")
        iam_token = create_token()
        print("А вот и Милена")
    else:
        print("Токен еще жив, а вот и Милена ...")
    signal("Harp 1.wav")
    milena("добро пожаловать!, Я ваш робот-медсестра")
    dialogue()
    milena("Бутьте здоровы!, до связи")
    signal("Harp 1.wav")
