"""Local MLflow UI, optionally behind a PRIVATE GitHub Codespaces forwarded port."""
import os
import json
import re
import subprocess
import sys

from evaluation.agent_evaluation import ROOT
from evaluation.mlflow_evaluation import EVIDENCE, STORE, local_store


def server_command(codespace_name=None):
    uri, artifact_root = local_store(STORE)
    hosts = ['localhost:5000', '127.0.0.1:5000']
    origins = ['http://localhost:5000', 'http://127.0.0.1:5000']
    if codespace_name:
        if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', codespace_name):
            raise ValueError('Invalid Codespaces hostname')
        domain = f'{codespace_name}-5000.app.github.dev'
        hosts.append(domain)
        origins.append(f'https://{domain}')
    return [sys.executable, '-m', 'mlflow', 'server', '--backend-store-uri', uri,
            '--default-artifact-root', artifact_root, '--host', '127.0.0.1',
            '--port', '5000', '--workers', '1', '--no-serve-artifacts',
            '--allowed-hosts', ','.join(hosts), '--cors-allowed-origins', ','.join(origins)]


def main():
    os.chdir(ROOT)
    env = dict(os.environ, MLFLOW_DISABLE_TELEMETRY='true', MLFLOW_DISABLE_AGENT_HINT='true')
    codespace = os.environ.get('CODESPACE_NAME')
    command = server_command(codespace)
    print('MLflow: http://127.0.0.1:5000 — keep forwarded port 5000 PRIVATE', flush=True)
    if (ROOT / EVIDENCE).is_file():
        proof = json.loads((ROOT / EVIDENCE).read_text())
        host = f'https://{codespace}-5000.app.github.dev' if codespace else 'http://127.0.0.1:5000'
        print(f"Latest run: {host}/#/experiments/{proof['experiment_id']}/runs/{proof['run_id']}", flush=True)
    return subprocess.call(command, env=env)


if __name__ == '__main__':
    sys.exit(main())
