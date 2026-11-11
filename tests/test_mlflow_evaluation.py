"""Optional MLflow adapter contract tested without installing MLflow or using network."""
import copy
import contextlib
import io
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from evaluation.agent_evaluation import load_cases
from evaluation.mlflow_dashboard import main as dashboard_main, server_command
from evaluation.mlflow_evaluation import (
    EVIDENCE, EXPERIMENT, SCORE_NAMES, collect, flat_metrics, local_store, private_path, project,
    reference_check, score_values,
)


class MLflowEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Path('work/mlflow').mkdir(parents=True, exist_ok=True)
        cls.cases = load_cases()
        cls.projections, cls.summary = collect()
        cls.rows = json.loads(Path('evaluation/agent_results.json').read_text())['scenarios']

    def test_reuses_all_cases_without_changing_reference(self):
        self.assertEqual(len(self.projections), 45)
        self.assertEqual(self.summary['metrics']['scenario_pass_rate']['numerator'], 42)
        self.assertEqual(self.summary['deterministic_tool_validation']['numerator'], 28)
        failures = [p['inputs']['scenario_id'] for p in self.projections if not p['outputs']['scenario_passed']]
        self.assertEqual(failures, ['EV-010', 'EV-016', 'EV-022'])
        self.assertFalse(self.summary['metrics']['permission_violations'])

    def test_projection_excludes_sensitive_and_confidential_content(self):
        row = copy.deepcopy(self.rows[0])
        row['result']['answer'] = 'private answer and private reasoning'
        row['result']['results'].append({'private': 'private payload'})
        case = copy.deepcopy(self.cases[0])
        case['question'] = 'confidential prompt'
        case['context']['customer_id'] = 'secret identity'
        raw = json.dumps(project(case, row, .01))
        for value in ('private answer', 'private reasoning', 'private payload', 'confidential prompt', 'secret identity'):
            self.assertNotIn(value, raw)
        raw = json.dumps(self.projections)
        for value in ('CMD-DEMO-', 'CLI-', '"customer_id"', '"question"', '"answer"', '"arguments"', '"reasoning"'):
            self.assertNotIn(value, raw)

    def test_scores_are_case_specific_and_not_applicable_is_not_success(self):
        expected_assessments = 0
        for p in self.projections:
            values = score_values(p['outputs'], p['expectations'])
            self.assertEqual(set(values), set(SCORE_NAMES))
            self.assertEqual(values['scenario_passed'], p['outputs']['scenario_passed'])
            expected_assessments += sum(v is not None for v in values.values())
            if p['expectations']['status'] != 'ok':
                self.assertIsNone(values['factual_fidelity'])
        self.assertEqual(expected_assessments, 356)

    def test_reference_data_and_text_fidelity_are_distinct(self):
        case, row = self.cases[0], copy.deepcopy(self.rows[0])
        row['checks']['fidelity'] = False
        self.assertTrue(reference_check(case, row))
        row['result']['results'][0]['data']['answer'] = 'wrong'
        self.assertFalse(reference_check(case, row))
        row['result']['results'] = []
        self.assertFalse(reference_check(case, row))

    def test_mutated_status_tools_sources_or_error_is_detected(self):
        p = self.projections[1]
        for key, value, score in [('status', 'error', 'status_correct'),
                                  ('tools', [], 'tools_correct'),
                                  ('sources', [], 'sources_exact'),
                                  ('error_type', 'provider', 'error_handling_correct')]:
            out = copy.deepcopy(p['outputs'])
            out[key] = value
            self.assertFalse(score_values(out, p['expectations'])[score])

    def test_metric_denominators_are_protocol_denominators(self):
        values = flat_metrics(self.summary, self.projections)
        self.assertEqual(values['protocol.fidelity_controlled.denominator'], 24)
        self.assertEqual(values['protocol.faq_source_coverage.denominator'], 13)
        self.assertEqual(values['protocol.permission_compliance.denominator'], 10)
        self.assertEqual(values['protocol.error_rate.numerator'], 6)
        self.assertEqual(values['permission_violation_count'], 0)
        self.assertGreaterEqual(values['mock_case_seconds_p95_nearest_rank'], 0)
        self.assertTrue(all(p['outputs']['duration_seconds'] >= 0 for p in self.projections))

    def test_evaluation_network_is_blocked(self):
        def network_attempt(case):
            socket.create_connection(('example.invalid', 443))
        with patch('evaluation.mlflow_evaluation.evaluate_case', side_effect=network_attempt):
            with self.assertRaisesRegex(AssertionError, 'offline evaluation'):
                collect()

    def test_changed_result_does_not_silently_replace_history(self):
        with patch('evaluation.mlflow_evaluation.evaluate_case', return_value=self.rows[0]):
            with self.assertRaisesRegex(ValueError, 'historical reference'):
                collect()

    def test_remote_or_escaping_store_is_rejected(self):
        for store in ('../remote', '/tmp/store', 'evaluation/store', 'https://remote'):
            with self.assertRaises(ValueError):
                local_store(store)
        self.assertEqual(EXPERIMENT, 'CommercePilot-Agent-Evaluation')
        dependencies = [line for line in Path('requirements.txt').read_text().splitlines()
                        if line.strip() and not line.startswith('#')]
        self.assertFalse(any('mlflow' in line.lower() for line in dependencies))

    def test_future_groq_pilot_is_separate_and_disabled(self):
        plan = json.loads(Path('evaluation/groq_evaluation_plan.json').read_text())
        self.assertNotEqual(plan['experiment_name'], EXPERIMENT)
        self.assertEqual(len(set(plan['case_ids'])), 10)
        self.assertTrue(set(plan['case_ids']) <= {c['id'] for c in self.cases})
        self.assertFalse(plan['execution_enabled'])
        self.assertTrue(plan['requires_explicit_future_authorization'])
        self.assertEqual(plan['automatic_retries'], 0)

    def test_dashboard_binds_loopback_and_allows_only_exact_codespace_origin(self):
        command = server_command('example-private-123')
        self.assertEqual(command[command.index('--host') + 1], '127.0.0.1')
        self.assertNotIn('--disable-security-middleware', command)
        hosts = command[command.index('--allowed-hosts') + 1]
        self.assertNotIn('*', hosts)
        self.assertIn('example-private-123-5000.app.github.dev', hosts)
        self.assertIn('https://example-private-123-5000.app.github.dev', command[-1])
        with self.assertRaises(ValueError):
            server_command('untrusted.example/escape')

    def test_runtime_outputs_and_legacy_results_cannot_be_accidentally_added(self):
        paths = [str(EVIDENCE), 'work/mlflow/store/mlflow.db',
                 'work/mlflow/store/artifacts/trace.json', 'work/mlflow/runs/id/results.json',
                 'evaluation/mlflow_results.json', 'evaluation/mlflow_verification.json',
                 'evaluation/mlflow_quality_verification.json', 'private.db-wal',
                 'commercepilot-mlflow-backup.tar.gz', 'ouvrir-mlflow-commercepilot.zip']
        for path in paths:
            self.assertEqual(subprocess.run(['git', 'check-ignore', '-q', '--no-index', path]).returncode, 0, path)
        tracked = subprocess.check_output(['git', 'ls-files', '--', 'work',
                                          'evaluation/mlflow_results.json',
                                          'evaluation/mlflow_verification.json',
                                          'evaluation/mlflow_quality_verification.json'], text=True)
        self.assertFalse(tracked.strip())

    def test_evidence_paths_stay_inside_private_tree(self):
        for path in ('evaluation/results.json', '../results.json', '/tmp/results.json', 'work/other/results.json'):
            with self.assertRaises(ValueError):
                private_path(path)
        self.assertEqual(private_path(EVIDENCE), EVIDENCE)

    def test_symlink_cannot_redirect_private_output_into_public_data(self):
        with tempfile.TemporaryDirectory(dir='work/mlflow') as folder:
            link = Path(folder) / 'escape'
            link.symlink_to(Path('data').resolve(), target_is_directory=True)
            with self.assertRaises(ValueError):
                private_path(link / 'results.json')

    def test_symlink_at_private_parent_is_also_rejected(self):
        with tempfile.TemporaryDirectory(dir='work/mlflow') as folder:
            root = Path(folder).resolve()
            (root / 'work').symlink_to(Path('data').resolve(), target_is_directory=True)
            with patch('evaluation.mlflow_evaluation.ROOT', root):
                with self.assertRaises(ValueError):
                    private_path('work/mlflow/results.json')

    def test_dashboard_uses_latest_run_id_without_running_agent(self):
        with tempfile.TemporaryDirectory(dir='work/mlflow') as folder:
            proof = Path(folder) / 'results.json'
            proof.write_text(json.dumps({'experiment_id': '7', 'run_id': 'new-run-id'}))
            output = io.StringIO()
            with patch('evaluation.mlflow_dashboard.EVIDENCE', proof), \
                 patch.dict('os.environ', {'CODESPACE_NAME': 'example-private-123'}), \
                 patch('evaluation.mlflow_dashboard.subprocess.call', return_value=0) as call, \
                 contextlib.redirect_stdout(output):
                self.assertEqual(dashboard_main(), 0)
            self.assertIn('https://example-private-123-5000.app.github.dev/#/experiments/7/runs/new-run-id', output.getvalue())
            self.assertIn('server', call.call_args.args[0])
            self.assertNotIn('evaluate', call.call_args.args[0])
