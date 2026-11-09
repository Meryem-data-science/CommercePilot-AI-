# CommercePilot AI

**Conception et industrialisation MLOps d'un agent intelligent multi-outils pour le e-commerce.**

Mini-projet académique — ENSA Fès, année universitaire 2026–2027.

## Objectif et périmètre prévus

CommercePilot AI vise une assistance e-commerce fondée sur trois outils de lecture :

- `search_faq(query)` : recherche dans la FAQ pour les trois rôles ;
- `get_order_status(order_id, role, customer_id)` : statut des propres commandes du client ou de toute commande synthétique pour l'administrateur ; accès refusé à l'analyste ;
- `sales_summary(period, role)` : ventes agrégées pour l'analyste et l'administrateur uniquement.

Aucun rôle ne pourra modifier les données, annuler une commande ou exécuter un remboursement. Les rôles de démonstration ne constituent pas une authentification réelle. Toutes les données futures seront fictives ; aucune donnée personnelle réelle n'est utilisée.

## État actuel

Les documents de cadrage (tâche 1), la structure du dépôt et l'environnement Python minimal (tâche 2) sont préparés. La tâche 3.A fournit maintenant les données synthétiques AtlasShop et leurs contrôles d'intégrité. Les trois outils métier indépendants du LLM sont implémentés à la tâche 3.B. La tâche 4 ajoute une orchestration bornée et un adaptateur Groq testé sur transport simulé. Les trois outils ont été validés avec Groq lors de la tâche 4. La tâche 5 ajoute une interface Streamlit locale, avec mode mock autonome et mode Groq configurable. Aucun pipeline CI/CD, MLflow ni déploiement public n'est réalisé.

## Documentation

- [Cadrage métier, cas d'usage et permissions](docs/cadrage.md)
- [Architecture fonctionnelle prévisionnelle](docs/architecture.md)
- [Rapport progressif et introduction académique](docs/rapport_progressif.md)

## Architecture prévisionnelle

L'interface Streamlit transmet une question et un contexte de rôle simulé à un orchestrateur Python. Celui-ci peut solliciter un modèle via Groq et sélectionner un outil autorisé. Les validations et permissions précèdent l'accès aux sources synthétiques ; les outils sensibles réappliquent les contrôles. La réponse reste fondée sur les résultats. MLflow est envisagé pour le suivi des expériences et évaluations futures. Le [diagramme détaillé](docs/architecture.md) décrit la cible initiale ; [l'orchestration actuelle](docs/agent.md) précise les composants de la tâche 4.

## Structure du dépôt

```text
CommercePilot-AI-/
├── .github/workflows/  # Réservé à la CI/CD future ; aucun workflow actif
├── src/
│   └── tools/         # Trois outils métier en lecture seule
├── tests/             # Tests de données, outils et agent mock
├── data/              # Données AtlasShop et scripts de validation
├── evaluation/        # Réservé aux évaluations futures
├── docs/              # Cadrage, architecture, rapport progressif
├── .python-version    # Version cible exacte : 3.11.14
├── requirements.txt   # SDK Groq et Streamlit
├── .env.example       # Noms de configuration, valeurs vides
├── .gitignore
└── README.md
```

Les dossiers vides contiennent un `.gitkeep`. L'environnement `.venv/` est local et ignoré.

## Prérequis et installation reproductible

Git et Python **3.11.14** avec `venv` et `pip` sont requis. Le dépôt distant sélectionné porte actuellement le nom `CommercePilot-AI-` (avec un tiret final).

```bash
git clone https://github.com/Meryem-data-science/CommercePilot-AI-.git
cd CommercePilot-AI-
python3.11 --version  # attendu : Python 3.11.14
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python --version
.venv/bin/python -m pip check
```

Le clonage ci-dessus est une instruction pour un nouveau poste ; il n'a pas été réexécuté dans le checkout cloud existant. Sous Windows, utiliser `.venv\Scripts\python.exe` à la place de `.venv/bin/python`.

Dans le cloud actuel, Python par défaut est 3.12.14. La préparation suivante a été exécutée avec `uv`, déjà disponible, en conservant la vérification TLS :

```bash
UV_PYTHON_INSTALL_DIR=/workspace/.commercepilot-python UV_CACHE_DIR=/tmp/commercepilot-uv-cache uv python install 3.11.14
cd /workspace/CommercePilot-AI-
export PIP_CACHE_DIR=/tmp/commercepilot-pip-cache
/workspace/.commercepilot-python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python --version
.venv/bin/python -m pip check
```

Le raccourci global `python3.11` n'a pas pu être créé dans le répertoire personnel en lecture seule ; le chemin explicite permet de créer le virtualenv. `.python-version` documente la version cible mais ne remplace pas l'installation de l'interpréteur. À la tâche 2, aucune dépendance tierce n'était requise ; le fichier actuel fixe les versions directes de Groq et Streamlit. Les commandes devront être relancées sur un nouveau poste : sa validation n'est pas revendiquée ici.

## Configuration et secrets

Pour préparer une configuration locale future, sans écraser un fichier existant :

```bash
# À exécuter seulement si .env n'existe pas encore.
cp -n .env.example .env
```

Cette copie reste facultative et ne configure pas automatiquement l'application : Groq lit `GROQ_API_KEY` et `GROQ_MODEL` dans l'environnement du serveur. `MLFLOW_TRACKING_URI` reste réservé à une étape future. Ne jamais placer une clé dans `.env.example`, le code, un rapport ou une capture. `.env` et ses variantes, les clés privées, les secrets Streamlit et les logs sont ignorés par Git ; `.env.example` reste versionnable. Utiliser ultérieurement les réglages sécurisés de l'environnement ou les secrets GitHub Actions pour l'injection des identifiants. Les règles d'exclusion ne remplacent pas une revue avant chaque commit.

## Données synthétiques — tâche 3.A

AtlasShop contient 50 produits, 30 clients fictifs, 300 commandes, 600 lignes et 35 FAQ. Aucune donnée personnelle réelle ni service externe n'est utilisé. Depuis la racine, avec Python 3.11.14 :

```bash
# Pour générer dans un dossier neuf, sans écraser la référence déjà fournie :
.venv/bin/python data/generate_data.py --output-dir /tmp/atlasshop-nouveau --seed 202627
.venv/bin/python data/validate_data.py --data-dir /tmp/atlasshop-nouveau
# Vérifier la référence et reproduire les contrôles effectivement exécutés :
.venv/bin/python data/validate_data.py
.venv/bin/python -m unittest discover -s tests -p test_data_validation.py -v
```

Le générateur refuse d'écraser les fichiers existants. La graine par défaut est `202627`, la période avril–septembre 2026 et la référence fixe le 1er octobre 2026. Voir le [dictionnaire et les KPI](docs/data_dictionary.md) et la [méthode et les validations](docs/data_generation.md). Ces contrôles portent sur les données, sans tester un agent. La tâche 3.B fournit les outils locaux ; l'orchestrateur est décrit ci-dessous (tâche 4).


## Outils métier — tâche 3.B

Les contrats, permissions, limites et exemples vérifiés sont décrits dans [docs/tools.md](docs/tools.md). Aucun LLM ni réseau n'est nécessaire. Depuis la racine :

```bash
.venv/bin/python -m unittest discover -s tests -p test_tools.py -v
.venv/bin/python -m unittest discover -s tests -v
```

Le contexte de rôle est simulé et ne constitue pas une authentification réelle.


## Orchestration — tâche 4

Le contexte utilisateur est fourni séparément à `run_agent` ; le modèle propose des appels sans rôle ni identité. Les permissions, arguments et limites sont contrôlés avant exécution. Le rendu final repose exclusivement sur les résultats locaux ; FAQ et données métier ne sont pas renvoyées au modèle. Les statuts d'erreur et refus restent déterministes. Voir [le contrat et la configuration](docs/agent.md).

```bash
PIP_CACHE_DIR=/tmp/commercepilot-pip-cache .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.agent --mode mock
.venv/bin/python -m unittest discover -s tests -v
```

Le mock est scripté et fonctionne sans clé ni réseau. Pour le mode réel, injecter `GROQ_API_KEY` de manière sécurisée et choisir un `GROQ_MODEL` compatible tool calling ; aucun modèle n'est codé en dur. Ne pas placer de secret dans les fichiers versionnés. La commande facultative `.venv/bin/python -m src.agent --mode groq --question 'Quels sont les délais de livraison ?'` n'a pas été exécutée avec l'API distante.

`configs/agent.yaml` utilise la syntaxe JSON, sous-ensemble YAML : 3 itérations, 3 appels d'outils, timeout API de 10 secondes, sortie de 512 tokens, entrée de 1500 caractères et 4 questions d'historique. L’identifiant et la période doivent être explicites : deux dates ISO ou un mois français avec son année (par exemple septembre 2026). Le contexte de rôle reste simulé et le filtre lexical d'injection reste limité. En cas de `provider`, vérifier variables et modèle sans afficher la clé ; `timeout` et `quota` n'entraînent aucune relance automatique. La tâche 5 n'est pas commencée.


## Interface Streamlit — tâche 5

L'interface réutilise l'orchestrateur sécurisé et ses réponses déterministes. Dans un environnement Python 3.11.14 préparé selon les instructions ci-dessus :

```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Ouvrir l'adresse locale affichée (port 8501 par défaut). Pour un environnement cloud, lancer si nécessaire avec `--server.address=0.0.0.0` et ouvrir ce port via le mécanisme de prévisualisation de la plateforme. Cela ne constitue pas un déploiement public.

Le mode **Mock**, sélectionné par défaut, ne nécessite aucun secret ni réseau : il crée des plans scriptés pour les formulations reconnues par l'orchestrateur, puis exécute les véritables outils locaux. Il ne prétend pas comprendre librement toutes les questions. Les boutons de suggestion fournissent des exemples compatibles. Le mode **Groq** n'est proposé que lorsque `GROQ_API_KEY` et `GROQ_MODEL` sont présentes dans l'environnement du serveur. Leurs valeurs ne sont pas affichées. La présence des variables ne garantit pas que l'API ou le modèle fonctionne. Les variables doivent être injectées par la configuration sécurisée ; l'application ne copie ni ne charge automatiquement de fichier `.env`. Aucun modèle n'est imposé.

Choisir le profil simulé et, pour un client, son identifiant synthétique. L'historique, les sélections et le dernier résultat vivent dans `st.session_state`. Tout changement de profil, de client ou de mode efface la conversation ; le bouton « Nouvelle conversation » fait de même. Les quatre dernières questions seulement sont transmises à l'orchestrateur. Chaque question en mode Groq peut appeler l'API et entraîner des coûts ; aucune relance automatique n'est ajoutée par l'interface.

La réponse, les références FAQ et les outils effectivement exécutés sont affichés. Les suivis réussis ont une carte de dates ; les analyses réussies présentent trois KPI distincts. Les refus et erreurs ne révèlent aucun résultat accumulé. Les demandes de précision et réponses partielles restent signalées. Les données sont fictives et historiques au 1er octobre 2026 ; les profils ne constituent pas une authentification. Cette interface ne doit pas être exposée comme un espace client de production. Aucune modification de commande ou remboursement n'est possible.

Vérifications :

```bash
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python data/validate_data.py
.venv/bin/python -m pip check
git diff --check
```

Captures utiles à conserver après exécution : accueil desktop, FAQ avec référence, suivi autorisé et ses dates, bilan analyste avec KPI, refus d'accès, clarification et vue mobile. Ne jamais inclure la configuration des secrets. Les captures doivent provenir de l'application réellement exécutée, jamais être fabriquées.


## Monitoring local — tâche 6

Chaque appel à `run_agent` produit une trace minimale dans `logs/agent_events.jsonl` (ignoré par Git). Aucun prompt, réponse brute, identifiant client/commande ou raisonnement privé n'est conservé. Une panne d'écriture ne bloque pas l'agent. Les journaux runtime restent privés et ne sont pas affichés dans Streamlit.

```bash
.venv/bin/python -m evaluation.run_monitoring
.venv/bin/python -m src.observability --path evaluation/anonymized_traces.jsonl
```

L'évaluation est exclusivement mock et génère sept traces anonymisées, `evaluation/monitoring_summary.json` et un tableau lisible dans `evaluation/monitoring_summary.md`. Elle inclut volontairement des refus et pannes ; ses taux ne représentent pas la fiabilité de Groq. Pour les traces runtime locales, utiliser `.venv/bin/python -m src.observability`. Les formules, mesures, limites de rétention et règles de confidentialité figurent dans la section de tâche 6 du rapport progressif.


## Qualité logicielle locale — tâche 8

```bash
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m quality.check
```

Cette commande exécute les tests sous garde réseau, mesure la couverture de `src/`, lance le validateur AtlasShop et Ruff, contrôle les seuils de la tâche 7, les métriques et la reproductibilité, recherche des secrets dans les fichiers versionnés/non ignorés et vérifie les diffs Git. Elle renvoie 0 si tous les gates passent, 1 sinon. Les résultats sont dans `evaluation/quality_results.json` et `evaluation/quality_report.md`, les preuves intermédiaires dans `work/quality/` (ignoré par Git).

Les seuils sont figés dans `quality/baseline.json` : 45 scénarios, au moins 42 réussis, aucun recul d'un scénario précédemment réussi, 28/28 contrôles directs et aucune violation de permission. Les échecs connus EV-010, EV-016 et EV-022 restent documentés ; les résultats de la tâche 7 ne sont jamais réécrits automatiquement. Le lint ciblé et la couverture ne remplacent pas un audit de sécurité. Aucun workflow GitHub Actions n'est créé.
