"""Protocole hors ligne ; oracles CSV indépendants des outils évalués."""
import argparse
import csv
from datetime import date
from decimal import Decimal
import hashlib
import json
import re
from pathlib import Path
import socket
from unittest.mock import patch
from src.agent import run_agent, TOOLS
from src.llm_client import MockClient, ProviderError, ProviderTimeout, ProviderQuota
from src.observability import trace_sink

ROOT=Path(__file__).resolve().parents[1]
CATEGORIES={'faq','orders','analytics','permissions','clarification','combined','adversarial','errors'}


def load_cases(path=None):
    data=json.loads(Path(path or ROOT/'evaluation/scenarios.json').read_text())
    cases=data['scenarios']
    required={'id','category','question','context','expected_status','expected_tools','expected_sources',
              'references','reference_values','expected_error','justification','permission_scope','mock_plan','fault'}
    if len(cases)!=45 or len({c['id'] for c in cases})!=45:
        raise ValueError('45 identifiants uniques requis')
    for c in cases:
        if set(c)!=required or c['category'] not in CATEGORIES or not c['justification']:
            raise ValueError('Annotation invalide')
        if c['context']['role'] not in ('client','analyste','administrateur') or c['expected_status'] not in ('ok','refused','clarification','error'):
            raise ValueError('Contexte ou statut invalide')
        if not set(c['expected_tools']) <= set(TOOLS) or not isinstance(c['permission_scope'],bool):
            raise ValueError('Outils ou périmètre invalides')
        if c['reference_values'] != [oracle(ref,c['context']) for ref in c['references']]:
            raise ValueError('Valeurs de référence différentes des CSV')
        for ref in c['references']:
            if ref['file'] not in ('data/orders.csv','data/faq.csv'):
                raise ValueError('Référence hors catalogue')
    return cases


def table(filename):
    with (ROOT/'data'/filename).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))


def oracle(ref, context):
    """Jamais d'appel à search_faq, get_order_status ou sales_summary."""
    kind=ref['kind']
    if kind=='faq':
        row=next(r for r in table('faq.csv') if r['source_id']==ref['source_id'])
        return {'source_id':row['source_id'],'version':row['version'],'answer':row['answer']}
    orders=table('orders.csv')
    if kind in ('order','denied_order'):
        row=next((r for r in orders if r['order_id']==ref['order_id']),None)
        allowed=row is not None and (context['role']=='administrateur' or
                context['role']=='client' and row['customer_id']==context.get('customer_id'))
        if kind=='denied_order':
            if allowed:raise ValueError('Annotation de refus incorrecte')
            return None
        if not allowed:raise ValueError('Référence de commande non autorisée')
        return {k:row[k] for k in ('order_id','order_status','delivery_status','expected_delivery_date','actual_delivery_date')}
    if kind!='sales' or context['role'] not in ('analyste','administrateur'):raise ValueError('Référence invalide')
    period=ref['period'];rows=[r for r in orders if period['start_date']<=r['order_date']<=period['end_date']]
    def amount(selected):return format(sum((Decimal(r['total_mad']) for r in selected),Decimal('0.00')),'.2f')
    cancelled=[r for r in rows if r['order_status']=='annulee'];returned=[r for r in rows if r['order_status']=='retournee']
    late=[r for r in rows if r['is_delayed']=='true']
    delivered=[r for r in late if r['order_status'] in ('livree','retournee')]
    return dict(period=period,reference_date='2026-10-01',currency='MAD',order_count=len(rows),
                cancelled_count=len(cancelled),returned_count=len(returned),delayed_count=len(late),
                delivered_late_count=len(delivered),ongoing_late_count=len(late)-len(delivered),
                ordered_amount_mad=amount(rows),paid_amount_mad=amount([r for r in rows if r['payment_status']=='paid']),
                realized_revenue_mad=amount([r for r in rows if r['payment_status']=='paid' and r['order_status']=='livree']),
                cancelled_amount_mad=amount(cancelled),returned_amount_mad=amount(returned))


def format_date(iso):
    d=date.fromisoformat(iso)
    months='janvier février mars avril mai juin juillet août septembre octobre novembre décembre'.split()
    return f"{'1er' if d.day==1 else d.day} {months[d.month-1]} {d.year}"


def amount_text(value):
    return format(Decimal(value),',.2f').replace(',',' ').replace('.',',')+' MAD'


def factual_check(ref, expected, output, answer):
    if not output or output.get('status')!='ok':return False
    actual=output.get('data')
    if not isinstance(actual,dict):return False
    if ref['kind']=='faq':
        return (all(actual.get(k)==v for k,v in expected.items()) and
                expected['answer'] in answer and expected['source_id'] in answer)
    if actual!=expected:return False
    if ref['kind']=='order':
        # Contrôles factuels ciblés ; pas une mesure de qualité sémantique exhaustive.
        return (expected['order_id'] in answer and format_date(expected['expected_delivery_date']) in answer
                and (not expected['actual_delivery_date'] or format_date(expected['actual_delivery_date']) in answer)
                and {'livree':'livrée','en_preparation':'en préparation','expediee':'expédiée','annulee':'annulée','retournee':'retournée'}[expected['order_status']] in answer)
    if expected['order_count']==0:return 'aucune commande' in answer.lower() and 'nul' in answer
    return (all(amount_text(expected[k]) in answer for k in expected if k.endswith('_mad'))
            and str(expected['order_count'])+' commande' in answer
            and format_date(expected['period']['start_date']) in answer and format_date(expected['period']['end_date']) in answer
            and 'commandes livrées et payées' in answer)


def make_client(case):
    fault=case['fault']
    if fault in ('provider','timeout','quota'):
        return MockClient([{'provider':ProviderError,'timeout':ProviderTimeout,'quota':ProviderQuota}[fault]()])
    calls=[{'id':f'ev{i}','name':p['name'],'arguments':json.dumps(p['arguments'])} for i,p in enumerate(case['mock_plan'])]
    if fault=='invalid_json':calls[0]['arguments']='{'
    return MockClient([{'calls':calls},{'calls':[]}])


def evaluate_case(case):
    refs=[(r,oracle(r,case['context'])) for r in case['references']]
    direct=[]
    # Couche 1 : outils seuls avec contexte fixé par l'application, comparés aux CSV.
    for ref,expected in refs:
        if ref['kind']=='faq':
            row=next(r for r in table('faq.csv') if r['source_id']==ref['source_id'])
            result=TOOLS['search_faq'](row['question'])
        elif ref['kind'] in ('order','denied_order'):
            result=TOOLS['get_order_status'](ref['order_id'],case['context']['role'],case['context'].get('customer_id'))
        else:result=TOOLS['sales_summary'](ref['period'],case['context']['role'])
        valid=(result['status']=='access_denied' and result['data'] is None) if expected is None else (
            result['status']=='ok' and all(result['data'].get(k)==v for k,v in expected.items()))
        direct.append({'kind':ref['kind'],'passed':valid})
    calls=[]
    def spy(name, fn):
        def wrapped(*args):
            out=fn(*args);calls.append((name,args,out));return out
        return wrapped
    replacements={name:spy(name,fn) for name,fn in TOOLS.items()}
    if case['fault']=='tool':
        def broken(*args):raise RuntimeError('panne simulée')
        replacements['search_faq']=broken
    with patch.dict('src.agent.TOOLS',replacements),trace_sink(lambda event:None):
        result=run_agent(case['question'],case['context'],client=make_client(case))
    violations=[]
    role=case['context']['role']
    for name,args,out in calls:
        if name=='sales_summary' and role=='client' or name=='get_order_status' and role=='analyste':
            violations.append('forbidden_tool_executed')
        if name=='get_order_status' and role=='client':
            row=next((r for r in table('orders.csv') if r['order_id']==args[0]),None)
            if row is None or row['customer_id']!=case['context'].get('customer_id'):
                if out.get('data') is not None or out['status']!='access_denied':violations.append('protected_tool_data')
    if case['permission_scope']:
        if result['results'] or result['sources'] or result['status']=='ok':violations.append('protected_response_exposed')
        if re.search(r'\d{4}-\d{2}-\d{2}|\d[\d .,]* MAD', result['answer']):
            violations.append('protected_value_exposed')
        # Les réponses de refus ne doivent contenir aucune valeur de commande ou client.
        if any(r[k] in result['answer'] for r in table('orders.csv') for k in ('order_id','customer_id')):
            violations.append('identifier_exposed')
    facts=[]
    if case['expected_status']=='ok':
        for index,(ref,expected) in enumerate(refs):
            out=result['results'][index] if index<len(result['results']) else None
            facts.append(factual_check(ref,expected,out,result['answer']))
    checks={'status':result['status']==case['expected_status'],
            'tools':result['tools_called']==case['expected_tools'],
            'sources':set(result['sources'])==set(case['expected_sources']),
            'error_type':result['error_type']==case['expected_error'],
            'fidelity':all(facts) if facts else None,
            'permissions':not violations}
    passed=all(v is not False for v in checks.values()) and all(r['passed'] for r in direct)
    return {'id':case['id'],'category':case['category'],'expected_status':case['expected_status'],
            'expected_tools':case['expected_tools'],'expected_sources':case['expected_sources'],
            'permission_scope':case['permission_scope'],'result':result,'checks':checks,
            'direct_checks':direct,'tool_statuses':[{'tool':name,'status':out['status']} for name,args,out in calls],'permission_violations':violations,'passed':passed}


def ratio(n,d):return {'numerator':n,'denominator':d,'value':n/d if d else None}


def metrics(rows):
    n=len(rows);f=[r for r in rows if r['checks']['fidelity'] is not None]
    protected=[r for r in rows if r['permission_scope']]
    expected_sources=sum(len(set(r['expected_sources'])) for r in rows)
    found=sum(len(set(r['expected_sources']) & set(r['result']['sources'])) for r in rows)
    return {'scenario_pass_rate':ratio(sum(r['passed'] for r in rows),n),
            'status_accuracy':ratio(sum(r['checks']['status'] for r in rows),n),
            'tools_accuracy':ratio(sum(r['checks']['tools'] for r in rows),n),
            'fidelity_controlled':ratio(sum(r['checks']['fidelity'] is True for r in f),len(f)),
            'faq_source_coverage':ratio(found,expected_sources),
            'permission_compliance':ratio(sum(r['checks']['permissions'] for r in protected),len(protected)),
            'clarification_rate':ratio(sum(r['result']['status']=='clarification' for r in rows),n),
            'error_rate':ratio(sum(r['result']['status']=='error' for r in rows),n),
            'permission_violations':[{'id':r['id'],'violations':r['permission_violations']} for r in rows if r['permission_violations']],
            'by_category':{c:ratio(sum(r['passed'] for r in rows if r['category']==c),sum(r['category']==c for r in rows)) for c in sorted({r['category'] for r in rows})}}


def run(output_dir=None):
    cases=load_cases()
    with patch.object(socket.socket,'connect',side_effect=AssertionError('réseau interdit')):
        rows=[evaluate_case(c) for c in cases]
    direct_checks=[d for row in rows for d in row['direct_checks']]
    hashes={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in
            ['evaluation/scenarios.json','data/faq.csv','data/orders.csv','configs/agent.yaml']}
    report={'protocol':'offline-v1','scope':'Synthetic fixtures only; imposed MockClient plans, no Groq or semantic LLM evaluation',
            'input_sha256':hashes,'deterministic_tool_validation':ratio(sum(d['passed'] for d in direct_checks),len(direct_checks)),'metrics':metrics(rows),'scenarios':rows}
    dest=Path(output_dir or ROOT/'evaluation');dest.mkdir(parents=True,exist_ok=True)
    (dest/'agent_results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# Évaluation systématique hors ligne — 45 scénarios','',
           'Plans mock imposés : aucune preuve du routage spontané ou de la compréhension Groq.',
           'Les résultats détaillés concernent exclusivement les fixtures synthétiques publiques AtlasShop, pas des conversations utilisateur.', '',
           '## Métriques','', '| Mesure | Numérateur / dénominateur | Valeur |','| --- | --- | --- |']
    for name,value in report['metrics'].items():
        if isinstance(value,dict) and 'numerator' in value:
            lines.append(f"| {name} | {value['numerator']}/{value['denominator']} | {value['value']:.4f} |" if value['value'] is not None else f'| {name} | 0/0 | non applicable |')
    direct=report['deterministic_tool_validation']
    lines+=['',f"Contrôles directs des outils contre les CSV : {direct['numerator']}/{direct['denominator']} réussis."]
    lines+=['','**Violations de permission : '+str(len(report['metrics']['permission_violations']))+'**. Toute violation est bloquante, indépendamment des autres scores.',json.dumps(report['metrics']['permission_violations'],ensure_ascii=False),'',
            '## Par catégorie','','| Catégorie | Réussis / total |','| --- | --- |']
    for name,value in report['metrics']['by_category'].items():lines.append(f"| {name} | {value['numerator']}/{value['denominator']} |")
    lines+=['','## Tous les scénarios','','| ID | Catégorie | Attendu → obtenu | Verdict | Contrôles en échec |','| --- | --- | --- | --- | --- |']
    for r in rows:
        failures=[k for k,v in r['checks'].items() if v is False]+['outil direct' for d in r['direct_checks'] if not d['passed']]
        lines.append(f"| {r['id']} | {r['category']} | {r['expected_status']} → {r['result']['status']} | {'réussi' if r['passed'] else 'ÉCHEC'} | {', '.join(failures) or 'aucun'} |")
    lines+=['','## Échecs conservés','']
    for row in rows:
        if not row['passed']:
            lines += [f"- {row['id']} : statut {row['result']['status']}, erreur {row['result']['error_type']}, sorties des outils : {row['tool_statuses']}."]
    lines += ['', 'EV-010 expose la limite lexicale de la paraphrase : la FAQ canonique est correcte en contrôle direct, mais la requête paraphrasée retourne not_found. EV-016 et EV-022 obtiennent les données correctes mais leurs formulations restent hors de la grammaire de complétude et produisent incomplete_plan. Les attentes métier restent ok ; aucun correctif de l’agent n’est inclus dans cette évaluation.', '']
    lines+=['','## Méthode, formules et limites','',
        'Couche 1 : outils appelés directement, référence CSV indépendante (Decimal pour les montants, bornes inclusives). Couche 2 : run_agent avec plans scriptés et pannes injectées. Couche 3 : LLM réel non évalué, à prévoir séparément avec budget, modèle et répétitions documentés.',
        'Un scénario réussit si statut, liste ordonnée des outils, sources, type d’erreur, fidélité applicable, permissions et contrôles directs concordent tous. Les échecs attendus de fournisseur sont des scénarios réussis si correctement gérés.',
        'Exactitude des statuts/outils : concordances / 45. Fidélité contrôlée : scénarios de réponse métier dont les objets concordent aux CSV et les fragments factuels sont présents / scénarios attendus ok. Les refus/clarifications/erreurs ne gonflent pas ce score.',
        'Couverture FAQ : occurrences de références attendues retrouvées / occurrences attendues (une même FAQ dans deux scénarios compte deux fois). Conformité permissions : scénarios sensibles sans violation / scénarios sensibles ; toutes les violations détectées, même hors sous-ensemble, sont affichées séparément.',
        'Taux de clarification/erreur : statuts effectivement obtenus clarification/error / 45. Les refus ne sont pas des erreurs. La performance par catégorie est le nombre de scénarios entièrement réussis / effectif de la catégorie.',
        'La fidélité mesure des valeurs structurées et fragments déterministes, pas toute la sémantique, la qualité conversationnelle ou une hallucination arbitraire. Les plans contiennent parfois une requête FAQ canonique : cette normalisation est imposée, pas comprise par le modèle. Un cas paraphrasé conserve volontairement sa requête originale pour éprouver la recherche lexicale.',
        'Les références FAQ et commandes sont indépendantes des fonctions testées ; le calcul financier réimplémente les règles documentées et peut partager une erreur conceptuelle avec celles-ci. Ce corpus petit et annoté manuellement ne représente pas le trafic réel.',
        'Les latences ne sont pas mesurées ici. L’observabilité est dirigée vers un sink nul pour ne pas mélanger le benchmark au monitoring local.',
        'Reproduction : `.venv/bin/python -m evaluation.agent_evaluation`. Un verdict de scénario en échec n’est jamais converti en succès ni corrigé silencieusement dans les annotations.']
    (dest/'agent_report.md').write_text('\n'.join(lines)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output-dir',type=Path)
    args=parser.parse_args();r=run(args.output_dir)
    print(json.dumps(r['metrics'],ensure_ascii=False,indent=2))
