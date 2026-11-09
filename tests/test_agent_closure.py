"""Clôture bornée, couverture des besoins et données métier comme unique source."""
import json
import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import httpx
from groq import Groq
from src.agent import run_agent
from src.llm_client import GroqClient, ProviderError
from src.schemas import load_config
from test_tool_selection import Capture, CLIENT, ANALYST, FAQ, faq_call


def order_call():
    return {'id':'order1','name':'get_order_status','arguments':json.dumps({'order_id':'CMD-DEMO-001'})}


class ClosureTests(unittest.TestCase):
    def test_faq_closes_without_second_provider_call(self):
        client=Capture([{'calls':[faq_call()]},ProviderError()])
        r=run_agent(FAQ,CLIENT,client=client)
        self.assertEqual(r['status'],'ok');self.assertEqual(len(client.requests),1)
        self.assertEqual(r['answer'],r['results'][0]['data']['answer']+'\nRéférence : FAQ AtlasShop, FAQ-002.')

    def test_order_closes_with_verified_values(self):
        client=Capture([{'calls':[order_call()]},ProviderError()])
        r=run_agent('Suivi CMD-DEMO-001',CLIENT,client=client)
        self.assertEqual(r['status'],'ok');self.assertEqual(len(client.requests),1)
        self.assertIn('22 juillet 2026',r['answer'])
        self.assertEqual(r['results'][0]['data']['expected_delivery_date'],'2026-07-22')

    def test_analytics_closes_without_second_request(self):
        period={'start_date':'2026-09-01','end_date':'2026-09-30'}
        client=Capture([{'calls':[{'id':'s1','name':'sales_summary','arguments':json.dumps({'period':period})}]}])
        r=run_agent('Ventes septembre 2026',ANALYST,client=client)
        self.assertEqual(r['status'],'ok');self.assertEqual(len(client.requests),1)
        self.assertIn(str(r['results'][0]['data']['order_count'])+' commandes',r['answer'])

    def test_two_needs_sequential(self):
        client=Capture([{'calls':[faq_call()]},{'calls':[order_call()]},{'calls':[]}])
        r=run_agent('Délais livraison et suivi CMD-DEMO-001',CLIENT,client=client)
        self.assertEqual(r['status'],'ok');self.assertEqual(r['tools_called'],['search_faq','get_order_status'])
        self.assertEqual([x[2]['tool_choice'] for x in client.requests],['required','auto','auto'])
        self.assertIn('FAQ-002',r['answer']);self.assertIn('CMD-DEMO-001',r['answer'])

    def test_missing_need_not_reported_as_complete(self):
        client=Capture([{'calls':[faq_call()]},{'calls':[]}])
        r=run_agent('Délais livraison et suivi CMD-DEMO-001',CLIENT,client=client)
        self.assertEqual(r['status'],'clarification');self.assertEqual(r['error_type'],'incomplete_plan')
        self.assertEqual(r['results'],[])

    def test_unrecognized_extra_request_indicated_partial(self):
        client=Capture([{'calls':[faq_call()]},{'calls':[]}])
        r=run_agent('Délais livraison et conseils personnalisés',CLIENT,client=client)
        self.assertEqual(r['status'],'clarification');self.assertIn('Résultats partiels',r['answer'])
        self.assertEqual(len(client.requests),2)

    def test_ambiguity_does_not_close_on_unrelated_success(self):
        client=Capture([{'calls':[faq_call()]},{'calls':[]}])
        r=run_agent('Où est ma commande ?',CLIENT,client=client)
        self.assertEqual(r['status'],'clarification')
        self.assertEqual(len(client.requests),2)

    def test_access_denied_and_errors_never_close(self):
        for result,expected in [({'status':'access_denied'},'refused'),({'status':'data_error'},'error')]:
            with patch.dict('src.agent.TOOLS',{'search_faq':lambda q:result}):
                r=run_agent(FAQ,CLIENT,client=Capture([{'calls':[faq_call()]}]))
            self.assertEqual(r['status'],expected);self.assertEqual(r['results'],[])
        with patch.dict('src.agent.TOOLS',{'search_faq':lambda q:(_ for _ in ()).throw(ValueError('confidentiel'))}):
            r=run_agent(FAQ,CLIENT,client=Capture([{'calls':[faq_call()]}]))
        self.assertEqual(r['error_type'],'tool_error');self.assertNotIn('confidentiel',json.dumps(r))

    def test_iteration_and_call_budgets(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg=load_config();cfg['max_iterations']=1;cfg['max_tool_calls']=1
            path=Path(tmp)/'config.json';path.write_text(json.dumps(cfg))
            r=run_agent(FAQ,CLIENT,client=Capture([{'calls':[faq_call()]}]),config_path=path)
            self.assertEqual(r['status'],'ok') # plus de tour inutile pour clôturer
            r=run_agent('Délais livraison et suivi CMD-DEMO-001',CLIENT,client=Capture([{'calls':[faq_call()]}]),config_path=path)
            self.assertEqual(r['error_type'],'iteration_limit')
            r=run_agent('Délais livraison et suivi CMD-DEMO-001',CLIENT,client=Capture([{'calls':[faq_call(),order_call()]}]),config_path=path)
            self.assertEqual(r['error_type'],'tool_limit');self.assertEqual(r['tools_called'],[])

    def test_unrelated_faq_query_cannot_satisfy_delivery_need(self):
        c=faq_call();c['arguments']=json.dumps({'query':'moyens de paiement'})
        client=Capture([{'calls':[c]},{'calls':[]}])
        r=run_agent(FAQ,CLIENT,client=client)
        self.assertEqual(r['status'],'clarification')
        self.assertEqual(r['error_type'],'incomplete_plan')
        self.assertEqual(len(client.requests),2)

    def test_gpt_oss_low_reasoning_and_truncated_call_not_executed(self):
        for model in ['openai/gpt-oss-20b','openai/gpt-oss-120b','autre-modele']:
            requests=[]
            def handler(request):
                payload=json.loads(request.content);requests.append(payload)
                if model.startswith('openai/gpt-oss-'):
                    self.assertEqual(payload['reasoning_effort'],'low')
                else:
                    self.assertNotIn('reasoning_effort',payload)
                self.assertEqual(payload['max_completion_tokens'],512)
                c=faq_call()
                return httpx.Response(200,json={'choices':[{'index':0,'finish_reason':'length','message':{'role':'assistant','content':None,'tool_calls':[{'id':c['id'],'type':'function','function':{'name':c['name'],'arguments':c['arguments']}}]}}]})
            def factory(**kwargs):
                self.assertEqual(kwargs['max_retries'],0)
                return Groq(**kwargs,http_client=httpx.Client(transport=httpx.MockTransport(handler)))
            with patch.dict(os.environ,{'GROQ_API_KEY':'factice','GROQ_MODEL':model}),patch('groq.Groq',side_effect=factory):
                r=run_agent(FAQ,CLIENT,client=GroqClient())
            self.assertEqual(r['error_type'],'provider');self.assertEqual(r['tools_called'],[])
            self.assertEqual(len(requests),1)
