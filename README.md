В файле itlad/itlad/spiders/parser.py необходимо заменить настройки БД на соответствующие по примеру
"postgresql+psycopg2://user:password@host:port/db_name"

Для установки зависимостей:

pip install -r requirements.txt

или, в случае проблем

pip install pipenv

pipenv shell

pipenv sync

cd itlad

scrapy crawl parser


Схема БД:

<img src="https://raw.githubusercontent.com/Mellolian/it-lad/2e58d1697ef6e94d9195b2f0e7a0b83316a5a8a2/%D0%91%D0%B5%D0%B7%20%D0%BD%D0%B0%D0%B7%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F.png" />
