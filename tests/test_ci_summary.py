"""Le résumé CI ne divulgue aucun détail brut et n'annonce pas un ancien PASS."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from quality.ci_summary import project, markdown, load_fresh


class CiSummaryTests(unittest.TestCase):
    def report(self):
        return json.loads(Path('evaluation/quality_results.json').read_text())

    def test_counts_and_no_raw_details(self):
        data=self.report()
        data['private']='SECRET_PROMPT'
        data['gates'][0]['detail']['private']='SECRET_PROMPT'
        result=project(data,'success')
        self.assertEqual(result['outcome'],'PASS')
        self.assertEqual(len(result['gates']),9)
        self.assertEqual(result['tests']['run'],data['gates'][0]['detail']['run'])
        self.assertEqual(result['evaluation']['scenario_successes'],{'numerator':42,'denominator':45})
        self.assertNotIn('SECRET_PROMPT',json.dumps(result)+markdown(result))

    def test_failed_step_cannot_be_hidden_by_pass_report(self):
        for outcome in ['failure','skipped','cancelled','']:
            self.assertEqual(project(self.report(),outcome)['outcome'],'FAIL')
        data=copy.deepcopy(self.report());data['gates'].pop()
        self.assertEqual(project(data,'success')['outcome'],'FAIL')

    def test_stale_or_missing_report_not_reused(self):
        with tempfile.TemporaryDirectory() as folder:
            report=Path(folder)/'report.json';marker=Path(folder)/'started'
            report.write_text(json.dumps(self.report()));marker.touch()
            os.utime(report,ns=(1,1))
            result=load_fresh(report,marker,'success')
            self.assertEqual(result['outcome'],'FAIL');self.assertIsNone(result['tests']['run'])
            report.write_text('{')
            self.assertEqual(load_fresh(report,marker,'success')['outcome'],'FAIL')

    def test_arbitrary_values_are_never_rendered(self):
        data=self.report();data['gates'][0]['detail']['run']='SECRET_VALUE'
        result=project(data,'success')
        self.assertNotIn('SECRET_VALUE',markdown(result));self.assertIsNone(result['tests']['run'])
        self.assertEqual(result['outcome'],'FAIL')
