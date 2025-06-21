
# SimpleSocialNetwork - проект простой социальной сети.


## Пререквизиты:

- docker
- docker-compose
- python3.12
- .env файл с содержимым


```bash
SECRET_KEY=your_secret_key
ALGORITM=HS256
DB__HOST=127.0.0.1
DB__PORT=6432
DB__USERNAME=postgres
DB__PASSWORD=postgres
DB__NAME=socialnetwork
```
    
## Команды для запуска проекта:
```bash
docker compose up -d db
pip install poetry && poetry self add poetry-dotenv-plugin
poetry install
linux: PYTHONPATH=$PWD/src poetry run uvicorn src.main:app
windows: $env:PYTHONPATH="$PWD/src"; poetry run uvicorn src.main:app
```
## Запуск тестов:
```bash
linux: PYTHONPATH=$PWD/src poetry run pytest tests -vv
windows: $env:PYTHONPATH="$PWD/src"; poetry run pytest tests -vv
```