"""Vérifier qu'une régression ne peut pas être diluée dans le score moyen."""
import json
from pathlib import Path
import tempfile
import unittest
from quality.check import evaluation_verdict, secret_issues


class QualityGateTests(unittest.TestCase):
    def test_frozen_baseline_passes(self):
        report=json.loads(Path('evaluation/agent_results.json').read_text())
        baseline=json.loads(Path('quality/baseline.json').read_text())
        self.assertEqual(evaluation_verdict(report,baseline),[])

    def test_permission_violation_blocks_even_with_good_average(self):
        report=json.loads(Path('evaluation/agent_results.json').read_text())
        base=json.loads(Path('quality/baseline.json').read_text())
        report['scenarios'][0]['checks']['permissions']=False
        self.assertIn('permission_violation',evaluation_verdict(report,base))
        # Hors sous-ensemble sensible : les agrégats peuvent rester identiques,
        # mais le contrôle global doit quand même bloquer.
        self.assertNotIn('metric_mismatch',evaluation_verdict(report,base))

    def test_previously_passing_case_cannot_be_replaced_by_new_success(self):
        report=json.loads(Path('evaluation/agent_results.json').read_text())
        base=json.loads(Path('quality/baseline.json').read_text())
        passed=next(r for r in report['scenarios'] if r['passed'])
        failed=next(r for r in report['scenarios'] if not r['passed'])
        passed['passed']=False;failed['passed']=True
        self.assertIn('previous_success_regressed',evaluation_verdict(report,base))

    def test_metric_tampering_and_direct_regression_fail(self):
        report=json.loads(Path('evaluation/agent_results.json').read_text())
        base=json.loads(Path('quality/baseline.json').read_text())
        report['metrics']['error_rate']['numerator']=0
        report['deterministic_tool_validation']['numerator']=27
        problems=evaluation_verdict(report,base)
        self.assertIn('metric_mismatch',problems);self.assertIn('direct_tools',problems)

    def test_scanner_returns_no_secret_content(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'fixture.txt'
            key='gsk_'+'A'*24
            p.write_text(key)
            issues=secret_issues([p])
            self.assertTrue(issues);self.assertNotIn(key,json.dumps(issues))
            secret=Path(folder)/'.env';secret.write_text('EMPTY=')
            self.assertEqual(secret_issues([secret])[0]['reason'],'sensitive_file')
            p.write_text('Données synthétiques sans secret')
            self.assertEqual(secret_issues([p]),[])
