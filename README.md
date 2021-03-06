Голосовой помощник Милена для стационаров клиник
================================================

Милена автоматизирует рутинные задачи медсестер 
в травматологии, такие как: "принести обезболивающее" 
или "помочь с туалетом". У медсестры останется больше времени
для общения с больными.


**В разработке Милены использованы технологии:**
- Yandex Speech Kit (распознавание и синтез)
- SQLAlchemy (для список задач)
- Speech Recognition (получение ответа от пациента 
    через микрофон в аудио)
- Flask (интерфейс медсестры)
- Pydub (запись синтезированной речи в wav)
- Simpleaudio (воспроизведение аудио)

Для работы Милены необходим сервисный аккаунт на Yandex.
Подробная документация по работе в облаке: [speechkit/quickstart](https://cloud.yandex.ru/docs/speechkit/quickstart)

Для общения с помощником используется встроенный микрофон. 

Установим необходимые зависимости:

    $ pip install -r requirements.txt

Для хранения, чтения и записи токенов и id-папки на облаке создадим файл settings.ini.
Эти данные понадобятся для обработки запросов на API:
    
    [Settings]
    oauth_token = AgAAAAAAH...
    iam_token = CggaATEVAg...
    expires_iam_token = 2019-08-13T21:45:20.342867Z
    id_folder = b1gd...

В словарь REPLIES записаны вопросы пациенту. Они основаны на базовых 
потребностях пациентов в травмотологии.

Милена пока умеет работать с одним пациентом.

