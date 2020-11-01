PYTHONEXEC = python3.7.7

clean_cache:
	find . -type d -name '__pycache__' | xargs rm -rf

clean: clean_cache
	rm -rf venv

venv: 
	python -m venv env

deps: venv
	requirements

requirements:
	. env/bin/activate
	pip3 install -r requirements.txt

test: 
	python3 -m unittest

run:
	python3 -m run.py