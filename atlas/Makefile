.PHONY: install init pull build snapshot serve test lint clean

install:
	pip install -e ".[dev]"

init:
	atlas init

pull:
	atlas pull

build:
	atlas build-features

snapshot:
	atlas snapshot

serve:
	atlas serve

test:
	pytest -v --tb=short

lint:
	ruff check src/ tests/
	mypy src/

clean:
	rm -rf data/bronze/* data/silver/* data/gold/* data/atlas.duckdb
	@echo "Data lake cleaned."
