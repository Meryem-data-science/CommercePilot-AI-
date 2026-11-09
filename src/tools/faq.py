"""Recherche lexicale déterministe, sans exécution du contenu documentaire."""
import re
import unicodedata
from .common import DATA_ERRORS, read_table, result, invalid, unavailable

STOP = set('a au aux avec ce ces cette comment dans de des du elle en est et il je la le les leur ma me mes mon ne ou par pas pour quels quelles quel quelle que qui se ses son sur un une vos votre vous'.split())


def tokens(text):
    text = ''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))
    return set(re.findall(r'[a-z0-9]+',text)) - STOP


def search_faq(query):
    if not isinstance(query,str) or not query.strip() or len(query) > 500 or any(unicodedata.category(c)=='Cc' for c in query):
        return invalid()
    words = tokens(query)
    if not words:
        return invalid()
    try:
        rows = read_table('faq.csv',['source_id','category','question','answer','version'],'source_id')
        ranked = []
        for row in rows:
            if not re.fullmatch(r'FAQ-\d{3}',row['source_id']) or not re.fullmatch(r'\d+\.\d+',row['version']):
                raise ValueError('FAQ')
            overlap = len(words & tokens(row['question']))
            score = overlap / len(words)
            if overlap and score >= 0.5:
                ranked.append((score, overlap, row))
        if not ranked:
            return result('not_found','Aucune réponse suffisamment pertinente dans la FAQ.')
        ranked.sort(key=lambda x:(-x[0],-x[1],x[2]['source_id']))
        score, _, row = ranked[0]
        return result('ok','Réponse documentaire disponible.',
                      {'answer':row['answer'],'source_id':row['source_id'],'version':row['version'],'score':round(score,4)})
    except DATA_ERRORS:
        return unavailable()
