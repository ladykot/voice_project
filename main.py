import json
import requests
import subprocess

from collections import OrderedDict

import simpleaudio as sa
import speech_recognition as sr

from settings import ID_FOLDER, IAM_TOKEN, URL

replies = {  # создаем словарь вопрос-ответ в случае ответа пациента "да"
    "у вас что-то болит?": "доктор принесёт лекарство",
    "вы хотите пить?": "медсестра позаботится о вас, ожидайте",
    "вы хотите поговорить с родными?": "я уже решаю этот вопрос",
    "вы хотите продолжить диалог?": "хорошо"
}

replies_order = OrderedDict(zip(replies.keys(), replies.values()))  # сохраним порядок


def milena(say_something):
    """ функция голоса Milena

    Принимает на вход текст и озвучивает его
    """
    subprocess.call(["say", "-v", "Milena", say_something])


def recognize(data_sound):
    """ функция распознавания русской речи

    Принимает на вход ответ пациента == результат отработки ф-ции listen (flac)
    Отправляет сгенерированные данные на url Yandex;
    Возвращает распознанный текст (str)
    """
    headers = {
        'Authorization': 'Bearer ' + IAM_TOKEN,  # новый токен >> headers
    }

    params = {
        'lang': 'ru-RU',
        'folderId': ID_FOLDER,
        'sampleRateHertz': 48000,
    }

    resp = requests.post(URL, params=params,
                         headers=headers, data=data_sound)  # отправка post-запроса
    decode_resp = resp.content.decode('UTF-8')  # декодируем
    text = json.loads(decode_resp)  # загружаем в json
    if text.get("error_code") is None:
        text = text.get("result")  # текст << json по ключу result
        print(text)
    else:
        raise requests.RequestException('Ошибка на сервере.'
                                        'Попробуйте через некоторое время снова')
    return text


def signal(trek):
    """ функция включения звукового сигнала

    Проигрывает мелодию wav
    """
    wave_obj = sa.WaveObject.from_wave_file(trek)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def main():
    """ функция включения диалога с помощником

    Последовательно задает вопросы;
    Распознает ответ пациента;
    Отвечает.
    """
    recognizer = sr.Recognizer()
    while True:
        for question in replies_order.keys():  # итерируемся по вопросам по порядку
            milena(question)
            with sr.Microphone() as source:  # слушаем ответ пациента
                recognizer.adjust_for_ambient_noise(source,
                                                    duration=0.3)  # настройка микрофона
                data_sound = recognizer.listen(source,
                                               phrase_time_limit=7)  # ответ от пациента
                data_sound = data_sound.get_flac_data()
                recognize_text = recognize(data_sound)  # распознавание ответа
            if recognize_text == "нет":
                continue
            elif recognize_text == "да":
                milena(replies_order[question])
                break
        break


if __name__ == "__main__":
    signal("Harp 1.wav")
    milena("добро пожаловать!, Я ваш робот-медсестра")
    main()
    milena("Будьте здоровы!, до связи")
    signal("Harp 1.wav")
