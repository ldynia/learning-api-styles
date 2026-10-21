#!/usr/bin/env bash

set -Eeuo pipefail

export PIP_UPLOADED_PRIOR_TO=P7D

python -m pip install --upgrade pip --requirement /usr/src/requirements.txt
