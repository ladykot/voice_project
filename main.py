import speech_recognition as sr
import subprocess
import pyglet
import time

replies = {
    "hello": "hello, patient, do you have any pain?",
    "yes": "the doctor will bring medicine",
    "enough": "good bye, bless you"
}


def signal():
    music = pyglet.resource.media('Harp 1.wav')
    music.play()


def main():
    recognizer = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            #subprocess.call(["say", "say something"])  # быстро надоест это слушать
            recognizer.adjust_for_ambient_noise(source)  # настройка микрофона
            data_sound = recognizer.listen(source, phrase_time_limit=7)  # пациент что-то отвечает ..> data_sound

        text = recognizer.recognize_google(data_sound)  # ответ пациента распознается через google Api
        print(text)
        subprocess.call(["say", replies.get(text.lower())])
        if text == "enough":
            signal()
            time.sleep(5)  # необходимое время для выполнения signal()
            break

if __name__ == "__main__":
    subprocess.call(["say", "welcome to voice helper"])  # Приветствие
    subprocess.call(["say", "speak after the signal"])
    signal()
    main()
