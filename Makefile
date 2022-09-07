.PHONY: lint test

lint:
	python -m pylint notify_rocketchat.py
test:
	python -m unittest -v -b
