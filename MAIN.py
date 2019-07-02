# Реализовать прототип голосового помощника без функции распознавания на русском языке

import speech_recognition as sr
import subprocess as sp

replies = {
    "yes/no": "Do you want to drink?",
    "enough": "if you need anything, call me. good bye!"
}   # сочетания ответ-вопрос

choices = ['yes', 'no']  # варианты ответов пациента

def say(text_to_speech):
    sp.call(['say', text_to_speech])

def main():
    say('hello. welcome to voice assistant. Do you have any trouble? Say yes or no.') # произносится 1 раз в начале
    while True:  # бесконечный цикл диалога
        rec = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:   # распознаем ответ с микрофона
            rec.adjust_for_ambient_noise(source)
            audio = rec.listen(source)
            speech_to_text = rec.recognize_google(audio)
        if speech_to_text in choices:  # сопоставляем ответы со списокм choices
            say(replies.get('yes/no'))  # если ответ "да" или "нет", цикл продолжаем
        elif speech_to_text == "enough":  # выход из цикла while
            say(replies.get("enough"))
            break


if __name__ == '__main__':
    main()
