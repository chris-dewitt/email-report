.PHONY: install dev test lint bench serve

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

test:
	pytest -v

lint:
	ruff check src/ tests/
	mypy src/

bench:
	pytest benchmarks/ -v --benchmark-only

serve:
	vollab serve
