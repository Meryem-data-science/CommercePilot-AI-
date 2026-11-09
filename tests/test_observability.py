"""Télémétrie sans prompts, valeurs confidentielles ni dépendance réseau."""
import copy
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from src.agent import run_agent
from src.llm_client import MockClient, ProviderError
from src.observability import observed, trace_sink, summarize, write_trace
from test_tool_selection import CLIENT, FAQ, faq_call


class ObservabilityTests(unittest.TestCase):
    def test_event_structure_and_unique_ids(self):
        events=[]
        with trace_sink(events.append):
            for _ in range(2):run_agent(FAQ,CLIENT,client=MockClient([{'calls':[faq_call()]}]))
        self.assertNotEqual(events[0]['request_id'],events[1]['request_id'])
        for e in events:
            self.assertEqual(e['status'],'ok');self.assertEqual(e['tool_count'],1)
            self.assertEqual(e['tools_called'],['search_faq'])
            self.assertGreaterEqual(e['duration_ms'],0);self.assertIn('+00:00',e['timestamp'])
            self.assertEqual(e['final_answer'],{'category':'ok','content':'not_retained'})

    def test_no_content_can_escape_from_arbitrary_answer(self):
        secret='gsk_FAKE_PRIVATE_CLI-001_CMD-DEMO-001@example.com'
        @observed
        def example(*args):
            return {'status':'ok','answer':secret,'results':[secret],'tools_called':[], 'error_type':None}
        events=[]
        with trace_sink(events.append):r=example(secret)
        self.assertEqual(r['answer'],secret)
        self.assertNotIn(secret,json.dumps(events))
        for word in ['gsk_', 'CLI-', 'CMD-DEMO-', '@example', 'answer_text', 'reasoning']:
            self.assertNotIn(word,json.dumps(events))

    def test_sink_failure_leaves_result_unchanged(self):
        q=lambda:MockClient([{'calls':[faq_call()]}])
        events=[]
        with trace_sink(events.append):expected=run_agent(FAQ,CLIENT,client=q())
        with trace_sink(lambda e:(_ for _ in ()).throw(OSError('secret'))):
            actual=run_agent(FAQ,CLIENT,client=q())
        self.assertEqual(actual,expected)

    def test_statuses_distinguished(self):
        events=[]
        with trace_sink(events.append):
            run_agent('Annule CMD-DEMO-001',CLIENT)
            run_agent('Où est ma commande ?',CLIENT)
            run_agent(FAQ,CLIENT,client=MockClient([ProviderError('secret')]))
        self.assertEqual([e['status'] for e in events],['refused','clarification','error'])
        m=summarize(events)
        self.assertEqual(m['error_count'],1);self.assertEqual(m['refusal_count'],1)
        self.assertEqual(m['clarification_count'],1);self.assertEqual(m['technical_error_count'],1)

    def test_exact_metric_formulas_and_empty_sample(self):
        events=[{'status':s,'duration_ms':d,'tool_count':c,'error_type':e} for s,d,c,e in
                [('ok',10,1,None),('error',20,0,'provider'),('refused',30,0,'access_denied'),('clarification',40,0,'clarification')]]
        result=summarize(events)
        self.assertEqual(result['mean_latency_ms'],25);self.assertEqual(result['p95_latency_ms'],40)
        self.assertEqual(result['error_rate'],.25);self.assertEqual(result['refusal_rate'],.25)
        self.assertEqual(result['mean_tools_per_request'],.25)
        self.assertIsNone(summarize([])['p95_latency_ms'])
        for value in [-1,float('nan'),float('inf')]:
            bad=copy.deepcopy(events);bad[0]['duration_ms']=value
            with self.assertRaises(ValueError):summarize(bad)

    def test_unexpected_exception_not_swallowed_or_logged(self):
        @observed
        def failing():raise RuntimeError('private reasoning secret')
        events=[]
        with trace_sink(events.append),self.assertRaises(RuntimeError):failing()
        self.assertEqual(events[0]['error_type'],'unhandled')
        self.assertNotIn('private',json.dumps(events))

    def test_private_jsonl_writer(self):
        with tempfile.TemporaryDirectory() as tmp,patch('src.observability.PATH',Path(tmp)/'events.jsonl'):
            write_trace({'safe':True})
            file=Path(tmp)/'events.jsonl'
            self.assertEqual(json.loads(file.read_text()),{'safe':True})
            self.assertEqual(file.stat().st_mode & 0o777,0o600)

    def test_metadata_failure_also_leaves_agent_usable(self):
        with patch('src.observability.uuid.uuid4',side_effect=OSError('private')):
            result=run_agent(FAQ,CLIENT,client=MockClient([{'calls':[faq_call()]}]))
        self.assertEqual(result['status'],'ok')

    def test_untrusted_metadata_and_p95_rank(self):
        @observed
        def example():
            return {'status':'error','tools_called':['secret','search_faq'], 'error_type':'private_value'}
        events=[]
        with trace_sink(events.append):example()
        self.assertEqual(events[0]['tools_called'],['search_faq'])
        self.assertEqual(events[0]['error_type'],'other')
        self.assertNotIn('private_value',json.dumps(events))
        sample=[dict(status='ok',duration_ms=i,tool_count=0,error_type=None) for i in range(1,21)]
        self.assertEqual(summarize(sample)['p95_latency_ms'],19)
