format:
	poetry run black src
	poetry run isort src

lint:
	poetry run pylint --disable=duplicate-code src

mypy:
	poetry run mypy src

check: lint mypy
	poetry run isort --check src
	poetry run black --check src

replicate_data:
	poetry run python -m src.maria_to_postgres

load_data:
	poetry run python -m src.data_preparation