import requests
import time
import json

import pyglet
import speech_recognition as sr
import subprocess


IAM_TOKEN = "CggaATEVAgAAABKABJJx5U9Z0-5jdng2gH8Z3-IK_4CCGUzDSv6MPT7fuGs9wwWdACF6gpSaPIzJ7_qTLHobF2dABEZx8evRci7Y-ilZBfrWZe9Tsa1EO7vEYCDLD1Fb2Yt8ZshDAC1XliDLrRDixT6wmka4ObKChqcmyi51IbWXoGowHAvBZAXMWO3gk_L-leiKsYNUMNPOgZQ4uq8Ld8SGJu3bBXs88-xw2eYVlHKP_MdmWa4AW6oVN4pHnDPvGZgSs101qXaG3rFYomU30GDGzlxqJFSmWFCjA-ZTHlLoTCLFCWryIZX94jx_P1PwWTcxRZgmdDAWAC7qOpiMtkWaeTh7Ud7ymUQDUikhYHoaqiS51H8WufuH-qRAWrZ2YvvlRT8yxMyo3CdWGCGj1ZNukoav6D62I1gfjmFZI3w_OF6ZuvwTzwcuHmCA0yuMX5CaJZzw_MM6io-39QE8g1mvKZ09tkL5BWNVbOwzg_r5m9LdXE8vjdfCbafecTp1tdZ2u6cR8ikZgbfUAqizV4E2MfcietqYGbpuHmS-jFZfJNxPhDWY9DLAiphRYN5vIoT3OP9SnLX7S0UW-azLgDfiuZPKXhzKB8ZrRQ5GcdpiDsnV2Nv-BgMyYA7NcQWj0zwzRyRiAaH9xxXRZIKoE3XM6iXuvhtka7t6VnoqbimyiiaKl6whJRyJ2bWIGmEKIDNjZDVkZDdlYWVlNTQ3ZDI4MTQ4MmVlNjVjNjIyNWVkEPWS3ugFGLXk4OgFIh8KFGFqZTJuYmdpdjYxYTB1YmJnMTE0EgdsYWR5a290WgAwAjgBSggaATEVAgAAAFABIPAE"
FOLDER_ID = "b1gb67gpn957qc6ctltf"
URL = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"


replies = {
    "привет": "hello, patient, do you have any pain?",
    "да": "the doctor will bring medicine",
    "я все": "good bye, bless you"
}


# функция включения звукового сигнала
def signal():
    music = pyglet.resource.media('Harp 1.wav')
    music.play()


def recognize(data_sound):
    headers = {
        'Authorization': 'Bearer ' + IAM_TOKEN,
    }

    params = {
        'lang': 'ru-RU',
        'folderId': FOLDER_ID,
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
            #  subprocess.call(["say", "say something"])  # быстро надоест это слушать
            recognizer.adjust_for_ambient_noise(source)  # настройка микрофона
            data_sound = recognizer.listen(source, phrase_time_limit=7)  # пациент что-то отвечает ..> data_sound
            data_sound = data_sound.get_flac_data()

        recognize_text = recognize(data_sound)  # ответ пациента распознается через Yandex Api, получаем в результате текст

        subprocess.call(["say", replies.get(recognize_text.lower())])
        if recognize_text == "я все":
            signal()
            time.sleep(5)  # необходимое время для выполнения signal()
            break


if __name__ == "__main__":
    subprocess.call(["say", "welcome to voice helper"])  # Приветствие
    subprocess.call(["say", "speak after the signal"])
    signal()
    main()
