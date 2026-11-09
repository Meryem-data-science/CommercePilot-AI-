"""CommercePilot AI — interface de démonstration Streamlit."""
import streamlit as st
from src.presentation import ask, customer_ids, groq_available, REFERENCE_LABEL
from src.agent import french_date, french_mad

st.set_page_config(page_title='CommercePilot AI · Assistant commerce', page_icon='◈', layout='wide')
st.markdown('''<style>
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif}
.stApp {background:#f6f8fb;color:#18283c}
[data-testid="stSidebar"] {background:#112c35;color:#edf7f4}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] p,[data-testid="stSidebar"] h3 {color:#edf7f4}
[data-testid="stSidebar"] button p {color:#183d40}
[data-testid="stSidebarCollapseButton"] button {color:#e0f6ef}
[data-testid="stSidebar"] .stCaption p {color:#b7cdd0}
.block-container {max-width:1150px;padding-top:2.2rem;padding-bottom:3rem}
.hero {padding:32px 36px;background:linear-gradient(125deg,#11313b,#215750);border-radius:22px;color:#f7fffd;margin-bottom:24px;box-shadow:0 12px 32px #163e4314}
.hero h1 {color:#fff;font-size:2.6rem;letter-spacing:-1.5px;margin:8px 0}
.hero p {color:#d1e7df;max-width:680px;font-size:1.05rem}
.eyebrow {font-size:.72rem;letter-spacing:2px;font-weight:700;color:#88dfb9}
.pill {display:inline-block;border:1px solid #80b4a566;padding:5px 12px;border-radius:30px;margin:8px 8px 0 0;font-size:.78rem;color:#e0f6ef}
[data-testid="stChatMessage"] {background:white;border:1px solid #e4eaf0;border-radius:18px;padding:22px;margin-bottom:16px;box-shadow:0 4px 16px #19304505}
[data-testid="stMetric"] {background:white;border:1px solid #e2e9ef;border-radius:14px;padding:16px}
[data-testid="stMetricValue"] {font-size:1.35rem}
.stButton>button {border-radius:10px}
[data-testid="stBottomBlockContainer"] {background:#f6f8fb}
@media(max-width:700px){.hero{padding:22px}.hero h1{font-size:2rem}.block-container{padding-top:1rem}}
</style>''', unsafe_allow_html=True)


def reset():
    st.session_state.messages = []
    st.session_state.last_result = None
    st.session_state.pop('pending_question', None)


def queue(question):
    st.session_state.pending_question = question


def show_result(result):
    status = result['status']
    if status == 'refused':
        st.warning(result['answer'], icon='🔒')
    elif status == 'error':
        st.error(result['answer'])
    elif status == 'clarification':
        st.info(result['answer'])
    else:
        st.markdown(result['answer'])
    # Ne jamais rendre les résultats accumulés d'un refus ou d'une erreur.
    if status == 'ok':
        for tool, output in zip(result['tools_called'], result['results']):
            if output['status'] != 'ok':
                continue
            data = output['data']
            if tool == 'get_order_status':
                with st.container(border=True):
                    st.caption('SUIVI · ' + data['order_id'])
                    statuses = {'livree':'Livrée','en_preparation':'En préparation','expediee':'Expédiée','annulee':'Annulée','retournee':'Retournée'}
                    st.markdown('**'+statuses[data['order_status']]+'**')
                    cols = st.columns(2)
                    cols[0].metric('Livraison prévue', french_date(data['expected_delivery_date']))
                    cols[1].metric('Livraison effectuée', french_date(data['actual_delivery_date']) if data['actual_delivery_date'] else 'Non renseignée')
                    st.caption('Données de démonstration au ' + REFERENCE_LABEL)
            elif tool == 'sales_summary':
                cols = st.columns(3)
                for col, label, key in zip(cols, ['Commandé', 'Payé', 'Réalisé · livré et payé'],
                                          ['ordered_amount_mad', 'paid_amount_mad', 'realized_revenue_mad']):
                    col.metric(label, french_mad(data[key]))
    if result['sources']:
        st.caption('Références documentaires · ' + ' · '.join(result['sources']))
    if result['tools_called']:
        labels = {'search_faq':'FAQ consultée', 'get_order_status':'Suivi consulté', 'sales_summary':'Ventes analysées'}
        st.caption('Outils exécutés · ' + ' · '.join(labels.get(t,t) for t in result['tools_called']))


st.session_state.setdefault('messages', [])
st.session_state.setdefault('last_result', None)
with st.sidebar:
    st.markdown('### ◈ CommercePilot')
    st.caption('VOTRE ESPACE DE DÉMONSTRATION')
    role = st.selectbox('Profil de démonstration', ['client','analyste','administrateur'], key='role')
    try:
        ids = customer_ids()
    except (OSError, ValueError, KeyError):
        st.error('Les données de démonstration sont indisponibles.')
        st.stop()
    cid = st.selectbox('Client synthétique', ids, key='customer_id') if role == 'client' else None
    modes = ['Mock', 'Groq'] if groq_available() else ['Mock']
    if st.session_state.get('mode') not in modes:
        st.session_state.mode = 'Mock'
    mode = st.radio('Mode de conversation', modes, key='mode', horizontal=True)
    signature = (role, cid, mode)
    if st.session_state.get('signature') != signature:
        reset()
        st.session_state.signature = signature
    st.caption('Mock : plans locaux scriptés. Groq : requêtes réelles au fournisseur.' if groq_available()
               else 'Mock autonome. Groq sera disponible après configuration sécurisée du serveur.')
    st.button('Nouvelle conversation', on_click=reset, use_container_width=True)
    st.divider()
    st.markdown('**Essayez une question**')
    examples = ['Quels sont les délais de livraison ?', 'Quel est le délai de retour ?']
    examples += ['Où est ma commande CMD-DEMO-001 ?'] if role == 'client' else ['Résume les ventes de septembre 2026.']
    for i, question in enumerate(examples):
        st.button(question, key=f'example{i}', on_click=queue, args=(question,), use_container_width=True)
    st.divider()
    st.caption('Profils simulés : aucune authentification réelle. Données AtlasShop fictives et historiques au ' + REFERENCE_LABEL + '. Aucun achat, remboursement ou changement de commande.')
    st.caption('Le changement de profil, de client ou de mode efface la conversation pour protéger son contexte.')

st.markdown(f'''<div class="hero"><div class="eyebrow">L’INTELLIGENCE AU SERVICE DU COMMERCE</div>
<h1>CommercePilot AI</h1><p>Vos réponses e-commerce, au même endroit.<br>Consultez les politiques de la boutique, suivez vos commandes et explorez vos ventes.</p>
<span class="pill">Mode {mode}</span><span class="pill">Profil {role}</span><span class="pill">AtlasShop · données synthétiques</span></div>''', unsafe_allow_html=True)
if not st.session_state.messages:
    st.subheader('Comment puis-je vous aider ?')
    st.caption('Choisissez une suggestion ou posez votre question ci-dessous.')
    cols = st.columns(3)
    for col, title, text in zip(cols, ['Politiques de la boutique','Suivi de commande','Pilotage des ventes'],
                               ['Livraison, retours et réponses documentées.','Des dates et statuts issus de vos commandes.','Des agrégats clairs pour les profils autorisés.']):
        with col, st.container(border=True):
            st.markdown('**'+title+'**')
            st.caption(text)
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        if message['role'] == 'user':
            st.markdown(message['content'])
        else:
            show_result(message['result'])
question = st.chat_input('Posez votre question sur AtlasShop…', max_chars=1500)
question = question or st.session_state.pop('pending_question', None)
if question:
    context = {'role':role, **({'customer_id':cid} if role == 'client' else {})}
    history = [m['content'] for m in st.session_state.messages if m['role']=='user'][-4:]
    with st.chat_message('user'):
        st.markdown(question)
    with st.chat_message('assistant'):
        with st.spinner('Je consulte les informations disponibles…'):
            try:
                result = ask(question, context, mode, history)
            except Exception:
                # Aucun détail de transport, secret ou traceback dans l'interface.
                result = {'status':'error','answer':'Les informations sont momentanément indisponibles. Réessayez plus tard.',
                          'tools_called':[],'sources':[],'results':[],'error_type':'ui_error'}
        show_result(result)
    st.session_state.messages.extend([{'role':'user','content':question},{'role':'assistant','result':result}])
    st.session_state.last_result = result
