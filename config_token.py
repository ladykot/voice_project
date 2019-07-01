import configparser
import os
import subprocess
import time


def createConfig(path):
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "iam_token", "iam_token")
    with open(path, "w") as config_file:   # записываем изменения
        config.write(config_file)


def crudConfig(path):
    while True:
        if not os.path.exists(path):  # если конфиг-файла нет, создаем
            createConfig(path)

        config = configparser.ConfigParser()  # создаем конфиг-парсер
        config.read(path)  # просим его прочесть конфиг
        result = subprocess.run("yc iam create-token".split(" "),
                                stdout=subprocess.PIPE).stdout.decode('utf-8')  # запуск генерации токена
        config.set("Settings", "iam_token", result)  # меняем значение токена на новое сгенерированное
        with open(path, "w") as config_file:   # записываем изменения
            config.write(config_file)

        try:
            time.sleep(3600 * 12)
        except KeyboardInterrupt:
            print("\nАвтоматичесекая генерация токена приостановлена")
            break

if __name__ == "__main__":
    path = "settings.ini"
    crudConfig(path)
