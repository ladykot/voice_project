import json
import requests
import subprocess

import simpleaudio as sa
import speech_recognition as sr

from settings import ID_FOLDER, IAM_TOKEN, URL


replies = {
    "привет": "здравствуйте, пациент, у вас что-то болит?",
    "да": "доктор принес+ёт лекарства",
    "я все": "до связи, будьте здоровы",
}


def recognize(data_sound):  # функция распознавания русской речи
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
            recognizer.adjust_for_ambient_noise(source,
                                                duration=0.3)  # настройка микрофона
            data_sound = recognizer.listen(source,
                                           phrase_time_limit=7)  # ответ от пациента
            data_sound = data_sound.get_flac_data()
        recognize_text = recognize(data_sound)  # распознавание ответа
        subprocess.call(["say", "-v", "Milena",
                         replies.get(recognize_text.lower())])
        if recognize_text == "я все":
            signal()
            break


if __name__ == "__main__":
    subprocess.call("say -v Milena добро пожаловать! "
                    "Я ваш робот-медсестра".split(" "))  # Приветствие
    subprocess.call("say -v Milena чтобы я вам помогла, "
                    "скажите после сигнала слово привет".split(" "))  # 1 раз при знакомстве
    signal()
    main()
