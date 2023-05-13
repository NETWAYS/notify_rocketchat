.PHONY: lint test coverage

lint:
	python -m pylint notify_rocketchat.py
test:
	python -m unittest -v -b
coverage:
	python -m coverage run -m unittest test_notify_rocketchat.py
	python -m coverage report -m --include notify_rocketchat.py
