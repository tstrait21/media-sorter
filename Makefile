test:
	PYTHONPATH=src python -m unittest discover -s tests

lint:
	ruff check .
