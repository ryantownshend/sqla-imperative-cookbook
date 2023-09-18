#!/bin/bash

# runs gitlab pipeline tests locally
# make sure you are in the python virtual env and the pip packages flake8, black, isort, and mypy are installed!

# args
# -- pytest - run python player tests

set -e

pytest=''

while test $# != 0
do
    case "$1" in
    --pytest) pytest="true" ;;
    esac
    shift
done

echo "===== running mypy... ====="
poetry run mypy

echo "===== running ruff ... ====="
poetry run ruff .


if [[ ${pytest} == "true" ]]; then
  echo "===== running pytest... ====="
  poetry run pytest
fi

echo "====== ALL TESTS PASSED! ======"

echo '
 _______  __   __  _______  _______  _______  _______  _______  __   __   __
|       ||  | |  ||       ||       ||       ||       ||       ||  | |  | |  |
|  _____||  | |  ||       ||       ||    ___||  _____||  _____||  | |  | |  |
| |_____ |  |_|  ||       ||       ||   |___ | |_____ | |_____ |  | |  | |  |
|_____  ||       ||      _||      _||    ___||_____  ||_____  ||__| |__| |__|
 _____| ||       ||     |_ |     |_ |   |___  _____| | _____| | __   __   __
|_______||_______||_______||_______||_______||_______||_______||__| |__| |__|
'
