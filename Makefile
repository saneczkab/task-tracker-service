build:
	docker compose build

up:
	docker compose up

down:
	docker compose down

test:
	python -m pytest

check_lint:
	docker compose run --rm backend ruff check .
	docker compose run --rm frontend npx prettier --check .

format:
	docker compose run --rm backend ruff format .
	docker compose run --rm backend ruff check --fix .
	docker compose run --rm frontend npx prettier --write .
