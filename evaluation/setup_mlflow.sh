#!/usr/bin/env bash
# Cloud-only, optional Python 3.11 environment. Does not run an evaluation.
set -euo pipefail
cd -- "$(dirname -- "$0")/.."
mkdir -p work/mlflow
export MLFLOW_DISABLE_TELEMETRY=true
export MLFLOW_DISABLE_AGENT_HINT=true
export UV_CACHE_DIR="$PWD/work/mlflow/uv-cache"
export UV_PYTHON_INSTALL_DIR="$PWD/work/mlflow/python"
python3 -m venv work/mlflow/bootstrap
work/mlflow/bootstrap/bin/python -m pip install --disable-pip-version-check 'uv==0.13.5'
work/mlflow/bootstrap/bin/python -m uv venv --python 3.11.14 --seed --allow-existing work/mlflow-env
work/mlflow-env/bin/python -m pip install --disable-pip-version-check -r requirements-evaluation.txt
work/mlflow-env/bin/python - <<'PY'
import sys
import mlflow
assert sys.version_info[:3] == (3, 11, 14)
assert mlflow.__version__ == '3.18.0'
print('Ready: Python 3.11.14 / MLflow 3.18.0; no evaluation run created.')
PY
