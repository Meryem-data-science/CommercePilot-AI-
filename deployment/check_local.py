"""Recette locale de déploiement : cinq parcours Mock, aucun service distant."""
import json
import os
from pathlib import Path
import socket
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from src.tools.orders import get_order_status
from src.tools.analytics import sales_summary

ROOT = Path(__file__).resolve().parents[1]


def main():
    previous = Path.cwd()
    os.chdir(ROOT)
    rows = []
    scenarios = [
        ('faq','Quels sont les délais de livraison ?','client','ok',['search_faq']),
        ('order','Où est ma commande CMD-DEMO-001 ?','client','ok',['get_order_status']),
        ('analytics','Résume les ventes de septembre 2026.','analyste','ok',['sales_summary']),
        ('refusal','Où est ma commande CMD-DEMO-002 ?','client','refused',['get_order_status']),
        ('clarification','Où est ma commande ?','client','clarification',[]),
    ]
    try:
        with patch.dict(os.environ,{'GROQ_API_KEY':'','GROQ_MODEL':''}), \
             patch.object(socket.socket,'connect',side_effect=AssertionError('Aucun réseau autorisé')), \
             patch('src.llm_client.GroqClient.complete',side_effect=AssertionError('Groq interdit')):
            for name,question,role,status,tools in scenarios:
                app = AppTest.from_file('app.py',default_timeout=15).run()
                assert not app.exception
                assert app.radio[0].options == ['Mock']
                if role != 'client':
                    app.selectbox[0].set_value(role).run()
                app.chat_input[0].set_value(question).run()
                assert not app.exception
                result = app.session_state.last_result
                assert result['status'] == status and result['tools_called'] == tools
                if name == 'faq':
                    assert result['sources'] == ['FAQ-002']
                elif name == 'order':
                    assert result['results'] == [get_order_status('CMD-DEMO-001','client','CLI-001')]
                elif name == 'analytics':
                    assert result['results'] == [sales_summary({'start_date':'2026-09-01','end_date':'2026-09-30'},'analyste')]
                else:
                    assert result['results'] == [] and result['sources'] == []
                rows.append({'scenario':name,'passed':True,'status':result['status'],'tools':tools})
    finally:
        os.chdir(previous)
    target=ROOT/'work/deployment';target.mkdir(parents=True,exist_ok=True)
    (target/'local_smoke.json').write_text(json.dumps({'scope':'local AppTest only; not a public site validation','scenarios':rows},indent=2)+'\n')
    print(json.dumps(rows,indent=2))


if __name__ == '__main__':
    main()
