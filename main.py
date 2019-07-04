import json
import requests
import subprocess

import settings
import simpleaudio as sa
import speech_recognition as sr


IAM_TOKEN = settings.IAM_TOKEN
ID_FOLDER = settings.ID_FOLDER


replies = {
    "привет": "здравствуйте, пациент, у вас что-то болит?",
    "да": "доктор принес+ёт лекарства",
    "я все": "до связи, будьте здоровы",
}



def recognize(data_sound):  # функция распознавания русской речи
    headers = {
        'Authorization': 'Bearer ' + IAM_TOKEN,  # добваляем новый токен в headers
    }

    params = {
        'lang': 'ru-RU',
        'folderId': ID_FOLDER,
        'sampleRateHertz': 48000,
    }

    resp = requests.post(settings.URL, params=params, headers=headers, data=data_sound)  # отправка post-запроса
    decode_resp = resp.content.decode('UTF-8')  # декодируем
    text = json.loads(decode_resp)  # загружаем в json
    if text.get("error_code") is None:
        text = text.get("result")  # забираем текст из json по ключу result
        print(text)
    else:
        raise requests.RequestException('Ошибка на сервере')
    return text


def signal():  # функция включения звукового сигнала
    wave_obj = sa.WaveObject.from_wave_file("Harp 1.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()


def main():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.3)  # настройка микрофона
            data_sound = recognizer.listen(source, phrase_time_limit=7)  # пациент что-то отвечает ..> data_sound
            data_sound = data_sound.get_flac_data()
        recognize_text = recognize(data_sound)  # ответ пациента распознается через Yandex Api, получаем в результате текст
        subprocess.call(["say", "-v", "Milena", replies.get(recognize_text.lower())])
        if recognize_text == "я все":
            signal()
            break


if __name__ == "__main__":
    subprocess.call("say -v Milena добро пожаловать! Я ваш робот-медсестра".split(" "))  # Приветствие
    subprocess.call("say -v Milena чтобы я вам помогла, скажите после сигнала слово привет".split(" "))  # нужно один раз для нового пациента
    signal()
    main()
