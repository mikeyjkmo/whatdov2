format-check:
	poetry run isort --check --profile black . && poetry run black --check .

format:
	poetry run isort --profile black . && poetry run black .

clean:
	rm -r .mypy_cache

type-check:
	poetry run mypy .

lint: format-check type-check
	poetry run flake8 .

test:
	poetry run pytest -vvv -m "not db_unit_test" tests

test-watch:
	poetry run ptw -- -vvv -m "not db_unit_test" tests

test-all:
	poetry run pytest tests -vvv

test-watch-all:
	poetry run ptw -- tests -vvv

develop:
	poetry run uvicorn whatdo2.entrypoints.fast_api:app --host 0.0.0.0 --reload

.PHONY: \
	formatting \
	lint \
	format-check \
	test \
	test-watch \
	test-all \
	test-watch-all \
	develop \
	clean
	type-check
