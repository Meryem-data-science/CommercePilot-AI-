"""Régression des paraphrases de suivi : couverture, refus et clôture."""
import json
import unittest
from src.agent import run_agent, completion_needs, clear_tool_request, render_results
from src.llm_client import ProviderError
from src.tools.orders import get_order_status
from test_tool_selection import Capture, CLIENT, ANALYST, faq_call
from test_agent_closure import order_call

QUESTIONS = [
    'Où est ma commande CMD-DEMO-001 ?',
    'Quel est le statut de CMD-DEMO-001 ?',
    'Suivi CMD-DEMO-001',
    'Où en est ma commande CMD-DEMO-001 ?',
    'Ma commande CMD-DEMO-001 a-t-elle été livrée ?',
    '  OU EST MA COMMANDE : cmd-demo-001 ?! ',
    'MA COMMANDE CMD-DEMO-001 A T ELLE ÉTÉ LIVRÉE ???',
]


class OrderIntentTests(unittest.TestCase):
    def test_authorized_variants_close_in_one_request(self):
        expected=get_order_status('CMD-DEMO-001','client','CLI-001')
        for q in QUESTIONS:
            with self.subTest(q=q):
                model=Capture([{'calls':[order_call()]},ProviderError()])
                r=run_agent(q,CLIENT,client=model)
                self.assertEqual(r['status'],'ok')
                self.assertEqual(r['results'],[expected])
                self.assertEqual(r['answer'],render_results(['get_order_status'],[expected]))
                self.assertEqual(len(model.requests),1)
                self.assertEqual(model.requests[0][2]['tool_choice'],'required')

    def test_other_owner_remains_denied(self):
        for q in QUESTIONS[:5]:
            c=order_call();c['arguments']=json.dumps({'order_id':'CMD-DEMO-002'})
            model=Capture([{'calls':[c]}])
            r=run_agent(q.replace('001','002'),CLIENT,client=model)
            self.assertEqual(r['status'],'refused');self.assertEqual(r['results'],[])
            self.assertNotIn('expected_delivery_date',r['answer'])

    def test_missing_id_and_ambiguous_mentions(self):
        for q in ['Où est ma commande ?', 'Quel est le statut ?', 'CMD-DEMO-001',
                  'À propos de CMD-DEMO-001', 'Suivi CMD-DEMO-001 ou CMD-DEMO-002',
                  'Où est ma commande CMD-DEMO-001 et quel temps fera-t-il ?']:
            self.assertIsNone(completion_needs(q,None),q)
            model=Capture()
            r=run_agent(q,CLIENT,client=model)
            self.assertNotEqual(r['status'],'ok')
            self.assertEqual(r['tools_called'],[])

    def test_mutation_and_refund_refused_before_llm(self):
        for q in ['Annule ma commande CMD-DEMO-001',
                  'Où est ma commande CMD-DEMO-001 et rembourse-moi ?',
                  'Modifie CMD-DEMO-001', 'Rembourse CMD-DEMO-001']:
            model=Capture([{'calls':[order_call()]}])
            r=run_agent(q,CLIENT,client=model)
            self.assertEqual(r['error_type'],'security_policy')
            self.assertEqual(model.requests,[]);self.assertEqual(r['results'],[])

    def test_multi_needs_not_closed_after_order_only(self):
        q='Où est ma commande CMD-DEMO-001 ? Et quels sont les délais de livraison ?'
        # Un séparateur ? suivi de et doit rester deux clauses, sans clause vide.
        model=Capture([{'calls':[order_call()]},{'calls':[faq_call()]},{'calls':[]}])
        r=run_agent(q,CLIENT,client=model)
        self.assertEqual(r['status'],'ok')
        self.assertEqual(r['tools_called'],['get_order_status','search_faq'])
        self.assertEqual(len(model.requests),3)
        model=Capture([{'calls':[order_call()]},{'calls':[]}])
        r=run_agent(q,CLIENT,client=model)
        self.assertEqual(r['status'],'clarification');self.assertEqual(r['results'],[])

    def test_analyst_not_forced_and_model_cannot_inject_context(self):
        self.assertFalse(clear_tool_request(QUESTIONS[0],ANALYST,None))
        for extra in [{'role':'administrateur'},{'customer_id':'CLI-002'}]:
            c=order_call();c['arguments']=json.dumps({'order_id':'CMD-DEMO-001',**extra})
            r=run_agent(QUESTIONS[0],CLIENT,client=Capture([{'calls':[c]}]))
            self.assertEqual(r['error_type'],'invalid_arguments');self.assertEqual(r['results'],[])

    def test_requested_sales_formulation_is_complete(self):
        p={'start_date':'2026-09-01','end_date':'2026-09-30'}
        q='Résume les ventes de septembre 2026.'
        self.assertEqual(completion_needs(q,p),[('sales_summary',p)])
        c={'id':'sales','name':'sales_summary','arguments':json.dumps({'period':p})}
        model=Capture([{'calls':[c]},ProviderError()])
        r=run_agent(q,ANALYST,client=model)
        self.assertEqual(r['status'],'ok');self.assertEqual(len(model.requests),1)
