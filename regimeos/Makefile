.PHONY: install dev test lint serve

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
	regimeos serve
