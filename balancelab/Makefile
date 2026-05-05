.PHONY: install dev test lint serve init

install:
	pip install -e .

dev:
	pip install -e ".[dev,copilot]"

test:
	pytest -v

lint:
	ruff check src/ tests/
	mypy src/

serve:
	balancelab serve

init:
	balancelab init
