.PHONY: lint lint-ruff lint-mypy format test run

lint: lint-ruff lint-mypy

lint-ruff:
	uv run ruff check .

lint-mypy:
	uv run mypy ./src

format:
	uv run ruff format .

test:
	uv run pytest -q -v --cov

run:
	uv run python -m cli.main
