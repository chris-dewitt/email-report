.PHONY: install dev init ingest embed event-study serve ui test lint status brief

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

init:
	fedlens init

ingest:
	fedlens ingest --doc-type all

embed:
	fedlens embed

event-study:
	fedlens event-study --all

brief:
	fedlens brief

serve:
	fedlens serve

ui:
	cd frontend && npm run dev

test:
	pytest -v --tb=short

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

format:
	ruff check --fix src/ tests/
	ruff format src/ tests/

status:
	fedlens status
