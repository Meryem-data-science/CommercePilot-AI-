"""Parcours UI légers avec le moteur Streamlit, réseau interdit."""
import os
import socket
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from src.presentation import scripted_client
from src.agent import run_agent


class StreamlitTests(unittest.TestCase):
    def app(self):
        return AppTest.from_file('app.py', default_timeout=15).run()

    def test_start_and_faq_without_secrets(self):
        with patch.dict(os.environ,{},clear=True), patch.object(socket.socket,'connect',side_effect=AssertionError('réseau interdit')):
            at=self.app()
            self.assertEqual(len(at.exception),0)
            self.assertEqual(at.radio[0].options,['Mock'])
            at.chat_input[0].set_value('Quels sont les délais de livraison ?').run()
            self.assertEqual(len(at.exception),0)
            self.assertEqual(at.session_state.last_result['sources'],['FAQ-002'])
            self.assertEqual(len(at.chat_message),2)

    def test_order_and_refused_order(self):
        at=self.app()
        at.chat_input[0].set_value('Où est ma commande CMD-DEMO-001 ?').run()
        self.assertEqual(at.session_state.last_result['status'],'ok')
        self.assertEqual(len(at.metric),2)
        at.chat_input[0].set_value('Où est ma commande CMD-DEMO-002 ?').run()
        self.assertEqual(at.session_state.last_result['status'],'refused')
        self.assertEqual(at.session_state.last_result['results'],[])
        self.assertEqual(len(at.exception),0)

    def test_context_change_clears_history_and_analytics(self):
        at=self.app()
        at.chat_input[0].set_value('Quels sont les délais de livraison ?').run()
        at.selectbox[0].set_value('analyste').run()
        self.assertEqual(at.session_state.messages,[])
        at.chat_input[0].set_value('Résume les ventes de septembre 2026.').run()
        self.assertEqual(at.session_state.last_result['tools_called'],['sales_summary'])
        self.assertEqual(len(at.metric),3)
        at.button[0].click().run()
        self.assertEqual(at.session_state.messages,[])
        self.assertIsNone(at.session_state.last_result)

    def test_missing_id_and_mixed_forbidden(self):
        at=self.app()
        at.chat_input[0].set_value('Où est ma commande ?').run()
        self.assertEqual(at.session_state.last_result['status'],'clarification')
        q='Quels sont les délais de livraison ? Et résume les ventes de septembre 2026.'
        r=run_agent(q,{'role':'client','customer_id':'CLI-001'},client=scripted_client(q))
        self.assertEqual(r['status'],'refused');self.assertEqual(r['tools_called'],[])
        self.assertEqual(len(at.exception),0)

    def test_client_and_mode_changes_clear_protected_context(self):
        at=self.app()
        at.chat_input[0].set_value('Où est ma commande CMD-DEMO-001 ?').run()
        at.selectbox[1].set_value('CLI-002').run()
        self.assertEqual(at.session_state.messages,[])
        with patch.dict(os.environ,{'GROQ_API_KEY':'factice','GROQ_MODEL':'fictif'}):
            at=self.app()
            at.chat_input[0].set_value('Quels sont les délais de livraison ?').run()
            at.radio[0].set_value('Groq').run()
            self.assertEqual(at.session_state.messages,[])
            self.assertEqual(len(at.exception),0)
