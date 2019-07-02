# Реализовать прототип голосового помощника без функции распознавания на русском языке

import speech_recognition as sr
import subprocess as sp

replies = {
    "yes": "Do you want to drink?",
    "enough": "if you need anything, call me. good bye!"
}

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
        if speech_to_text == "enough":  # выход из цикла
            say(replies.get("enough"))
            break
        elif speech_to_text == "yes" or "no":  # если ответ "да" или "нет", цикл продолжаем
            say(replies.get('yes'))


if __name__ == '__main__':
    main()
