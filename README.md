# hotel_business
Подмодуль с бизнес-логикой и взаимодействием с БД.

В данном репозитории содержится бизнесс логика для управления отелем, которая используется в нескольких других проектах. 

Приемущественно тут содержатся CRUD операции, но также есть и дополнительные функции, на подобие отправки писем.

В моделях сосредоточена только логика хранения данных (описание таблиц и валидаторы), взаимодействие c БД происходит по шаблону TableGateway, для всех основных моделей есть свой класс gateway, в котором хранится логика обработки данных и основные use-cases приложения.

Также имеются тесты, для проверки корректности работы части функций и настроен MakeFile. MakeFile по команде make test запускает тесты и выводит в консоль процент покрытия кода.
