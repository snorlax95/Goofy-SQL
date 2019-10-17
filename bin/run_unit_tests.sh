#!/usr/bin/env bash

export BUILD_SCRIPTS_DIR="$(pwd)"
export PROJECT_DIR="$BUILD_SCRIPTS_DIR/.."
export ACCEPTANCE_TEST_DIR="$PROJECT_DIR/acceptance-tests"
export APPLICATION_DIR="$PROJECT_DIR/app"


. "create_venv.sh"


activate_build_venv
with_venv
pushd "$PROJECT_DIR" > /dev/null
echo "Running pytest"
pytest --cov="$APPLICATION_DIR" --junit-xml="test_results.xml" --cov-report term-missing -vs


echo "Generating coverage report"
coverage xml
coverage html -d coverage_html
coverage report --fail-under "90" --skip-covered

deactivate
popd > /dev/null
