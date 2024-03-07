SOURCE_DIR=src
TEST_PATH=tests

test:
	pytest --cov-report xml --cov-report term --cov=$(SOURCE_DIR) --junitxml=report.xml $(TEST_PATH)

check_black:
	black --check .

check_isort:
	isort --diff .

check_format: check_black check_isort

isort:
	isort --atomic .

black:
	black .

format: isort black

lint:
	pylint --rcfile=pylintrc $(SOURCE_DIR) $(TEST_PATH)

mypy:
	mypy --ignore-missing-imports $(SOURCE_DIR) $(TEST_PATH)

static_checks: mypy lint
