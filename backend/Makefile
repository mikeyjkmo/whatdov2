format-check:
	poetry run black --check .

format:
	poetry run black .

type-check:
	poetry run mypy .

lint: format-check type-check
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
	test-watch \
	type-check
