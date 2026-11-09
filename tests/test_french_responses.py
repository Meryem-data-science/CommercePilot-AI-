"""Rendu français hors ligne : fidélité, précision et absence de fuite."""
import copy
import unittest
from unittest.mock import patch
from src.agent import run_agent, render_results, french_date, french_mad
from src.llm_client import MockClient
from src.tools.orders import get_order_status
from src.tools.faq import search_faq
from src.tools.analytics import sales_summary
from test_tool_selection import Capture, CLIENT, FAQ, faq_call
from test_agent_closure import order_call

PERIOD={'start_date':'2026-09-01','end_date':'2026-09-30'}


class FrenchResponseTests(unittest.TestCase):
    def test_faq_keeps_documentary_text_and_reference(self):
        result=search_faq(FAQ)
        r=run_agent(FAQ,CLIENT,client=Capture([{'calls':[faq_call()]}]))
        self.assertEqual(r['results'],[result]);self.assertEqual(r['sources'],['FAQ-002'])
        self.assertEqual(r['answer'],result['data']['answer']+'\nRéférence : FAQ AtlasShop, FAQ-002.')
        self.assertIn('il ne s’agit pas d’une garantie',r['answer'])

    def test_dates_independent_of_locale(self):
        for iso, expected in [('2026-07-22','22 juillet 2026'),('2026-09-01','1er septembre 2026'),('2024-02-29','29 février 2024'),('2026-12-31','31 décembre 2026')]:
            self.assertEqual(french_date(iso),expected)
        with self.assertRaises(ValueError):french_date('2026-02-30')

    def test_money_exact_without_float_rounding(self):
        for value,expected in [('0.00','0,00 MAD'),('109544.30','109 544,30 MAD'),('1000000000000000000000.01','1 000 000 000 000 000 000 000,01 MAD'),('-1234.05','-1 234,05 MAD')]:
            self.assertEqual(french_mad(value),expected)
        for value in ['123.456','secret',1.01]:
            with self.assertRaises(ValueError):french_mad(value)

    def test_order_fluent_and_json_unchanged(self):
        expected=get_order_status('CMD-DEMO-001','client','CLI-001')
        client=Capture([{'calls':[order_call()]}])
        r=run_agent('Où est ma commande CMD-DEMO-001 ?',CLIENT,client=client)
        self.assertEqual(r['results'],[expected]);self.assertEqual(r['status'],'ok')
        self.assertEqual(len(client.requests),1)
        self.assertEqual(r['answer'],'Selon les données de démonstration au 1er octobre 2026, votre commande CMD-DEMO-001 était livrée. La livraison a eu lieu le 22 juillet 2026, à la date prévue.')

    def test_order_all_statuses_missing_and_different_dates(self):
        original=get_order_status('CMD-DEMO-001','client','CLI-001')
        for status,label in [('en_preparation','en préparation'),('expediee','expédiée'),('annulee','annulée'),('retournee','retournée')]:
            result=copy.deepcopy(original);result['data']['order_status']=status
            result['data']['actual_delivery_date']=''
            before=copy.deepcopy(result)
            answer=render_results(['get_order_status'],[result])
            self.assertIn('était '+label,answer);self.assertNotIn('a eu lieu',answer)
            self.assertIn('22 juillet 2026',answer);self.assertEqual(result,before)
        result=copy.deepcopy(original);result['data']['actual_delivery_date']='2026-07-24'
        answer=render_results(['get_order_status'],[result])
        self.assertIn('a eu lieu le 24 juillet 2026',answer)
        self.assertIn('elle était prévue le 22 juillet 2026',answer)
        self.assertNotIn('à la date prévue',answer)

    def test_analytics_distinguishes_financial_indicators(self):
        result=sales_summary(PERIOD,'analyste');before=copy.deepcopy(result)
        answer=render_results(['sales_summary'],[result])
        self.assertIn('du 1er septembre 2026 au 30 septembre 2026 inclus : 87 commandes',answer)
        self.assertIn('statuts sont ceux du 1er octobre 2026',answer)
        self.assertIn('- Montant total commandé : 109 544,30 MAD.',answer)
        self.assertIn('- Montant des commandes payées : 66 261,30 MAD.',answer)
        self.assertIn('- Chiffre d’affaires réalisé (commandes livrées et payées) : 29 157,20 MAD.',answer)
        self.assertIn('Annulations : 2 (2 082,30 MAD)',answer)
        self.assertIn('retours : 1 (2 252,50 MAD)',answer)
        self.assertIn('Retards : 12, dont 4 pour la livraison initiale et 8',answer)
        self.assertEqual(result,before)

    def test_empty_and_single_order_grammar(self):
        result=sales_summary({'start_date':'2025-09-01','end_date':'2025-09-30'},'analyste')
        answer=render_results(['sales_summary'],[result])
        self.assertIn('Aucune commande n’a été enregistrée',answer);self.assertIn('est donc nul',answer)
        self.assertEqual(result['data']['ordered_amount_mad'],'0.00')
        result['data']['order_count']=1
        self.assertIn('1 commande.',render_results(['sales_summary'],[result]))

    def test_combined_results_keep_all_sources_and_sections(self):
        faq=search_faq(FAQ);order=get_order_status('CMD-DEMO-001','client','CLI-001')
        before=copy.deepcopy([faq,order])
        answer=render_results(['search_faq','get_order_status'],[faq,order])
        self.assertIn('Délais de livraison\n',answer)
        self.assertIn('\n\nLe suivi de votre commande\n',answer)
        self.assertIn('FAQ-002',answer);self.assertIn(faq['data']['answer'],answer)
        self.assertIn('22 juillet 2026',answer);self.assertEqual([faq,order],before)

    def test_unknown_and_other_owner_indistinguishable(self):
        answers=[]
        for oid in ['CMD-DEMO-002','CMD-DEMO-999']:
            c=order_call();c['arguments']='{"order_id":"'+oid+'"}'
            r=run_agent('Suivi '+oid,CLIENT,client=Capture([{'calls':[c]}]))
            self.assertEqual(r['status'],'refused');self.assertEqual(r['error_type'],'access_denied')
            self.assertEqual(r['results'],[]);self.assertEqual(r['sources'],[])
            self.assertNotIn('2026-',r['answer']);self.assertNotIn('CLI-',r['answer'])
            self.assertIn('introuvable ou votre profil',r['answer']);answers.append(r['answer'])
        self.assertEqual(answers[0],answers[1])

    def test_contextual_clarifications_and_partial_label(self):
        for q,expected in [('Où est ma commande ?','numéro de votre commande'),('Résume les ventes','Quelle période'),('Bonjour','Pouvez-vous préciser')]:
            r=run_agent(q,CLIENT,client=MockClient())
            self.assertEqual(r['status'],'clarification');self.assertIn(expected,r['answer'])
        r=run_agent('Délais livraison et conseils personnels',CLIENT,client=Capture([{'calls':[faq_call()]},{'calls':[]}]))
        self.assertEqual(r['status'],'clarification');self.assertIn('Résultats partiels',r['answer'])

    def test_refusals_and_errors_not_positive(self):
        r=run_agent('Annule CMD-DEMO-001',CLIENT,client=MockClient())
        self.assertEqual(r['status'],'refused');self.assertIn('ne peux pas',r['answer'])
        with patch.dict('src.agent.TOOLS',{'get_order_status':lambda *a:{'status':'data_error'}}):
            r=run_agent('Suivi CMD-DEMO-001',CLIENT,client=Capture([{'calls':[order_call()]}]))
        self.assertEqual(r['status'],'error');self.assertEqual(r['results'],[])
        self.assertNotIn('est livrée',r['answer'])
        for status in ['access_denied','data_error']:
            with self.assertRaises(ValueError):render_results(['get_order_status'],[{'status':status}])

    def test_malformed_display_data_returns_safe_error(self):
        result=get_order_status('CMD-DEMO-001','client','CLI-001')
        result['data']['expected_delivery_date']='invalide-confidentiel'
        with patch.dict('src.agent.TOOLS',{'get_order_status':lambda *a:result}):
            r=run_agent('Suivi CMD-DEMO-001',CLIENT,client=Capture([{'calls':[order_call()]}]))
        self.assertEqual(r['error_type'],'tool_error');self.assertEqual(r['results'],[])
        self.assertNotIn('confidentiel',r['answer'])
