import json
import configparser
import os
import requests
import subprocess

import simpleaudio as sa
import speech_recognition as sr


URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"


replies = {
    "привет": "здравствуйте, пациент, у вас что-то болит?",
    "да": "доктор принес+ёт лекарства",
    "я все": "до связи, будьте здоровы"
}


def create_config(path):  # создание файла settings.ini, если его не существует
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "iam_token", "iam_token")
    with open(path, "w") as config_file:   # записываем изменения
        config.write(config_file)


def read_id_folder(path):  # функция считывает id_folder из конфига
    config = configparser.ConfigParser()
    config.read(path)
    return config.items("Settings", 'id_folder')[1][1]


def crud_config(path):  # функция генерирует, записывает в settings.ini и возвращает новый токен
    if not os.path.exists(path):  # если конфиг-файла нет, создаем
        create_config(path)

    config = configparser.ConfigParser()  # создаем конфиг-парсер
    config.read(path)  # просим его прочесть конфиг
    result = subprocess.run("yc iam create-token".split(" "),
                            stdout=subprocess.PIPE).stdout.decode('utf-8')[:-1]  # запуск генерации токена
    config.set("Settings", "iam_token", result)  # меняем значение токена на новое сгенерированное
    with open(path, "w") as config_file:   # записываем изменения в settings.ini
        config.write(config_file)

    return config.get("Settings", "iam_token")


def signal():  # функция включения звукового сигнала
    wave_obj = sa.WaveObject.from_wave_file("Harp 1.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()


def recognize(data_sound):  # функция распознавания русской речи
    headers = {
        'Authorization': 'Bearer ' + iam_token,  # добваляем новый токен в headers
    }

    params = {
        'lang': 'ru-RU',
        'folderId': id_folder,
        'sampleRateHertz': 48000,
    }

    resp = requests.post(URL, params=params, headers=headers, data=data_sound, stream=True)  # отправка post-запроса
    decode_resp = resp.content.decode('UTF-8')  # декодируем
    text = json.loads(decode_resp)  # загружаем в json
    if text.get("error_code") is None:
        text = text.get("result")  # забираем текст из json по ключу result
        print(text)
    return text


def main():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)  # настройка микрофона
            data_sound = recognizer.listen(source, phrase_time_limit=7)  # пациент что-то отвечает ..> data_sound
            data_sound = data_sound.get_flac_data()

        recognize_text = recognize(data_sound)  # ответ пациента распознается через Yandex Api, получаем в результате текст

        subprocess.call(["say", "-v", "Milena", replies.get(recognize_text.lower())])
        if recognize_text == "я все":
            signal()
            break


if __name__ == "__main__":
    path = "settings.ini"  # определяем путь к конфигу
    iam_token = crud_config(path)  # генерируем новый токен
    id_folder = read_id_folder(path)  # считывваем id_folder с конфига
    subprocess.call(["say", "-v", "Milena", "добро пожаловать, я ваш голосовой помощник"])  # Приветствие
    subprocess.call(["say", "-v", "Milena", "говорите после сигнала"])
    signal()
    main()
