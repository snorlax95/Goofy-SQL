#!/usr/bin/env bash


set_venv() {
     export VENV="../venv/sql_gui"

     if [[ ! -d "$VENV" ]]; then
        echo "Creating virtual environment $VENV"
        python3 -m venv $VENV
    fi
}

with_venv () {
    . "$VENV/bin/activate"
}

activate_build_venv () {
  with_venv
  pip3 install --upgrade pip > /dev/null
  pip3 install -r "../build_requirements.txt" > /dev/null
  pip3 install -r "../app/requirements.txt" > /dev/null
}


if [[ ! -z "${#VENV}" ]]; then
    set_venv
fi