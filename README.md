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
