format-check:
	poetry run black --check .

format:
	poetry run black .

lint: format-check
	poetry run flake8 .

test:
	poetry run pytest tests -vvv

test-watch:
	poetry run ptw -- tests -vvv

.PHONY: \
	formatting \
	lint \
	format-check \
	test \
	test-watch
