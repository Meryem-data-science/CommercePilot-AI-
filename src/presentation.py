"""Adaptation UI locale : plans mock explicites, aucun modèle à l'import."""
import os
from .agent import completion_needs, run_agent
from .schemas import explicit_period
from .llm_client import MockClient, GroqClient
from .tools.common import read_table
import json


def groq_available():
    return all(bool(os.environ.get(n)) for n in ('GROQ_API_KEY', 'GROQ_MODEL'))


def customer_ids():
    from .tools.common import read_orders
    return sorted({r['customer_id'] for r in read_orders()})


def scripted_client(question):
    """Démo déterministe des formulations reconnues, pas un substitut de LLM."""
    needs = completion_needs(question, explicit_period(question))
    if not needs:
        return MockClient()
    faq = {r['source_id']:r['question'] for r in read_table(
        'faq.csv', ['source_id','category','question','answer','version'], 'source_id')}
    calls = []
    for i, (tool, value) in enumerate(needs):
        args = ({'query':faq[value]} if tool == 'search_faq' else
                {'order_id':value} if tool == 'get_order_status' else {'period':value})
        calls.append({'id':f'ui{i}', 'name':tool, 'arguments':json.dumps(args)})
    return MockClient([{'calls':calls}, {'calls':[]}])


def ask(question, context, mode, history):
    if mode == 'Groq' and not groq_available():
        raise ValueError('Configuration indisponible')
    client = GroqClient() if mode == 'Groq' else scripted_client(question)
    return run_agent(question, context, client=client, history=history)


REFERENCE_LABEL = '1er octobre 2026'
