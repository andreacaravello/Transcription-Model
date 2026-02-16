.PHONY: venv install build up down logs

venv:
	python3 -m venv .venv
	source .venv/bin/activate && pip install --upgrade pip

install: venv
	source .venw/bin/activate && pip install -r requirements.txt

build:
	docker build -t transcriber .

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f
