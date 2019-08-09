# Учимся использовать API сервиса Yandex SpeechKit




После прочтения статьи вы сможете:

[1. разобраться, что же такое API на простых примерах (mac os)](#1.-подготовимся-<a-name="d"></a>)

[2. познакомиться с сервисом распознавания и синтеза речи от Yandex](#2.-знакомство-с-api-yandex-speechkit)

## 1. Подготовимся <a name="d"></a>

### Активация аккаунта на облаке

Для использования сервиса YSK у вас должна быть почта на Y. 

Заходим на [cloud.yandex](https://cloud.yandex.ru/) и подключаемся. Вуаля – теперь мы на облаке и можно активировать пробный период пользования сервисом. Привяжите карту и вам будет предложен грант на 60 дней. 

Ваш платежный аккаунт должен быть в статусе ACTIVE. Подробности про биллинг можно почитать здесь  https://cloud.yandex.ru/docs/billing/quickstart/

Работаем в облаке через командную строку. CLI
---
Для понимания, как работает распознавание и синтез, мы потренируемся 
в командной строке. Например, в iTerm. 
Давайте вмете [откроем документацию](https://cloud.yandex.ru/docs/cli/quickstart#install) и настроим Интерфейс командной строки Яндекс.Облака (CLI)

Для обращения к API через командную строку установим утилиту cURL. Перед установкой проверьте, возможно, она у вас уже есть ($ curl --version):

    $ brew install curl

Установим CLI c помощью этого скрипта: 

    $ curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

Перезапустите командную оболочку. В переменную окружения PATH добавится путь к исполняемому файлу – install.sh.

Теперь нам нужно, чтобы в CLI заработало автодополнение команд в bash:  

* Если у вас еще нет менеджера пакетов Homebrew, [установите его](https://brew.sh/). Он вам не раз пригодится, обещаю. 
	
* затем ставим пакет bash-completion: 

    ```$ brew install bash-completion```      
	
    и посмотрим, что изменилось  в файлике ~/.bash_profile :

    `````$ open ~/.bash_profile`````
	
~/.bash_profile используется для пользовательских настроек 
	(в частности  – для определения переменных окружения)

Видим, что в конце bash_profile добавились новые строчки:
    # The next line updates PATH for Yandex Cloud CLI.
	...
    # The next line enables shell command completion for yc.
	...

Это значит, что переменная окружения PATH обновилась и можно пользоваться сервисом в через командную строку. 

Выше новых строк вставьте эту:

    if [ -f $(brew --prefix)/etc/bash_completion ]; then
    . $(brew --prefix)/etc/bash_completion
    fi
	
Порядок! 
А теперь пристегнитесь, приступаем к [инициализации](https://cloud.yandex.ru/docs/cli/quickstart#initialize)  и получаем наш первый “ключик” – aouth_token. 
	
    $ yc init

ловите мессадж:

	Welcome! This command will take you through the configuration process.
    Pick desired action:
 	[1] Re-initialize this profile 'default' with new settings
 	[2] Create a new profile
    Please enter your numeric choice:
	
вводите логичную “1”, скопируйте из отдельного окна aouth_token и вставьте. 

Вам предложат выбрать облако (скорее всего у вас оно единственное) и папку (default):

    You have one cloud available: 'cloud' (id = <цифрыибуквывашейпапочки>). 
    It is going to be used by default.
    Please choose folder to use:
    [1] default (id = <цифрыибуквывашейпапочки>)
    [2] Create a new folder

Далее по желанию выберете Compute zone. Пока полоьзователь один - этим можно пренебречь.

Посмотрим, как выглядят настройки профиля CLI:

    $ yc config list

    token: AgAAAAAAHzS2AATuwTpDlcC9LExto-7iIHEWH9o
    cloud-id: b1gthramkv9de6i2ll5n
    folder-id: b1gdt133kktmm89lr51k
    compute-default-zone: ru-central1-b

Штош, мы в шаге от старта! Осталось добыть второй ключ:

    $ yc iam create-token

Полетели!

## 2. Знакомство с API Yandex SpeechKit
	
Представьте простую, максимально идеальную ситуацию без подводных камней типа  “а если..”. Вы организуете закрытую вечеринку и хотите общаться с гостями, ни на что не отвлекаясь. Тем более на тех, кого вы не ждали.

Давайте попробуем создать виртуального дворецкого, который будет встречать гостей и открывать дверь только приглашенным.
Синтезируем текст приветствия прямо из командной строки:

С помощью встроенной в bash команды export запишем данные в переменные:
    
    $ export FOLDER_ID=b1gvmob95yysaplct532
    $ export IAM_TOKEN=CggaATEVAgA… 

Теперь их можно передать в POST-запрос с помощью cURL:

    $ url -X POST \
        -H "Authorization: Bearer ${IAM_TOKEN}" \
        -o speech.raw \
        --data-urlencode "text=Привет, чувак! Назови-ка мне свои имя и фамилию?" \
        -d "lang=ru-RU&folderId=${FOLDER_ID}&format=lpcm&sampleRateHertz=48000\
    &emotion=good&voice=ermil" \
        https://tts.api.cloud.yandex.net/speech/v1/tts:synthesizec
	
   **в командной строке делайте все в одну строку, без “\”**
   
	что внутри запроса:
speech.raw – файл формата LPSM (несжатый звук). Это и есть озвученный текст, который будет сохранен в текущую папку
	lang=ru-RU –  язык текста
	emotion=good – эмоциональный окрас голоса. Пусть будет доброжелательным
voice=ermil – по умолчанию говорит Оксана. Выберем, например, мужской вариант
https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize – url, на который отправляется post-запрос на синтез речи дворецкого

получаем такой
– Чтобы прослушать полученный raw, установим утилиту SoX и сделаем конвертацию в wav:

$ brew install sox
$ sox -r 48000 -b 16 -e signed-integer -c 1 speech.raw speech.wav

speech.wav – готовое приветствие сохраняется в текущую папку.

Для проигрывания wav внутри кода python, можно взять, например, библиотеку simpleaudio. Она простая и не создает других потоков:

import simpleaudio as sa

def wave_play(trek):
wave_obj = sa.WaveObject.from_wave_file(trek)
play_obj = wave_obj.play()
play_obj.wait_done()

	wave_play(speech.wav)

Итак, наш первый гость стоит перед входом на долгожданную party, пытается открыть дверь, и вдруг слышит голос откуда-то сверху:

<“ваш вариант приветствия”>

Поможем дворецкому распознать ответ гостя

Распознаем ответ 

– Создадим аудио-файл, в который вы запишите ответ гостя 

Сделать это можно через встроенный микрофон на вашем ноутбуке разными инструментами. Например, Quick Time Player. Сконвертируйте аудио в формат ogg: outh_quest.ogg.  Можно онлайн в браузере.

– Снова воспользуемся curl и отправим аудио в post-запросе 
	
curl -X POST \
     -H "Authorization: Bearer ${IAM_TOKEN}" \
     -H "Transfer-Encoding: chunked" \
     --data-binary "@outh_quest.ogg" \  "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?topic=general&folderId=${FOLDER_ID}"

Как видно, в запросе передаются те же ключи из нашего профиля CLI, но на другой url.

– Готово! Получаем в ответ json. Ответ гостя находится по ключу “result”:
	
	{"result" : "<имя_и фамилия_гостя>"}

– Теперь вы уже знаете, как синтезировать вердикт дворецкого, например, такой:

	“Мы вам очень рады, <имя_и фамилия_гостя>, но вас нет в списке, сорян”


Отлично! Вы научились распознавать и синтезировать речь, отправляя запросы на API Yandex SpeechKit.


3. Если вам позвонили из Yandex












