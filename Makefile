FLASK = .venv/bin/flask
PYTHON = .venv/bin/python

.PHONY: run test db-create install lint

install:
	pip install -r requirements.txt --user

venv:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt

db-create:
	$(FLASK) db-create

run:
	$(FLASK) run

test:
	$(PYTHON) -m nose2 -v

lint:
	.venv/bin/flake8 service tests --max-line-length=100
