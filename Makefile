build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

test:
	python -m pytest

check_lint:
	python -m ruff check .
	cd gantt-frontend && npx prettier --check .

format:
	python -m ruff format .
	python -m ruff check --fix .
	cd gantt-frontend && npx prettier --write .
