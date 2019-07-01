# Реализовать прототип голосового помощника без функции распознавания на русском языке

import speech_recognition as sr
import subprocess as sp

replies = {
    "hello": "hello, Mr. Do you have any trouble?",
    "yes": "Do you want to drink?"
}

def say(text_to_speech):
    sp.call(['say', text_to_speech])
say('welcome to voice assistant')

def __main__():
    rec = sr.Recognizer()
    mic = sr.Microphone()
    say(replies['hello'])
    with mic as source:
        rec.adjust_for_ambient_noise(source)
        audio = rec.listen(source)
        speech_to_text = rec.recognize_google(audio)
    return speech_to_text

__main__()

while __main__() != 'enough':
    if __main__() == 'yes':
        __main__()
print('break')



# return speech_to_text