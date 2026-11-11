"""Native MLflow GenAI tracking of the existing offline-v1 evaluation.

No agent instrumentation/autologging: only an allowlisted projection is exported.
MLflow is optional and imported exclusively inside run_mlflow().
"""
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.metadata import distributions
import json
import math
import os
from pathlib import Path
import platform
import socket
import subprocess
import time
from unittest.mock import patch

from evaluation.agent_evaluation import ROOT, evaluate_case, load_cases, metrics, ratio

EXPERIMENT = 'CommercePilot-Agent-Evaluation'
PROTOCOL = 'offline-v1'
INTEGRATION_VERSION = 'mlflow-projection-v1'
SCORE_NAMES = ('status_correct', 'tools_correct', 'error_handling_correct',
               'sources_exact', 'faq_source_recall', 'reference_data_correct',
               'factual_fidelity', 'permissions_correct', 'direct_tools_correct',
               'scenario_passed')
STORE = Path('work/mlflow/store')
EVIDENCE = Path('work/mlflow/latest_results.json')


def private_path(path):
    """All new MLflow output stays in the ignored, local work/mlflow tree."""
    path = Path(path)
    private_root = ROOT / 'work/mlflow'
    if (path.is_absolute() or '..' in path.parts or path.parts[:2] != ('work', 'mlflow')
            or not (ROOT / path).resolve().is_relative_to(private_root)):
        raise ValueError('MLflow output must stay under ignored work/mlflow/')
    return path


def reference_check(case, row):
    """Structured data only; distinguish it from the existing factual text check."""
    if case['expected_status'] != 'ok' or not case['references']:
        return None
    outputs = row['result']['results']
    if len(outputs) != len(case['references']):
        return False
    for ref, expected, output in zip(case['references'], case['reference_values'], outputs):
        if output.get('status') != 'ok' or not isinstance(output.get('data'), dict):
            return False
        actual = output['data']
        if ref['kind'] == 'faq':
            if any(actual.get(k) != v for k, v in expected.items()):
                return False
        elif actual != expected:
            return False
    return True


def project(case, row, duration):
    """Never export questions, answers, arguments, identities or raw business data."""
    return {
        'inputs': {'scenario_id': row['id']},
        'outputs': {
            'scenario_id': row['id'], 'category': row['category'],
            'status': row['result']['status'], 'tools': row['result']['tools_called'],
            'sources': row['result']['sources'], 'error_type': row['result']['error_type'],
            'factual_fidelity': row['checks']['fidelity'],
            'reference_data_correct': reference_check(case, row),
            'permissions_correct': row['checks']['permissions'],
            'permission_violations': row['permission_violations'],
            'direct_checks': row['direct_checks'], 'scenario_passed': row['passed'],
            'duration_seconds': duration,
        },
        'expectations': {
            'status': row['expected_status'], 'tools': row['expected_tools'],
            # MLflow Expectation forbids a null value; an envelope preserves null.
            'sources': row['expected_sources'], 'error_type': {'value': case['expected_error']},
        },
    }


def score_values(outputs, expectations):
    """None is not applicable, never an artificial successful assessment."""
    sources = set(expectations['sources'])
    direct = outputs['direct_checks']
    return {
        'status_correct': outputs['status'] == expectations['status'],
        'tools_correct': outputs['tools'] == expectations['tools'],
        'error_handling_correct': outputs['error_type'] == expectations['error_type']['value'],
        'sources_exact': set(outputs['sources']) == sources,
        'faq_source_recall': len(sources & set(outputs['sources'])) / len(sources) if sources else None,
        'reference_data_correct': outputs['reference_data_correct'],
        'factual_fidelity': outputs['factual_fidelity'],
        'permissions_correct': outputs['permissions_correct'],
        'direct_tools_correct': all(d['passed'] for d in direct) if direct else None,
        'scenario_passed': outputs['scenario_passed'],
    }


def collect():
    """Run exactly 45 cases sequentially: the existing evaluator patches global tools."""
    cases = load_cases()
    projections, rows = [], []
    start = time.perf_counter()
    with patch.object(socket.socket, 'connect', side_effect=AssertionError('offline evaluation')), \
         patch.object(socket, 'create_connection', side_effect=AssertionError('offline evaluation')):
        for case in cases:
            t0 = time.perf_counter()
            row = evaluate_case(case)
            projections.append(project(case, row, time.perf_counter() - t0))
            rows.append(row)
    elapsed = time.perf_counter() - start
    historical = json.loads((ROOT / 'evaluation/agent_results.json').read_text())
    hashes = {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest()
              for f in historical['input_sha256']}
    # Keep historical expectations and results immutable; never hide a regression.
    if (rows != historical['scenarios'] or metrics(rows) != historical['metrics']
            or hashes != historical['input_sha256']):
        raise ValueError('Current evaluation differs from historical reference; inspect offline')
    direct = [d for row in rows for d in row['direct_checks']]
    return projections, {
        'metrics': metrics(rows),
        'deterministic_tool_validation': ratio(sum(d['passed'] for d in direct), len(direct)),
        'evaluation_seconds': elapsed,
        'input_sha256': hashes,
    }


def flat_metrics(summary, projections):
    result = {'scenario_count': len(projections),
              'evaluation_seconds': summary['evaluation_seconds'],
              'permission_violation_count': len(summary['metrics']['permission_violations'])}
    for name, value in summary['metrics'].items():
        if isinstance(value, dict) and 'numerator' in value:
            for key in ('numerator', 'denominator', 'value'):
                if value[key] is not None:
                    result[f'protocol.{name}.{key}'] = value[key]
    for category, value in summary['metrics']['by_category'].items():
        for key, number in value.items():
            result[f'category.{category}.{key}'] = number
    for key, value in summary['deterministic_tool_validation'].items():
        result[f'direct_tools.{key}'] = value
    durations = sorted(p['outputs']['duration_seconds'] for p in projections)
    result['mock_case_seconds_mean'] = sum(durations) / len(durations)
    result['mock_case_seconds_p95_nearest_rank'] = durations[math.ceil(.95 * len(durations)) - 1]
    return result


def make_scorers():
    from mlflow.entities import Feedback
    from mlflow.genai.scorers import scorer

    def make(name):
        @scorer(name=name)
        def check(outputs, expectations):
            value = score_values(outputs, expectations)[name]
            return [] if value is None else Feedback(
                name=name, value=value, rationale='Deterministic offline-v1 oracle; no LLM judge')
        return check
    return [make(name) for name in SCORE_NAMES]


def local_store(store):
    """Local SQLite only; MLflow normalizes the artifact root to an absolute URI."""
    store = private_path(store)
    store.mkdir(parents=True, exist_ok=True)
    return f'sqlite:///{store.resolve() / "mlflow.db"}', (store / 'artifacts').as_posix()


def run_mlflow(store=STORE, evidence=EVIDENCE):
    os.chdir(ROOT)
    evidence = private_path(evidence)
    # Explicit local destination; never inherit a remote MLflow/Databricks URI.
    os.environ['MLFLOW_DISABLE_TELEMETRY'] = 'true'
    os.environ['MLFLOW_DISABLE_AGENT_HINT'] = 'true'
    os.environ['MLFLOW_GENAI_EVAL_MAX_WORKERS'] = '1'
    os.environ['MLFLOW_ENABLE_ASYNC_TRACE_LOGGING'] = 'false'
    import mlflow
    from mlflow.tracking import MlflowClient

    if mlflow.__version__ != '3.18.0':
        raise RuntimeError('Install requirements-evaluation.txt (MLflow 3.18.0)')
    uri, artifact_location = local_store(store)
    mlflow.set_tracking_uri(uri)
    client = MlflowClient(tracking_uri=uri)
    experiment = client.get_experiment_by_name(EXPERIMENT)
    eid = experiment.experiment_id if experiment else client.create_experiment(
        EXPERIMENT, artifact_location=artifact_location,
        tags={'protocol_version': PROTOCOL, 'integration_version': INTEGRATION_VERSION, 'mode': 'Mock'})
    mlflow.set_experiment(experiment_id=eid)
    projections, summary = collect()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    params = {'protocol_version': PROTOCOL, 'integration_version': INTEGRATION_VERSION,
              'mode': 'Mock', 'reference_commit': commit, 'python_version': platform.python_version(),
              'mlflow_version': mlflow.__version__, 'scenario_count': len(projections),
              'llm_judge': False, 'network_allowed': False,
              'evaluator_sha256': hashlib.sha256((ROOT / 'evaluation/agent_evaluation.py').read_bytes()).hexdigest(),
              'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    params['working_tree_dirty'] = bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True))
    started = time.perf_counter()
    with mlflow.start_run(run_name='Mock-offline-v1', tags={
            'mode': 'Mock', 'protocol_version': PROTOCOL,
            'scope': 'Imposed plans, not spontaneous Groq routing',
            'projection': 'No raw question, answer, identity, arguments or reasoning'}) as active:
        rid = active.info.run_id
        mlflow.log_params(params)
        # Block networking for the entire native evaluation, including scorers/exporters.
        with patch.object(socket.socket, 'connect', side_effect=AssertionError('offline MLflow')), \
             patch.object(socket, 'create_connection', side_effect=AssertionError('offline MLflow')):
            evaluated = mlflow.genai.evaluate(data=projections, scorers=make_scorers())
        if evaluated.run_id != rid:
            raise RuntimeError('Unexpected native evaluation run')
        recorded_metrics = flat_metrics(summary, projections)
        recorded_metrics['native_scoring_seconds'] = time.perf_counter() - started
        mlflow.log_metrics(recorded_metrics)
        safe_rows = [{**p, 'scores': score_values(p['outputs'], p['expectations'])} for p in projections]
        failures = [p for p in safe_rows if not p['outputs']['scenario_passed']]
        mlflow.log_dict({'scope': 'Mock only; no real model comprehension measured',
                         **summary, 'parameters': params}, 'protocol_summary.json')
        mlflow.log_dict({'scenarios': safe_rows}, 'scenario_scores.json')
        mlflow.log_dict({'failures': failures}, 'known_failures.json')
        mlflow.log_dict({d.metadata['Name']: d.version for d in distributions()},
                        'installed_versions.json')
        passed = summary['metrics']['scenario_pass_rate']['numerator']
        mlflow.log_text('# Mock offline-v1\n\n'
                        f'{len(projections)} scenarios; {passed} passed; no spontaneous LLM routing measured.\n\n'
                        'Known failures: EV-010 (lexical FAQ), EV-016 and EV-022 (completion).\n'
                        'See scenario_scores.json and the native Traces tab for scores.\n'
                        'Null scores are not applicable, never counted as successes.\n'
                        'Protocol metrics retain their original denominators.\n', 'run_summary.md')
        mlflow.log_text(Path(__file__).read_text(), 'mlflow_evaluation.py')
        mlflow.log_text((ROOT / 'requirements-evaluation.txt').read_text(), 'requirements-evaluation.txt')
    # Read back persisted results, not only in-memory EvaluationResult.
    persisted = client.get_run(rid)
    for key, value in recorded_metrics.items():
        if persisted.data.metrics.get(key) != value:
            raise RuntimeError('Persisted metric mismatch')
    mlflow.flush_trace_async_logging()
    traces = mlflow.search_traces(locations=[eid], run_id=rid, max_results=100,
                                 return_type='list', include_spans=True)
    if len(traces) != 45:
        raise RuntimeError(f'Expected 45 persisted evaluation traces, got {len(traces)}')
    assessments = 0
    trace_ids = {}
    for trace in traces:
        payload = json.loads(trace.data.spans[0].inputs) if isinstance(trace.data.spans[0].inputs, str) else trace.data.spans[0].inputs
        sid = payload['scenario_id']
        expected = next(p['scores'] for p in safe_rows if p['inputs']['scenario_id'] == sid)
        actual = {a.name: a.value for a in trace.info.assessments if a.name in SCORE_NAMES}
        if actual != {k: v for k, v in expected.items() if v is not None}:
            raise RuntimeError(f'Persisted per-scenario score mismatch: {sid}')
        assessments += len(actual)
        trace_ids[sid] = trace.info.trace_id
    # Exact artifact readback also proves local artifact paths are functional.
    downloaded = client.download_artifacts(rid, 'scenario_scores.json')
    if json.loads(Path(downloaded).read_text()) != {'scenarios': safe_rows}:
        raise RuntimeError('Persisted scenario artifact mismatch')
    proof = {'experiment_name': EXPERIMENT, 'experiment_id': eid, 'run_id': rid,
             'run_status': persisted.info.status, 'created_at_utc': datetime.now(timezone.utc).isoformat(),
             'parameters': params, 'summary': summary, 'logged_metrics': recorded_metrics,
             'persisted_scenario_count': len(traces), 'persisted_assessment_count': assessments,
             'trace_ids': dict(sorted(trace_ids.items())), 'scores': safe_rows,
             'known_failures': [p['inputs']['scenario_id'] for p in failures],
             'store': str(store), 'verification': 'SQLite run, metrics, trace assessments and artifact read back'}
    # Preserve every proof; latest_results.json is only a pointer to the newest run.
    saved = private_path(Path('work/mlflow/runs') / rid / 'results.json')
    saved.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(proof, ensure_ascii=False, indent=2) + '\n'
    saved.write_text(payload)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text(payload)
    print(json.dumps({k: proof[k] for k in ('experiment_name', 'experiment_id', 'run_id',
          'run_status', 'persisted_scenario_count', 'persisted_assessment_count', 'known_failures')}, indent=2))
    return proof


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store', type=Path, default=STORE)
    parser.add_argument('--evidence', type=Path, default=EVIDENCE)
    args = parser.parse_args()
    run_mlflow(args.store, args.evidence)
