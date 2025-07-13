.PHONY: help test lint build

help:
	@echo "Makefile for media-sorter"
	@echo ""
	@echo "Usage:"
	@echo "    make [target]"
	@echo ""
	@echo "Targets:"
	@echo "    help      Show this help message"
	@echo "    test      Run tests"
	@echo "    lint      Run linter"
	@echo "    build     Build the application"

test:
	PYTHONPATH=src python -m unittest discover -s tests

lint:
	ruff check .

build:
	python build.py
