"""Contrôle du protocole, de ses oracles et de métriques non masquantes."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from evaluation.agent_evaluation import load_cases, oracle, metrics, run, ratio


class EvaluationTests(unittest.TestCase):
    def test_annotated_corpus(self):
        cases=load_cases()
        self.assertEqual(len(cases),45);self.assertEqual(len({c['category'] for c in cases}),8)
        for c in cases:
            self.assertEqual(c['reference_values'],[oracle(ref,c['context']) for ref in c['references']])
            self.assertTrue(c['justification']);self.assertTrue(c['question'])

    def test_duplicate_missing_and_forged_reference_rejected(self):
        source=json.loads(Path('evaluation/scenarios.json').read_text())
        for kind in ['duplicate','missing','forged']:
            data=copy.deepcopy(source)
            if kind=='duplicate':data['scenarios'][1]['id']=data['scenarios'][0]['id']
            elif kind=='missing':data['scenarios'][0].pop('justification')
            else:data['scenarios'][0]['reference_values'][0]['answer']='inventé'
            with tempfile.TemporaryDirectory() as folder:
                p=Path(folder)/'bad.json';p.write_text(json.dumps(data))
                with self.assertRaises(ValueError):load_cases(p)

    def test_independent_numeric_oracles(self):
        context={'role':'analyste'}
        month=oracle({'kind':'sales','period':{'start_date':'2026-09-01','end_date':'2026-09-30'}},context)
        self.assertEqual(month['order_count'],87)
        self.assertEqual(month['ordered_amount_mad'],'109544.30')
        self.assertEqual(month['paid_amount_mad'],'66261.30')
        self.assertEqual(month['realized_revenue_mad'],'29157.20')
        order=oracle({'kind':'order','order_id':'CMD-DEMO-001'},{'role':'client','customer_id':'CLI-001'})
        self.assertEqual(order['expected_delivery_date'],'2026-07-22')
        self.assertEqual(order['order_status'],'livree')

    def test_metric_denominators_and_violations_never_hidden(self):
        row={'passed':True,'category':'permissions','expected_sources':['FAQ-002'],
             'permission_scope':True,'checks':{'status':True,'tools':True,'fidelity':None,'permissions':True},
             'result':{'status':'refused','sources':[]},'permission_violations':[],'id':'test1'}
        other=copy.deepcopy(row);other.update(id='test2',passed=False)
        other['checks'].update(fidelity=False,permissions=False,status=False)
        other['permission_violations']=['protected_response_exposed']
        other['result']={'status':'error','sources':['FAQ-002']}
        m=metrics([row,other])
        self.assertEqual(m['fidelity_controlled'],ratio(0,1))
        self.assertEqual(m['faq_source_coverage'],ratio(1,2))
        self.assertEqual(m['permission_compliance'],ratio(1,2))
        self.assertEqual(m['error_rate'],ratio(1,2))
        self.assertEqual(len(m['permission_violations']),1)
        self.assertIsNone(metrics([])['status_accuracy']['value'])

    def test_reproducible_protocol_without_fixing_observed_failures(self):
        with tempfile.TemporaryDirectory() as folder:
            first=run(folder);second=run(folder)
            self.assertEqual(first,second)
            self.assertEqual(first['metrics']['scenario_pass_rate']['denominator'],45)
            self.assertEqual(first['deterministic_tool_validation']['denominator'],28)
            self.assertEqual(first['metrics']['permission_violations'],[])
            # Le test ne remplace pas les attentes des cas en échec par leur sortie.
            for row in first['scenarios']:
                if row['checks']['status'] is False:self.assertFalse(row['passed'])
            self.assertTrue((Path(folder)/'agent_report.md').exists())
