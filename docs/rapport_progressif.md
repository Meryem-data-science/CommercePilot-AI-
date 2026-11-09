# Rapport progressif — CommercePilot AI

**Titre :** CommercePilot AI — Conception et industrialisation MLOps d'un agent intelligent multi-outils pour le e-commerce.

**Cadre académique :** ENSA Fès, année universitaire 2026–2027.

## Introduction

Le développement des services de commerce électronique s'accompagne d'un besoin d'assistance capable de traiter des questions variées tout en préservant la confidentialité des informations. Les demandes relatives aux conditions de livraison, au suivi d'une commande et à l'analyse des ventes mobilisent des sources et des niveaux d'autorisation distincts. Dans ce contexte, une réponse conversationnelle pertinente doit être associée à un accès maîtrisé aux données et à une identification explicite des limites du service.

Le projet CommercePilot AI s'inscrit dans cette problématique. Il vise à concevoir un agent intelligent multi-outils de support e-commerce, puis à préparer son industrialisation selon une démarche MLOps. La question directrice est la suivante : comment articuler compréhension du langage naturel, consultation de sources structurées et contrôle d'accès afin de fournir des réponses vérifiables, sans permettre des opérations dépassant les droits de l'utilisateur ou le périmètre de l'agent ?

La solution envisagée repose sur trois fonctions complémentaires : `search_faq(query)` pour la recherche documentaire, `get_order_status(order_id, role, customer_id)` pour le suivi contrôlé d'une commande et `sales_summary(period, role)` pour les analyses commerciales agrégées. Python est prévu pour l'orchestration, Groq pour l'accès au modèle, Streamlit pour l'interface de démonstration et GitHub Actions pour une automatisation ultérieure. Ces choix constituent une orientation de conception et ne décrivent pas une intégration réalisée.

Trois acteurs fictifs structurent les besoins. Le client consulte la FAQ et ses propres commandes. L'analyste accède à la FAQ et aux synthèses commerciales, sans accès aux commandes individuelles. L'administrateur dispose d'un accès en lecture aux trois fonctions sur les données synthétiques. Ce dernier rôle ne confère aucun droit de mutation. Les rôles seront simulés pour la démonstration académique ; cette simulation ne constitue pas une authentification réelle et ne permet pas de revendiquer une protection adaptée à un service de production.

L'agent est limité à la fourniture d'informations. Il ne doit ni exécuter de remboursement, ni annuler une commande, ni modifier un stock, ni effectuer un paiement, ni exporter des clients ou contacter des tiers. Une demande portant sur la commande d'un autre client, une analyse commerciale sollicitée par un client ou une tentative de modification des permissions par injection doit conduire à un refus. L'explication documentaire d'une procédure de retour reste possible sans engager l'opération correspondante. Les données sources et les messages sont considérés comme non fiables du point de vue des instructions ; ils ne doivent pas modifier les règles d'autorisation.

Le recours exclusif à des données fictives, réalistes et reproductibles permettra ultérieurement de construire un cadre d'évaluation sans mobiliser de données personnelles réelles. Les volumes envisagés sont d'environ 50 produits, 30 clients, 300 commandes, 500 à 800 lignes de commande, 30 à 40 entrées de FAQ et 40 à 50 scénarios d'évaluation. Ces volumes sont prévisionnels : aucun jeu de données n'est produit dans la présente tâche.

La première étape se limite au cadrage métier et aux frontières fonctionnelles. Elle formalise douze cas d'usage, dont une demande combinant FAQ et statut de commande, une matrice de permissions fondée sur le moindre privilège et une architecture prévisionnelle. Des cas limites complémentaires décrivent les comportements attendus face à une panne technique à simuler, à des paramètres mal formés et à un échec partiel ; ils ne correspondent pas à des tests exécutés. La synthèse commerciale prévue portera notamment sur le nombre de commandes, le montant des ventes et les retards, avec des règles distinctes pour les annulations, paiements et retours ; les définitions exactes seront établies à la tâche 3. Les critères d'évaluation portent notamment sur les autorisations, l'exactitude des informations, l'ancrage documentaire et la reproductibilité. Les budgets de latence et de coût devront être justifiés par un protocole futur ; aucune mesure ni performance n'est annoncée dans ce rapport.

## État du travail à l'issue de la tâche 1

| Élément | État |
| --- | --- |
| Cadrage métier, acteurs, douze cas d'usage et permissions | Documentés dans `cadrage.md` |
| Architecture fonctionnelle et frontières de confiance | Décrites à titre prévisionnel dans `architecture.md` |
| Introduction du rapport | Rédigée dans le présent document |
| Outils Python et orchestrateur | Non implémentés |
| Intégration Groq et interface Streamlit | Non réalisées |
| Données synthétiques et scénarios d'évaluation | Non générés |
| Tests applicatifs, mesures, CI/CD et déploiement | Non réalisés |

Les contrôles documentaires portant sur l'existence des fichiers et leur cohérence ne constituent pas des tests applicatifs. Aucun résultat expérimental ou preuve de fonctionnement de l'agent n'est présenté.

## Documents de référence

- [Cadrage métier et permissions](cadrage.md)
- [Architecture prévisionnelle](architecture.md)

## Illustrations à préparer pour le rapport

Aucune capture d'interface applicative n'est disponible, puisque l'interface n'est pas implémentée. Les illustrations utiles à cette étape sont une capture du diagramme Mermaid rendu, de la matrice de permissions et du tableau des douze cas d'usage. Elles devront être légendées « conception prévisionnelle — tâche 1 » ; elles ne constituent pas des preuves d'exécution. Aucune capture d'écran n'est produite dans ce livrable.


## Environnement technique et organisation du projet

La tâche 2 établit le socle technique du projet, sans développer de fonctionnalité métier. Python constitue le langage retenu pour l'orchestration et les outils futurs. Groq est prévu pour l'accès au modèle de langage, Streamlit pour l'interface de démonstration, MLflow pour le suivi des expériences et GitHub Actions pour l'automatisation ultérieure. Ces composants ne sont ni installés comme dépendances du projet ni intégrés à cette étape. Git assure le suivi des fichiers ; leur publication sur GitHub reste distincte de leur création dans le checkout cloud.

L'organisation sépare le code futur (`src/` et `src/tools/`), les tests (`tests/`), les données synthétiques (`data/`), l'évaluation (`evaluation/`), la documentation (`docs/`) et les workflows futurs (`.github/workflows/`). Les dossiers vides sont conservés par des fichiers `.gitkeep`. Aucun workflow exécutable n'est créé. Le cadrage et l'architecture de la tâche 1 sont conservés sans modification, et l'introduction du présent rapport est préservée.

La version cible est Python 3.11, fixée précisément à 3.11.14 dans `.python-version`. L'interpréteur initial du cloud est Python 3.12.14 et la commande `python3.11` n'était pas disponible. Python 3.11.14 a donc été installé avec l'utilitaire `uv` déjà fourni, puis utilisé par son chemin explicite pour créer `.venv/`. Ce choix évite de dépendre de la version globale de la machine. Le fichier `.python-version` est une déclaration de version ; il ne constitue pas à lui seul un mécanisme d'installation.

À cette étape, aucune bibliothèque tierce n'est nécessaire. `requirements.txt` contient uniquement des commentaires explicitant ce choix. Streamlit, Groq et MLflow seront ajoutés avec des versions fixées lors des étapes concernées. La reproductibilité actuelle repose sur une version explicite de l'interpréteur, un environnement virtuel isolé et des commandes documentées. Aucune reproduction sur une seconde machine n'est revendiquée et aucune dépendance applicative future n'est validée.

Le fichier `.env.example` déclare `GROQ_API_KEY`, `GROQ_MODEL` et `MLFLOW_TRACKING_URI`, avec des valeurs vides. Il ne contient aucun identifiant secret. `.gitignore` exclut les environnements virtuels, caches, fichiers `.env` et variantes, clés privées, secrets Streamlit, logs et fichiers temporaires. Le modèle `.env.example` reste versionnable. Ces exclusions doivent être complétées par une revue avant chaque commit et, lors des intégrations futures, par une injection sécurisée des secrets. Aucun appel Groq n'a été effectué.

Les commandes suivantes ont été réellement exécutées dans l'environnement cloud :

```bash
UV_PYTHON_INSTALL_DIR=/workspace/.commercepilot-python UV_CACHE_DIR=/tmp/commercepilot-uv-cache uv python install 3.11.14
cd /workspace/CommercePilot-AI-
/workspace/.commercepilot-python/cpython-3.11.14-linux-x86_64-gnu/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python --version
.venv/bin/python -m pip check
# Nouvelle exécution avec un cache accessible :
PIP_CACHE_DIR=/tmp/commercepilot-pip-cache .venv/bin/python -m pip install -r requirements.txt
PIP_CACHE_DIR=/tmp/commercepilot-pip-cache .venv/bin/python -m pip check
```

L'installation de Python et la création du virtualenv ont abouti. La version effectivement observée dans le virtualenv est `Python 3.11.14`. L'installation depuis `requirements.txt` s'est terminée avec un code de sortie nul, sans paquet tiers à installer. La vérification a retourné `No broken requirements found.` ; ce résultat concerne uniquement l'environnement minimal, et non le fonctionnement de l'agent.

Deux limitations locales ont été diagnostiquées. La création du raccourci global de Python dans le répertoire personnel en lecture seule a échoué ; l'utilisation du chemin explicite de l'interpréteur a permis de poursuivre. Le cache pip du répertoire personnel n'était pas accessible ; la nouvelle exécution avec `PIP_CACHE_DIR=/tmp/commercepilot-pip-cache` s'est achevée sans cet avertissement. Aucun contournement de la vérification TLS n'a été utilisé.

Les contrôles documentaires et Git ont confirmé la présence des dossiers et fichiers essentiels, les valeurs vides du modèle de configuration, l'exclusion de douze chemins représentatifs de fichiers sensibles ou générés, et la possibilité de versionner les fichiers modèles et marqueurs. Les empreintes SHA-256 du cadrage et de l'architecture sont inchangées. Aucun test applicatif n'a été exécuté, car aucun test applicatif n'existe. La procédure de clonage figurant dans le README n'a pas été réexécutée dans le checkout existant. Aucun commit, push ou déploiement n'est réalisé dans cette tâche.

L'environnement courant est préparé, mais la persistance du script d'installation et des instructions de reprise dans les réglages cloud n'a pas pu être confirmée par l'outil de configuration. Les commandes vérifiées sont conservées dans le README et dans cette section ; la restauration automatique dans une nouvelle tâche cloud reste non vérifiée. Les preuves techniques pertinentes sont les sorties du terminal relatives à la version Python, à l'installation, à `pip check` et aux contrôles Git. Aucune capture de conversation ou de configuration cloud n'est nécessaire au rapport.
