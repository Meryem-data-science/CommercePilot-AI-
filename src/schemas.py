"""Schémas stricts ; JSON constitue le sous-ensemble YAML utilisé pour la config."""
import json
from pathlib import Path
import re
from .tools.common import iso

LIMITS = {'max_iterations':(1,10), 'max_tool_calls':(1,10), 'api_timeout_seconds':(1,60),
          'max_output_tokens':(64,2048), 'max_input_chars':(1,10000), 'max_history_messages':(0,10)}


def load_config(path=None):
    config = json.loads(Path(path or Path(__file__).resolve().parents[1]/'configs/agent.yaml').read_text())
    if not isinstance(config,dict) or set(config) != set(LIMITS):
        raise ValueError('configuration')
    for k,(low,high) in LIMITS.items():
        if type(config[k]) is not int or not low <= config[k] <= high:
            raise ValueError('configuration')
    return config


def valid_context(context):
    if not isinstance(context,dict) or set(context)-{'role','customer_id'}:
        return False
    role = context.get('role')
    if role not in ('client','analyste','administrateur'):
        return False
    cid = context.get('customer_id')
    return (isinstance(cid,str) and re.fullmatch(r'CLI-\d{3}',cid) is not None) if role=='client' else cid is None


def valid_arguments(name, args):
    if not isinstance(args,dict):
        return False
    if name == 'search_faq':
        return set(args)=={'query'} and isinstance(args['query'],str) and 1 <= len(args['query'].strip()) and len(args['query'])<=500
    if name == 'get_order_status':
        return set(args)=={'order_id'} and isinstance(args['order_id'],str) and re.fullmatch(r'CMD-DEMO-\d{3}',args['order_id']) is not None
    if name == 'sales_summary':
        if set(args)!={'period'} or not isinstance(args['period'],dict) or set(args['period'])!={'start_date','end_date'}:
            return False
        try:
            return iso(args['period']['start_date']) <= iso(args['period']['end_date'])
        except (ValueError,TypeError):
            return False
    return False


def function(name, description, properties, required):
    return {'type':'function','function':{'name':name,'description':description,
            'parameters':{'type':'object','properties':properties,'required':required,'additionalProperties':False}}}


TOOL_SCHEMAS = [
    function('search_faq', 'Consulter les politiques générales AtlasShop : délais, frais et zones de livraison, paiement, retours. Utiliser pour une question informative, sans identifiant de commande. Disponible pour tous les rôles.', {'query':{'type':'string','maxLength':500,'description':'Question générale en français, conservant les mots précis du besoin utilisateur.'}},['query']),
    function('get_order_status', 'Consulter le statut et les dates d’une commande précise. Nécessite un identifiant explicite dans la question. Client : ses commandes seulement ; administrateur : autorisé ; analyste : interdit. Ne jamais inventer un identifiant.', {'order_id':{'type':'string','pattern':'^CMD-DEMO-[0-9]{3}$','description':'Identifiant CMD-DEMO-NNN fourni explicitement par la question actuelle.'}},['order_id']),
    function('sales_summary', 'Calculer des agrégats de ventes sur une période explicite complète. Réservé aux analystes et administrateurs ; interdit aux clients. Ne pas inventer de dates ni utiliser de période relative.', {'period':{'description':'Bornes inclusives ISO, exactement égales à la période normalisée par l’application.','type':'object','properties':{'start_date':{'type':'string','format':'date'},'end_date':{'type':'string','format':'date'}},'required':['start_date','end_date'],'additionalProperties':False}},['period']),
]


def explicit_period(question):
    """Période explicite uniquement : deux dates ISO ou un seul mois français daté."""
    import calendar
    import unicodedata
    text = ''.join(c for c in unicodedata.normalize('NFKD',question.casefold()) if not unicodedata.combining(c))
    if re.search(r'\b(ce mois|ce trimestre|cette annee|mois (dernier|prochain|precedent|courant)|annee (derniere|prochaine)|aujourd.hui|hier|demain)\b',text):
        return None
    dates = re.findall(r'(?<![\d-])\d{4}-\d{2}-\d{2}(?![\d-])',text)
    months = ('janvier','fevrier','mars','avril','mai','juin','juillet','aout','septembre','octobre','novembre','decembre')
    matches = re.findall(r'\b('+'|'.join(months)+r')\s+(\d{4})\b',text)
    if not dates and (re.search(r'\b(depuis|avant|apres|jusqu|partir|quinzaine|trimestre|semestre|mi)\b',text)
                      or re.search(r'\b\d{1,2}(?:er)?\s+(?:'+'|'.join(months)+r')\b',text)):
        return None
    try:
        if len(dates)==2 and not matches:
            start, end = dates
        elif len(matches)==1 and not dates:
            month, year = matches[0]
            year, month = int(year), months.index(month)+1
            start = f'{year:04d}-{month:02d}-01'
            end = f'{year:04d}-{month:02d}-{calendar.monthrange(year,month)[1]:02d}'
        else:
            return None
        if iso(start) > iso(end):
            return None
        return {'start_date':start,'end_date':end}
    except ValueError:
        return None
