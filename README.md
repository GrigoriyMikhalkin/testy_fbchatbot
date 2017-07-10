# Чатбот для facebook

Ссылка на чатбота: https://www.facebook.com/Testy-the-chatbot-191383118059500/


## Преварительные требования для запуска

    python 3.6

    pip install -r requirements.txt

## Запуск

    python app.py

## Установка чатбота

    ./setup_messenger.sh

## Тренировка классификатора

    python train_classifier.py

## Запуск тестов

Установить переменные среды:

  MONGODB_TEST_HOST -- URI для инсталляции MongoDB, без указания имени DB
  MONGODB_TEST_NAME -- Имя тестовой DB

Например:

    python -m unittest tests.server_tests
