import json
import logging
import requests
from collections import OrderedDict

import simpleaudio as sa
import speech_recognition as sr
from pydub import AudioSegment

from webapp.create_token_copy import create_token, read_config
from webapp.model import db, Tasks

REPLIES = OrderedDict([
    ("Болит у вас что-нибудь?", ("доктор принесёт лекарство", "Принести обезболивающее")),
    ("Хотите в туалет?", ("медсестра уже идёт к вам на помощь", "Помочь с туалетом")),
    ("Хотите пить?", ("медсестра позаботится о вас, ожидайте", "Дать питьё")),
    ("Желаете поговорить с родными?", ("я уже решаю этот вопрос", "Найти родных")),
    ("Продолжим диалог?", ("хорошо, попробуем снова", ))
    ])

# tasks_list = [value[1] for value in REPLIES.values() if len(value) == 2]  # список задач по порядку
# tasks_order = OrderedDict([])
pacient_name = "Самый любимый"

URL_REC = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
URL_SYN = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

log_format = '[%(asctime)s] %(level)-8s %(name)-12s %(message)s'
logging.basicConfig(filename="sample.log", format=log_format, level=logging.INFO)


def milena(iam_token, id_folder, text):
    """ Функция синтеза русской речи из текста

    :param iam_token: (str) <-- create_token()
    :param id_folder: (str) <-- read_config()
    :param text: (str)
    :return: sync.wav
    """

    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    data = {
        'text': text,
        'lang': 'ru-RU',
        'folderId': id_folder,
        'speed': 1.0,
        'emotion': 'neutral'
    }

    resp = requests.post(URL_SYN, headers=headers, data=data, stream=True)  # делаем запрос на синтез текста
    if resp.status_code != 200:
        raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))
    with open('sync.ogg', 'wb') as f:
        f.write(resp.content)  # запись в .ogg
    AudioSegment.from_file('sync.ogg').export('sync.wav', format="wav")
    signal('sync.wav')


def recognize(data_sound, iam_token, id_folder):
    """ функция распознавания русской речи

    :param iam_token: результат работы модуля create_token
    :param data_sound: ответ пациента (flac)
    :param id_folder: (str)
    :return text: (str)

    """

    headers = {'Authorization': 'Bearer ' + iam_token}  # iam_token >> headers
    params = {
        'lang': 'ru-RU',
        'folderId': id_folder,
        'sampleRateHertz': 48000,
    }
    response = requests.post(URL_REC, params=params, headers=headers, data=data_sound)  # отправка post-запроса
    decode_resp = response.content.decode('UTF-8')  # декодируем
    text = json.loads(decode_resp)  # загружаем в json
    if text.get('error_code') is None:
        text = text.get('result')  # забираем текст из json по ключу result
        print(f'Пациент .. {text}')
    else:
        print(text.get('error_code'))
        logging.debug('Милена недоступна. Попробуйте позже')
        return False
    return text


def signal(trek):
    """ функция включения звукового сигнала

    :param: trek (wav)

    """
    wave_obj = sa.WaveObject.from_wave_file(trek)
    play_obj = wave_obj.play()
    play_obj.wait_done()


def dialogue(iam_token, id_folder):
    """ Функция итерируется по ключам(question) в replies,
    Милена задает вопросы: milena()
    Пациент отвечает: listen() -> data_sound - ответ пациента (br)
    Yandex SpeechKit распознает: recognize(data_sound) -> текст (str)

    """

    recognizer = sr.Recognizer()
    while True:
        for question in REPLIES.keys():  # итерируемся по вопросам по порядку
            milena(iam_token, id_folder, question)
            with sr.Microphone() as source:  # слушаем ответ пациента
                recognizer.adjust_for_ambient_noise(source,
                                                    duration=0.3)  # настройка микрофона
                data = recognizer.listen(source, )  # записываем ответ пациента
                data_sound = data.get_flac_data()  # ответ -> flac
                recognize_text = recognize(data_sound, iam_token, id_folder)  # распознавание ответа

            if recognize_text == 'нет':
                if question == list(REPLIES.items())[-1][0]:  # если уже последний вопрос
                    return
                else:
                    continue

            elif recognize_text == 'да':
                milena(iam_token, id_folder, REPLIES[question][0])  # ответ Милены -- значение по словарю
                if question == list(REPLIES.items())[-1][0]:
                    continue
                task = REPLIES[question][1]
                save_tasks(pacient_name, task)  # запись задачи в БД


def main_dialogue():
    """ Функция разговора пациента с пощником
    """
    iam_token = create_token()  # генерируем токен ПЕРЕД диалогом
    id_folder = read_config('id_folder')  # читаем с конфига id_folder
    signal('webapp/Harp 1.wav')
    milena(iam_token, id_folder, 'добро пожаловать!, Я ваш голосовой помощник. Отвечайте -- Д+а -- или-Нет')
    dialogue(iam_token, id_folder)
    milena(iam_token, id_folder, 'Бутьте здоровы!, до связи')
    signal('webapp/Harp 1.wav')
    return f"Задачи для пациента: {pacient_name} успешно отправлены медсестре"


def save_tasks(pacient_name, task):
    """ Функция записи задачи (task) для пациента (pacient_name) в БД

    :param pacient_name (str), task (str)
    """
    task_exists = Tasks.query.filter(Tasks.pacient_name == pacient_name, Tasks.task == task).count()
    if not task_exists:
        new_task = Tasks(pacient_name=pacient_name, task=task)  # новая задача по модели БД
        db.session.add(new_task)
        db.session.commit()  # коммитим после добавления задачи


if __name__ == '__main__':
    main_dialogue()























