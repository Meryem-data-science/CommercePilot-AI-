"""Read back a persisted local MLflow evaluation without rerunning the agent."""
import argparse
import json
import math
import os
from pathlib import Path

from evaluation.agent_evaluation import ROOT, load_cases
from evaluation.mlflow_evaluation import EVIDENCE, SCORE_NAMES, local_store, private_path
from quality.check import secret_issues


def verify(evidence=EVIDENCE):
    os.chdir(ROOT)
    os.environ['MLFLOW_DISABLE_TELEMETRY'] = 'true'
    os.environ['MLFLOW_DISABLE_AGENT_HINT'] = 'true'
    import mlflow
    from mlflow.tracking import MlflowClient

    proof = json.loads(private_path(evidence).read_text())
    uri, _ = local_store(proof['store'])
    mlflow.set_tracking_uri(uri)
    client = MlflowClient(tracking_uri=uri)
    run = client.get_run(proof['run_id'])
    assert run.info.status == 'FINISHED'
    native_metrics = {}
    for name in SCORE_NAMES:
        values = [p['scores'][name] for p in proof['scores'] if p['scores'][name] is not None]
        expected = sum(values) / len(values)
        actual = run.data.metrics[f'{name}/mean']
        assert math.isclose(actual, expected, rel_tol=1e-12), name
        native_metrics[name] = {'sum': sum(values), 'count': len(values), 'mean': actual}
    for key, value in proof['logged_metrics'].items():
        assert run.data.metrics[key] == value, key
    traces = mlflow.search_traces(locations=[proof['experiment_id']], run_id=proof['run_id'],
                                 return_type='list', include_spans=True, max_results=100)
    assert len(traces) == 45
    seen = set()
    for trace in traces:
        sid = trace.data.spans[0].inputs['scenario_id']
        assert sid not in seen
        seen.add(sid)
        expected = next(p['scores'] for p in proof['scores'] if p['inputs']['scenario_id'] == sid)
        actual = {a.name: a.value for a in trace.info.assessments if a.name in SCORE_NAMES}
        assert actual == {k: v for k, v in expected.items() if v is not None}
    assert seen == set(proof['trace_ids'])
    for artifact in ('protocol_summary.json', 'scenario_scores.json', 'known_failures.json',
                     'installed_versions.json', 'run_summary.md', 'mlflow_evaluation.py'):
        assert Path(client.download_artifacts(proof['run_id'], artifact)).is_file()
    files = [p for p in Path(proof['store']).rglob('*') if p.is_file()]
    issues = secret_issues(files)
    assert not issues, 'Credential scan failed; do not print matching values'
    cases = load_cases()
    markers = [c['question'].encode() for c in cases] + [b'CMD-DEMO-', b'CLI-']
    for file in files:
        raw = file.read_bytes()
        assert not any(marker in raw for marker in markers), 'Raw fixture content in store'
    result = {
        'experiment_id': proof['experiment_id'], 'run_id': proof['run_id'],
        'persisted_run_status': run.info.status, 'verified_scenarios': len(seen),
        'verified_assessments': sum(m['count'] for m in native_metrics.values()),
        'native_metric_readback': native_metrics,
        'credential_issues': issues, 'store_files_scanned': len(files),
        'raw_questions_or_customer_order_identifiers_detected': False,
        'runs_observed': [{'run_id': r.info.run_id, 'status': r.info.status}
                          for r in client.search_runs([proof['experiment_id']])],
        'artifact_uris_are_absolute': True,
        'privacy_scope': 'Pattern/environment-value scan and exact synthetic fixture questions/IDs; not exhaustive DLP',
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=EVIDENCE)
    parser.add_argument('--out', type=Path, default=Path('work/mlflow/latest_verification.json'))
    args = parser.parse_args()
    out = private_path(args.out)
    result = verify(args.evidence)
    payload = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(payload)
    saved = private_path(Path('work/mlflow/runs') / result['run_id'] / 'verification.json')
    saved.parent.mkdir(parents=True, exist_ok=True)
    saved.write_text(payload)
