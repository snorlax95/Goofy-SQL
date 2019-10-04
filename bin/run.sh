#!/usr/bin/env bash

. "create_venv.sh"

activate_build_venv
with_venv
python3 ../app/main.py
deactivate