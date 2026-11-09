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

Les documents de cadrage (tâche 1), la structure du dépôt et l'environnement Python minimal (tâche 2) sont préparés. Aucun outil métier, orchestrateur, dataset, test applicatif, interface, pipeline CI/CD ou déploiement n'est réalisé. Groq, Streamlit et MLflow restent à intégrer ; GitHub Actions reste à configurer. Aucune commande de lancement d'application n'est disponible.

## Documentation

- [Cadrage métier, cas d'usage et permissions](docs/cadrage.md)
- [Architecture fonctionnelle prévisionnelle](docs/architecture.md)
- [Rapport progressif et introduction académique](docs/rapport_progressif.md)

## Architecture prévisionnelle

L'interface Streamlit transmettra une question et un contexte de rôle simulé à un orchestrateur Python. Celui-ci pourra solliciter un modèle via Groq et sélectionner un outil autorisé. Les validations et permissions précéderont l'accès aux sources synthétiques ; les outils sensibles réappliqueront les contrôles. La réponse devra rester fondée sur les résultats. MLflow est envisagé pour le suivi des expériences et évaluations futures. Le [diagramme détaillé](docs/architecture.md) décrit cette cible, sans composant applicatif implémenté.

## Structure du dépôt

```text
CommercePilot-AI-/
├── .github/workflows/  # Réservé à la CI/CD future ; aucun workflow actif
├── src/
│   └── tools/         # Outils futurs, non implémentés
├── tests/             # Tests futurs, aucun test applicatif
├── data/              # Données synthétiques futures
├── evaluation/        # Scénarios et évaluations futurs
├── docs/              # Cadrage, architecture, rapport progressif
├── .python-version    # Version cible exacte : 3.11.14
├── requirements.txt   # Aucune dépendance tierce à cette étape
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

Le raccourci global `python3.11` n'a pas pu être créé dans le répertoire personnel en lecture seule ; le chemin explicite permet de créer le virtualenv. `.python-version` documente la version cible mais ne remplace pas l'installation de l'interpréteur. Aucune dépendance tierce n'étant requise pour la tâche 2, le fichier de dépendances ne contient que des commentaires ; les versions seront fixées lors de leur ajout. Les commandes devront être relancées sur un nouveau poste : sa validation n'est pas revendiquée ici.

## Configuration et secrets

Pour préparer une configuration locale future, sans écraser un fichier existant :

```bash
# À exécuter seulement si .env n'existe pas encore.
cp -n .env.example .env
```

Cette copie est facultative à la tâche 2 : aucun composant ne lit encore ces variables. `GROQ_API_KEY`, `GROQ_MODEL` et `MLFLOW_TRACKING_URI` sont des emplacements futurs, laissés vides. Ne jamais placer une clé dans `.env.example`, le code, un rapport ou une capture. `.env` et ses variantes, les clés privées, les secrets Streamlit et les logs sont ignorés par Git ; `.env.example` reste versionnable. Utiliser ultérieurement les réglages sécurisés de l'environnement ou les secrets GitHub Actions pour l'injection des identifiants. Les règles d'exclusion ne remplacent pas une revue avant chaque commit.

La tâche 3 n'est pas engagée.
