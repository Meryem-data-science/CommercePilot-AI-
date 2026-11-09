"""Évaluation locale reproductible : sept interactions mock, aucun appel API."""
import json
from pathlib import Path
import socket
from unittest.mock import patch
from src.agent import run_agent
from src.llm_client import MockClient, ProviderError
from src.observability import trace_sink, summarize

ROOT=Path(__file__).resolve().parent


def call(name,args):
    return {'id':'sample','name':name,'arguments':json.dumps(args)}


def main():
    client={'role':'client','customer_id':'CLI-001'}
    cases=[
        ('Quels sont les délais de livraison ?',client,call('search_faq',{'query':'Quels sont les délais de livraison ?'})),
        ('Où est ma commande CMD-DEMO-001 ?',client,call('get_order_status',{'order_id':'CMD-DEMO-001'})),
        ('Résume les ventes de septembre 2026.',{'role':'analyste'},call('sales_summary',{'period':{'start_date':'2026-09-01','end_date':'2026-09-30'}})),
        ('Où est ma commande CMD-DEMO-002 ?',client,call('get_order_status',{'order_id':'CMD-DEMO-002'})),
        ('Où est ma commande ?',client,None),
        ('Quels sont les délais de livraison ?',client,ProviderError()),
        ('Quels sont les délais de livraison ?',client,call('search_faq',{'query':'Quels sont les délais de livraison ?'})),
    ]
    events=[]
    def tool_failure(*args):raise RuntimeError('simulated failure')
    with trace_sink(events.append),patch.object(socket.socket,'connect',side_effect=AssertionError('réseau interdit')):
        for i,(question,context,step) in enumerate(cases):
            model=MockClient([step if isinstance(step,Exception) else {'calls':[step] if step else []}])
            if i==6:
                with patch.dict('src.agent.TOOLS',{'search_faq':tool_failure}):
                    result=run_agent(question,context,client=model)
            else:
                result=run_agent(question,context,client=model)
            assert result['status']==['ok','ok','ok','refused','clarification','error','error'][i]
    assert len(events)==7
    summary=summarize(events)
    report={'scope':'seven local mock interactions; not Groq latency or production metrics',
            'sample_order':['faq','authorized_order','authorized_sales','access_refusal','clarification','provider_failure','tool_failure'],
            'formulas':{'error_rate':'count(status=error)/N', 'refusal_rate':'count(status=refused)/N',
                        'mean_latency_ms':'sum(duration_ms)/N', 'p95_latency_ms':'sorted(duration_ms)[ceil(0.95*N)-1]',
                        'mean_tools_per_request':'sum(tool_count)/N'},
            'metrics':summary}
    (ROOT/'anonymized_traces.jsonl').write_text(''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events))
    (ROOT/'monitoring_summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    table='# Monitoring local · échantillon mock\n\nAucune mesure distante Groq. N = 7 interactions.\n\n| Indicateur | Valeur |\n| --- | --- |\n'
    for key,value in summary.items():
        table+=f'| {key} | {value} |\n'
    (ROOT/'monitoring_summary.md').write_text(table)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
