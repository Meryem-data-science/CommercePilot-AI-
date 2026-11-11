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


### Constitution et validation des données synthétiques

La tâche 3.A constitue une base entièrement fictive pour AtlasShop, boutique marocaine de démonstration utilisant le dirham marocain. Elle prépare la recherche FAQ, le suivi contrôlé de commandes et les analyses futures, sans implémenter ces outils. Aucun nom de personne, numéro, contact ou adresse personnelle n'est généré.

| Ensemble | Volume réellement généré |
| --- | --- |
| Produits | 50 |
| Clients fictifs | 30 |
| Commandes | 300 |
| Lignes de commande | 600 |
| FAQ | 35 entrées, exportées en CSV et Markdown |

La génération utilise Python 3.11.14 et sa bibliothèque standard, avec la graine fixe 202627. Les transactions couvrent avril à septembre 2026 ; les états et retards sont observés au 1er octobre 2026. Les clients et produits sont reliés aux commandes par des clés étrangères. Les identifiants sont stables, notamment pour les futurs scénarios d'autorisation. Les montants sont calculés en centimes entiers puis validés avec des décimaux exacts. Après vérification ciblée du réalisme, les états comprennent 210 commandes livrées (70 %), 24 en préparation (8 %), 36 expédiées (12 %), 18 annulées (6 %) et 12 retournées (4 %), selon des combinaisons de paiement et livraison compatibles. Ces quotas pédagogiques ne sont pas calibrés sur des observations commerciales.

Le montant total commandé inclut les commandes annulées et retournées ; il représente un volume brut. Le montant actuellement payé exclut les remboursements et inclut les avances des commandes en cours. Le chiffre d'affaires réalisé est limité aux commandes livrées et payées. Les annulations interviennent avant encaissement et les retours sont intégralement remboursés. Le retard compare la livraison initiale à l'échéance, ou la référence à l'échéance pour les commandes en cours ; les annulations sont exclues. Les périodes commerciales futures seront filtrées selon la date de commande. Ces conventions pédagogiques ne constituent pas un référentiel comptable.

La génération et le validateur séparé ont été exécutés avec succès. Les vérifications portent sur les volumes, clés, quantités, prix, totaux, dates, statuts, retards, disponibilité et cohérence des deux représentations de la FAQ. La commande `python -m unittest discover -s tests -p test_data_validation.py -v`, exécutée avec l'interpréteur du virtualenv, a terminé trois méthodes de tests sans échec, y compris le contrôle de diversité des statuts par client et de l’âge des commandes en cours. Deux sorties indépendantes générées avec la même graine présentent les mêmes empreintes SHA-256 pour les six fichiers de données ; ces empreintes correspondent aussi à celles de la référence. Huit copies temporaires volontairement altérées ont été rejetées, notamment pour des clés étrangères invalides. La référence conservée n'a pas été modifiée par ces contrôles négatifs. Aucun test d'agent ou de contrôle d'accès applicatif n'est revendiqué.

Le diagnostic initial a identifié un statut unique pour chacun des 30 clients et 100 commandes en cours âgées de plus de 30 jours. Le mélange des statuts, distinct de l'attribution des clients, corrige cette dépendance : les 30 clients possèdent désormais deux à quatre statuts. Les commandes en cours ont de 1 à 11 jours observés, dont 8 en retard. Les propriétaires et états des trois commandes de référence sont préservés. La nouvelle génération a été validée en sortie temporaire avant remplacement contrôlé de la référence, puis les contrôles ont été relancés. Les données présentent néanmoins des limites : quotas de statuts artificiels, dix commandes par client, catalogue figé, stock sans historique et absence d'événements datés de paiement ou de retour. Elles ne permettent ni estimation commerciale réelle ni reconstitution des états passés. Les règles, colonnes et empreintes sont détaillées dans `data_dictionary.md` et `data_generation.md`. Les preuves utiles au rapport sont un résumé terminal de validation et un extrait des relations entre tables ; aucune capture de conversation n'est nécessaire. Aucun outil de la tâche 3.B, appel Groq, interface ou pipeline n'est développé.


## Architecture et implémentation des outils métier

La tâche 3.B implémente trois fonctions autonomes en Python 3.11.14, sans dépendance tierce ni modèle externe. La recherche FAQ applique une normalisation lexicale et restitue une réponse sourcée avec un score de couverture. La consultation de commande vérifie le contexte simulé et limite la restitution au suivi nécessaire. La synthèse commerciale agrège les commandes selon une période ISO inclusive et les règles métier établies ; les montants sont calculés avec des décimaux exacts et sérialisés avec deux décimales. Les sources synthétiques sont conservées sans modification.

| Opération | Client | Analyste | Administrateur |
| --- | --- | --- | --- |
| FAQ | Autorisée | Autorisée | Autorisée |
| Suivi individuel | Ses commandes | Refusé | Autorisé |
| Agrégats commerciaux | Refusé | Autorisés | Autorisés |

Les outils valident les paramètres avant lecture et utilisent des chemins locaux fixes. Les formats CSV, montants, états et dates sont contrôlés ; les erreurs de lecture ou données invalides produisent un résultat générique sans détails internes. Les commandes inconnues et celles d'un autre client reçoivent le même refus externe. Aucune opération de mutation n'est disponible. La structure commune de retour distingue succès, entrée invalide, refus, absence de réponse FAQ et erreur de données.

| Vérifications exécutées | Résultat |
| --- | --- |
| Quinze tests des outils : FAQ, permissions, erreurs, périodes, calculs | Réussis |
| Trois tests existants des données : intégrité négative, reproductibilité et réalisme | Réussis |
| Suite complète | 18 tests réussis, aucun échec |

L'oracle monétaire repose sur six commandes contrôlées dont les attentes sont calculées indépendamment de l'outil : 242.61 MAD commandés, 121.41 MAD payés et 101.21 MAD réalisés. Sur les données de référence, l'exemple avril–septembre 2026 retourne 300 commandes et 46 retards ; la FAQ identifie FAQ-002 pour les délais de livraison et le suivi autorisé restitue la commande CMD-DEMO-001. La validation des données et les tests ont été réellement exécutés. Ces observations ne constituent pas une évaluation de l'agent complet.

La recherche lexicale ne garantit pas la compréhension des paraphrases ou des négations ; son seuil heuristique n'est pas une probabilité de pertinence. Un texte malveillant reste une donnée, mais son filtrage sémantique n'est pas implémenté. Les paramètres de rôle et d'identité ne constituent pas une authentification : leur provenance fiable devra être garantie par l'application et l'orchestrateur futurs. Les contrats détaillés figurent dans `tools.md`. Les captures utiles sont la sortie synthétique des tests et les exemples structurés autorisés et refusés ; aucune image n'est fabriquée. L'orchestration, Groq, Streamlit et la CI/CD restent hors de cette tâche.


## Orchestration de l'agent et intégration du modèle de langage

La tâche 4 introduit un orchestrateur borné, une validation de schémas et un adaptateur au SDK officiel Groq, fixé à la version 1.7.0. Le modèle propose des appels selon le mécanisme officiel de tool calling ; il ne choisit ni rôle ni identité. Le contexte de démonstration est fourni par l'application appelante, distinctement du texte utilisateur. La liste blanche contient exclusivement les trois outils métier existants, conservés sans modification.

Les arguments et permissions sont vérifiés de manière déterministe avant exécution. Les lots multi-outils sont validés entièrement avant leur premier appel. L'identifiant doit apparaître dans la question. La période est établie localement à partir de deux dates ISO ou d'un mois français explicitement daté, tel que « septembre 2026 », converti en premier et dernier jours du mois. Le calcul tient compte des années bissextiles et ne dépend pas de l'horloge système. Toute période proposée par le modèle doit correspondre à ces bornes ; les expressions relatives ou ambiguës provoquent une clarification. Le contrôle lexical préalable refuse plusieurs formes de mutation, exportation et changement de rôle, sans prétendre détecter toutes les injections. Les paramètres simulés ne remplacent pas une authentification réelle.

Les résultats sont traités comme des données non fiables du point de vue des instructions. Aucun contenu FAQ ou résultat métier n'est retransmis au modèle : seuls des accusés de traitement sont fournis. La réponse finale utilise des gabarits français déterministes pour la FAQ sourcée, le suivi et la synthèse commerciale, sans reformulation libre susceptible d'introduire un statut ou montant absent des sources. Les résultats JSON sont conservés pour l'interface future. Les montants sont affichés à partir de leurs chaînes décimales exactes et les dates absentes ne sont pas complétées. En cas d'erreur ou de refus, les résultats accumulés sont masqués. Les refus de sécurité restent déterministes et ne sont pas délégués au modèle.

La configuration prévoit trois itérations, trois appels d'outils, dix secondes de timeout SDK par requête, 512 tokens de sortie et 1500 caractères par entrée, avec quatre questions d'historique. Le timeout réseau n'est pas une garantie de durée totale de l'interaction. Les appels SDK ne sont pas relancés automatiquement. Les erreurs de JSON, schéma, outil inconnu, permission, timeout, quota et fournisseur sont distinguées sans exposer de détails internes. Une limite atteinte arrête la boucle.

| Vérifications effectivement exécutées | Résultat |
| --- | --- |
| Agent et adaptateur, mocks et transport HTTP simulé | 30 tests réussis |
| Outils métier existants | 15 tests réussis |
| Données, reproductibilité et contrôles négatifs | 3 tests réussis |
| Suite complète | 48 réussis, aucun échec |

Le mode mock utilise des plans déterministes et ne requiert aucune clé ni facturation. Les scénarios couvrent FAQ, propriété des commandes, analytics, multi-outils, ambiguïtés, injections et pannes simulées. Le SDK officiel est également exercé avec un transport HTTP simulé, notamment pour les erreurs 429 et 500. La commande de démonstration mock a retourné une réponse française sourcée FAQ-002. Cinq tests ciblés supplémentaires vérifient le rendu sans altération des résultats, les valeurs absentes, les mois explicites, les années bissextiles et la clarification des périodes ambiguës ou contradictoires. L'installation des dépendances, le validateur et `pip check` ont réussi.

Le modèle distant reste configurable par `GROQ_MODEL` ; aucun identifiant de modèle n'est imposé. Lors de cette validation initiale, la clé et le modèle n'étaient pas disponibles et aucun appel Groq réel n'avait été lancé. Les vérifications distantes ultérieures sont distinguées ci-dessous. L'accès à la page web de documentation a renvoyé HTTP 403 ; les contrats ont été consultés dans les sources officielles du SDK. Ces résultats valident le fonctionnement local simulé, sans établir la qualité du routage réel ni une sécurité de production. Le filtre lexical peut produire des faux positifs et manquer des formulations inédites.

Le diagramme de séquence et les contrats détaillés figurent dans `agent.md`. Les figures utiles sont ce diagramme, la sortie synthétique des 48 tests et l'exemple CLI mock, sans clé ni capture de conversation. Aucune image n'est fabriquée. L'interface, l'observabilité complète, la CI/CD et le déploiement restent hors périmètre.


### Correction de la sélection d'outils et essais Groq réels — 9 novembre 2026

Le premier essai réel sur `main` (`e6f473ede97d4dbf6f1a2e596f70dd51925c92cb`) a techniquement abouti mais retourné `clarification` sans outil pour la question « Quels sont les délais de livraison ? ». Le code utilisait toujours `tool_choice=auto`, des descriptions limitées aux noms des outils et une conversion systématique de l'absence d'appel en clarification. La fin de génération de ce premier essai n'est pas connue ; ces facteurs constituent un diagnostic de conception, sans preuve d'une cause unique côté modèle.

Sur la branche locale `fix/groq-tool-selection`, les descriptions et le prompt sont précisés. Une reconnaissance déterministe conservatrice établit si une demande est complète et autorisée avant d'utiliser `required` au premier tour. Elle ne choisit ni la fonction ni les arguments à la place du modèle. Les autres demandes et la clôture restent en `auto`. Les schémas proposés sont filtrés par rôle ; les permissions, la propriété, les arguments stricts, les limites et les interdictions restent vérifiés. Les appels parallèles sont désactivés pour permettre la planification séquentielle. Une absence d'appel malgré une demande complète est distinguée d'une ambiguïté, et les sorties tronquées sont rejetées. Seules des métadonnées de fin sur liste blanche sont conservées, sans contenu privé de raisonnement.

Les **59 tests hors ligne réussissent** : 48 tests existants et 11 nouveaux tests ciblés, dont des échanges du SDK sur transport HTTP simulé. Le validateur des données et `git diff --check` réussissent. Python 3.11.14 et Groq SDK 1.7.0 ont été utilisés. Les données restent inchangées.

Le nouvel essai réel a été exécuté une seule fois après ces contrôles, avec les variables Groq présentes sans exposition de leurs valeurs. Deux réponses API ont été observées : sélection en `required`, fin `tool_calls`, puis clôture en `auto`, fin `length`. `search_faq` a réellement été exécuté, mais la limite de sortie au second tour conduit au statut final `error`, de type `provider`, avec « Le fournisseur est indisponible ou non configuré. ». Selon la politique existante, sources et résultats sont masqués en erreur. Ce message générique n'indique pas ici une absence de configuration : la métadonnée observée est une limite de génération.

La réponse attendue hors ligne pour AtlasShop est « La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie. », référence `FAQ-002`. Elle n'a pas été restituée dans ce nouvel essai réel. La sélection d'outil est corrigée pour cet essai, mais le succès de bout en bout reste non établi en raison de la clôture tronquée. Aucun nouvel appel, aucune métrique de qualité ni analyse du raisonnement privé ne sont revendiqués. Les détails et limites du reconnaisseur lexical figurent dans `agent.md`. Aucun commit ni push ; la tâche 5 n'est pas commencée.


### Clôture déterministe et troisième essai réel — 9 novembre 2026

Le défaut de clôture du deuxième essai était lié à un appel Groq supplémentaire obligatoire dans l'ancienne boucle, même après succès de la FAQ. Le rendu métier était déjà disponible, mais n'était déclenché qu'après réception d'un tour sans outil. Le second appel atteignait la limite de génération (`length`) et son rejet produisait une erreur masquant les résultats. La part du raisonnement interne dans cet épuisement n'a pas été mesurée ; aucun raisonnement privé n'a été enregistré ou analysé.

La correction ajoute une preuve de couverture conservatrice pour les formulations simples entièrement reconnues. Après succès d'un lot complet satisfaisant un seul besoin, l'agent appelle directement `render_results`, sans demander au modèle de terminer. Les données métier sont l'unique source de la réponse. Les demandes multi-outils gardent une planification séquentielle ; un besoin restant ne peut être présenté comme satisfait. Les demandes non entièrement reconnues sont signalées comme partielles si des résultats sont disponibles. Refus, erreurs et sorties tronquées ne sont jamais convertis en succès. Les permissions et outils métier restent inchangés.

Le budget reste fixé à 512 tokens de génération, sans hausse. `reasoning_effort=low` est transmis seulement aux modèles GPT-OSS explicitement reconnus par l'adaptateur ; les autres modèles ne reçoivent pas cette option. Les plafonds d'itérations et d'appels, le timeout et l'absence de relance SDK sont conservés. Le réglage vise une réduction du raisonnement généré sans économie de tokens revendiquée.

La suite complète comporte **70 tests réussis** : les 59 tests précédents adaptés aux nouvelles conditions de terminaison et 11 tests complémentaires. Ils couvrent les trois besoins simples, les demandes combinées, les besoins manquants ou ambigus, refus et pannes, couverture du thème FAQ, budget et réponses API tronquées sur transport simulé. Le validateur des données et `git diff --check` réussissent. Les données AtlasShop et les trois outils métier sont inchangés.

Une seule nouvelle interaction réelle a ensuite été exécutée sur la branche locale `fix/groq-tool-selection`, avec Python 3.11.14 et la CLI Groq. Résultat : **`status=ok`**, `tools_called=['search_faq']`, `sources=['FAQ-002']`, `error_type=null`. Une seule réponse API a été observée, avec `tool_choice=required` et `finish_reason=tool_calls`. La clôture a été réalisée localement sans deuxième requête.

Réponse réellement restituée : « La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie. (Source : FAQ-002.) » La référence est la FAQ AtlasShop version 1.0. Pour cette question, le nombre de réponses API observées est passé de deux à une entre les deux essais distincts ; aucun coût, temps ou volume de tokens n'est inventé. La généralisation à d'autres formulations et modèles reste à évaluer. Aucun nouvel essai automatique, commit ou push ; la tâche 5 n'est pas commencée. Les détails de la grammaire et des limites sont documentés dans `agent.md`.


### Vérification réelle complémentaire du suivi — 9 novembre 2026

Sur la branche locale `fix/groq-tool-selection`, les changements existants ont été préservés. Une seule interaction a été exécutée avec le véritable `GroqClient` via `run_agent`, pour « Où est ma commande CMD-DEMO-001 ? », contexte de démonstration `role=client`, `customer_id=CLI-001`. La configuration sécurisée existante a été utilisée sans affichage ni stockage de ses valeurs.

| Observation | Résultat réel |
| --- | --- |
| Statut final | `clarification` |
| Outil exécuté | `get_order_status` |
| Résultat de l'outil | `ok` |
| Appartenance | Commande appartenant à `CLI-001`, vérifiée dans les données locales |
| Statut et dates | Livrée ; date prévue et date effective : 2026-07-22 |
| Comparaison déterministe | Résultat de l'agent exactement égal à celui de `get_order_status` pour ce contexte |
| Réponses API observées | 2 : `auto/tool_calls`, puis `auto/stop` |
| Erreur de l'agent | `incomplete_plan` ; aucune erreur fournisseur signalée |

Réponse réellement produite :

> Résultats partiels ; la couverture complète de la demande reste à confirmer.
> Commande CMD-DEMO-001 : livrée. Date de livraison prévue : 2026-07-22. Livraison effectuée le 2026-07-22.

Le contenu métier du suivi est exact et compréhensible en français, mais le scénario n'est pas validé de bout en bout : le statut final reste une clarification injustifiée. Le contrôle `completion_needs` reconnaît notamment « Suivi CMD-DEMO-001 » et « Statut CMD-DEMO-001 », mais pas la formulation complète « Où est ma commande CMD-DEMO-001 ? ». La demande n'est donc pas reconnue comme entièrement couverte ; après l'appel de fin, le mécanisme conservateur présente les résultats comme partiels. Cette limite de reconnaissance explique le résultat observé sans défaut de permission ni de données. Aucune correction n'a été apportée dans cette vérification.

Conformément à l'arrêt demandé dès détection d'un défaut, le test « Résume les ventes de septembre 2026. », prévu avec `role=analyste` sans identité client, **n'a pas été exécuté**. Il n'existe donc pour cet essai ni statut, ni outil exécuté, ni réponse, ni erreur API observée ; zéro requête a été lancée pour les ventes. La période, les agrégats et l'absence de transmission de détails individuels ne sont pas revendiqués comme vérifiés par un nouvel essai réel.

Rappel historique sans nouvel appel : le dernier test FAQ validé avait retourné `ok`, exécuté `search_faq`, cité `FAQ-002` et utilisé une seule requête API. Sa réponse était « La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie. (Source : FAQ-002.) ».

Seule cette section de tâche 4 du rapport a été actualisée lors de la présente vérification. Les 70 tests automatiques étaient réussis lors de la validation précédente ; ils n'ont pas été relancés pour cette modification documentaire. Aucune donnée ni règle de sécurité modifiée, aucune répétition de l'interaction, aucun commit ni push. La tâche 5 n'est pas commencée.


### Reconnaissance des formulations de suivi et validation réelle finale — 9 novembre 2026

Le contrôle de complétude ne reconnaissait auparavant que des formulations étroites telles que « Suivi CMD-DEMO-001 ». La formulation « Où est ma commande CMD-DEMO-001 ? » donnait donc `completion_needs=None` malgré un résultat métier exact, et le tour de fin la présentait comme partielle (`clarification/incomplete_plan`). Le filtre préalable de sélection normalisait aussi « où » en « ou », puis pouvait le confondre avec une alternative. Ce défaut concernait la reconnaissance, pas les permissions ni les données.

La correction reste dans les fonctions de reconnaissance de `src/agent.py` : normalisation commune des accents, casse, espaces et ponctuation, avec conservation des identifiants et des séparateurs de clauses ; reconnaissance ancrée de chaque clause de consultation par `order_intent`. Les formulations suivantes sont reconnues : « Où est ma commande CMD-DEMO-001 ? », « Quel est le statut de CMD-DEMO-001 ? », « Suivi CMD-DEMO-001 », « Où en est ma commande CMD-DEMO-001 ? » et « Ma commande CMD-DEMO-001 a-t-elle été livrée ? ». Une simple mention d'identifiant ne suffit pas. Les besoins reconnus et leurs permissions sont consultés avant le filtre conservateur d'incertitude, ce qui distingue l'interrogatif « où » d'une alternative.

La séparation des clauses accepte aussi « ? Et … » sans perdre le second besoin. Une demande suivi + FAQ doit toujours satisfaire les deux besoins ; un besoin manquant conserve une clarification. Pour préparer la question exacte de validation commerciale sans reproduire le défaut de grammaire, le préfixe « Résume les ventes de … » est également reconnu lorsque la période est complète. Le moteur de rendu, les conditions de clôture, le client Groq, les limites et les outils métier n'ont pas été modifiés dans cette correction. Les mutations restent refusées avant tout appel ; la propriété, les permissions et l'interdiction des arguments de rôle ou d'identité restent contrôlées.

**Validation hors ligne : 77 tests réussis**, incluant les 70 précédents et 7 nouveaux tests paramétrés. Ils vérifient les variantes de formulation et de normalisation, les commandes autorisées et interdites, l'identifiant absent, les mentions ambiguës, le suivi combiné à la FAQ, les besoins insatisfaits, les mutations/remboursements, les arguments de contexte injectés, les permissions d'analyste et la formulation exacte des ventes. Le validateur des données et `git diff --check` réussissent. Aucune donnée AtlasShop ni aucun des trois outils métier n'a été modifié.

#### Essai réel de suivi

Une seule interaction `run_agent` avec le véritable `GroqClient` a été exécutée pour « Où est ma commande CMD-DEMO-001 ? », contexte `role=client`, `customer_id=CLI-001`.

- Statut final : **`ok`** ; outil exécuté : **`get_order_status`** ; erreur : **`null`**.
- Résultat exactement égal à celui de l'outil déterministe sous ce contexte, qui valide la propriété de la commande.
- Une seule réponse API observée : `required/tool_calls`. Aucun appel de clôture.
- Réponse réelle : « Commande CMD-DEMO-001 : livrée. Date de livraison prévue : 2026-07-22. Livraison effectuée le 2026-07-22. »

Le nombre de réponses API pour cette même formulation est passé de deux dans l'essai précédent à une dans ce nouvel essai, et le statut est passé de clarification à succès. Aucune mesure de coût, latence ou consommation de tokens n'est revendiquée.

#### Essai réel d'analyse des ventes

Après succès du suivi uniquement, une seule interaction a été exécutée pour « Résume les ventes de septembre 2026. », contexte `role=analyste`, sans `customer_id`.

- Statut final : **`ok`** ; outil exécuté : **`sales_summary`** ; erreur : **`null`**.
- Période normalisée : **2026-09-01 au 2026-09-30 inclus**.
- Tous les résultats sont exactement égaux à `sales_summary` exécuté localement pour cette période et ce rôle ; le rendu correspond exactement à `render_results`.
- Une seule réponse API observée : `required/tool_calls`. Aucun appel de clôture.
- Les schémas proposés excluent le suivi individuel pour ce rôle. Le contrôle des messages sortants n'a détecté aucun identifiant de client ou de commande ni champ `customer_id`/`order_id` ; aucun résultat métier individuel n'a été envoyé. Seuls des booléens de vérification ont été imprimés, sans contenu de raisonnement privé.

Réponse réelle : « Synthèse du 2026-09-01 au 2026-09-30 inclus (états au 2026-10-01) : 87 commande(s). Montant total commandé : 109544,30 MAD. Montant des commandes payées : 66261,30 MAD. Chiffre d’affaires réalisé : 29157,20 MAD. Annulations : 2 (2082,30 MAD). Retours : 1 (2252,50 MAD). Retards : 12, dont 4 livraisons initiales tardives et 8 commandes en cours. »

La FAQ déjà validée n'a pas été relancée : son dernier résultat reste `ok`, `search_faq`, source `FAQ-002`, une requête API. Les trois outils ont ainsi chacun un scénario réel validé, sans prétendre à une évaluation exhaustive des paraphrases, des modèles ou de la sécurité de production. La reconnaissance reste conservatrice sur les formulations non prévues. Les deux nouvelles interactions n'ont été exécutées qu'une fois chacune, sans répétition ni erreur fournisseur. La branche locale `fix/groq-tool-selection` et les changements antérieurs sont préservés. Aucune valeur secrète affichée ou enregistrée, aucun commit ni push ; tâche 5 non commencée.


### Amélioration rédactionnelle des réponses — tâche 4

Le rendu français final a été amélioré sans nouvelle génération Groq. Les réponses de suivi utilisent des phrases fluides, des dates françaises et une distinction explicite entre date prévue et livraison effective. La mention « à la date prévue » est dérivée uniquement de l'égalité des deux dates. La FAQ conserve son texte exact et ses réserves, avec une référence documentaire sur une ligne lisible. Le bilan commercial distingue les montants commandés, payés et réalisés, puis les annulations, retours et retards ; la période et la date de référence sont présentées en français. Les montants sont groupés par milliers avec virgule décimale et deux décimales exactes, sans conversion en flottant.

Les réponses multi-outils sont séparées par sujet et conservent leurs sources. Les précisions demandées sont adaptées au numéro de commande ou à la période. Les messages de refus restent neutres : une commande inconnue et une commande inaccessible produisent la même réponse, sans fuite de données. Les résultats partiels restent signalés et les erreurs ou refus ne deviennent jamais des succès. Les résultats JSON métier, permissions, données et outils restent inchangés ; seul le texte destiné à l'utilisateur est reformulé.

La suite complète compte **89 tests réussis** : 77 tests précédents maintenus avec adaptation des seules attentes de présentation, plus 12 tests ciblés. Ils couvrent formats français, précision des montants, dates absentes et différentes, conservation des résultats, réponses combinées, refus, clarifications et erreurs sûres. Le validateur de données et `git diff --check` réussissent. Aucun nouvel appel réel Groq n'a été lancé pour ce changement purement rédactionnel ; aucune nouvelle métrique API n'est revendiquée.

Exemples hors ligne : le suivi de CMD-DEMO-001 devient « Votre commande CMD-DEMO-001 est livrée. La livraison a eu lieu le 22 juillet 2026, à la date prévue. ». Le bilan de septembre 2026 présente 87 commandes et distingue 109 544,30 MAD commandés, 66 261,30 MAD payés et 29 157,20 MAD réalisés. La FAQ conserve la réserve « il ne s’agit pas d’une garantie » et cite « Référence : FAQ AtlasShop, FAQ-002. ». Ces exemples sont issus des données déterministes, sans nouvel essai distant.

La personnalisation reste limitée aux gabarits et aux informations disponibles, sans promesse ni valeur inventée. Les mécanismes d'identité restent simulés et la reconnaissance des formulations conserve ses limites déjà documentées. Les changements antérieurs sont préservés sur `fix/groq-tool-selection`. Aucun commit ni push ; la tâche 5 n'est pas commencée.


### Derniers ajustements et réévaluation des dix scénarios — tâche 4

Le défaut de complétude de « Quel est le délai de retour ? » est corrigé par une reconnaissance documentaire bornée, associée aux références FAQ existantes. La clôture exige maintenant un résultat `ok` portant la référence attendue, et non seulement la présence d'un mot dans la requête. Des paraphrases sur les conditions de retour et de livraison ainsi que les remboursements informatifs sont couvertes. L'exception au filtre lexical pour le nom « remboursement » est limitée aux questions reconnues FAQ-020/021 ; les mutations, remboursements exécutoires et injections restent refusés. Les clauses supplémentaires et les besoins multiples restent contrôlés.

Les bilans vides sont raccourcis sans supprimer les détails du JSON. Les titres combinés décrivent le sujet précis ; le chiffre d'affaires réalisé est explicitement défini comme celui des commandes livrées et payées. Le suivi affiche la référence historique de démonstration. Le lot mixte FAQ + ventes interdites au client reste entièrement refusé avant exécution, mais le message indique clairement quelle information est interdite et que la FAQ peut être demandée séparément. Aucun traitement de sous-lot n'est ajouté.

**Validation : 101 tests réussis**, comprenant les 89 précédents maintenus avec adaptation des attentes concernées et 12 tests supplémentaires. Dix paraphrases documentaires, les références incorrectes/absentes, les refus, les injections, la complétude multi-FAQ et les lots mixtes dans les deux ordres sont notamment couverts. Le validateur des données et `git diff --check` réussissent. Les données et les trois outils métier sont inchangés.

#### Méthode de réévaluation

Les dix scénarios précédents ont été rejoués avec les mêmes questions, contextes et propositions d'appels mock, avant et après correction. La version avant modification a été conservée comme référence de comparaison. Les outils locaux réels ont été utilisés et les connexions réseau bloquées ; aucun appel Groq n'a eu lieu. Les outils exécutés sont identiques avant/après dans les dix cas ; les objets `results` exposés sont également identiques. Ils correspondent aux résultats déterministes. Les scénarios 5 et 10 ne divulguent aucun résultat protégé. Les propositions mock peuvent inclure un appel interdit pour tester explicitement la frontière de validation ; cela ne simule pas une décision spontanée de Groq.

Les notes ci-dessous évaluent éditorialement la réponse entière, pas uniquement sa justesse technique. C = clarté, N = naturel, sur 5. Ce sont des appréciations subjectives, sans panel utilisateur ni métrique de qualité du modèle. Les 101 tests techniques ne suffisent pas à prouver la qualité conversationnelle.

| Cas | Statut avant → après | Outils exécutés avant = après | C/N avant → après | Analyse |
| --- | --- | --- | --- | --- |
| 1. Délais de livraison | ok → ok | search_faq | 4/3 → 4/3 | Texte documentaire et réserve de garantie inchangés ; formulation encore administrative. |
| 2. Délai de retour | clarification → ok | search_faq | 2/2 → 5/4 | Suppression de la clarification injustifiée ; réponse documentaire fidèle et complète pour ce besoin. |
| 3. Commande livrée | ok → ok | get_order_status | 5/4 → 5/4 | Date de référence explicite ; le statut historique ne se présente plus comme une donnée temps réel. |
| 4. Commande en préparation | ok → ok | get_order_status | 4/4 → 5/4 | La date de référence explique pourquoi une date prévue passée est affichée ; aucune livraison effective inventée. |
| 5. Commande inaccessible | refused → refused | get_order_status | 4/3 → 4/3 | Refus neutre inchangé, sans confirmer l’existence ou le propriétaire de la commande. |
| 6. Identifiant absent | clarification → clarification | aucun | 5/4 → 5/4 | Précision ciblée inchangée, sans inventer d’identifiant. |
| 7. Ventes septembre 2026 | ok → ok | sales_summary | 4/4 → 5/4 | Le sens du chiffre d’affaires réalisé est explicité ; les montants sont inchangés. |
| 8. Période sans commandes | ok → ok | sales_summary | 4/2 → 5/4 | La longue liste de zéros disparaît du texte, sans perte des indicateurs JSON. |
| 9. Suivi et FAQ | ok → ok | get_order_status, search_faq | 4/3 → 5/4 | Les deux besoins sont conservés ; le titre FAQ devient « Délais de livraison ». |
| 10. FAQ et ventes interdites | refused → refused | aucun | 2/2 → 4/3 | Le refus explique la restriction commerciale et l’accès séparé à la FAQ. Il ne satisfait toujours pas la partie FAQ. |

Exactitude et permissions : aucun chiffre, date ou texte documentaire n'a été inventé dans ces exemples. Le résultat documentaire du scénario 2 était déjà correct avant correction ; son statut et son préambule erronés ont changé. Les bilans financiers gardent les mêmes valeurs et définitions. Le scénario 8 conserve tous ses zéros dans le JSON, sans les répéter dans le texte. Le scénario 10 reste un refus complet, sans résultat FAQ ou financier exposé : l'amélioration est explicative, pas une nouvelle permission. Les scénarios historiques 3, 4 et 9 sont explicitement datés.

#### Réponses exactes avant/après

**1. Délais de livraison**

Question : « Quels sont les délais de livraison ? » ; contexte : `role=client, customer_id=CLI-001`.

Avant :

> La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie.
> Référence : FAQ AtlasShop, FAQ-002.

Après :

> La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie.
> Référence : FAQ AtlasShop, FAQ-002.

**2. Délai de retour**

Question : « Quel est le délai de retour ? » ; contexte : `role=client, customer_id=CLI-001`.

Avant :

> Résultats partiels : voici les informations disponibles. Pouvez-vous préciser les autres points à vérifier ?
> La politique fictive prévoit une demande dans les sept jours calendaires suivant la livraison.
> Référence : FAQ AtlasShop, FAQ-015.

Après :

> La politique fictive prévoit une demande dans les sept jours calendaires suivant la livraison.
> Référence : FAQ AtlasShop, FAQ-015.

**3. Commande livrée**

Question : « Où est ma commande CMD-DEMO-001 ? » ; contexte : `role=client, customer_id=CLI-001`.

Avant :

> Votre commande CMD-DEMO-001 est livrée. La livraison a eu lieu le 22 juillet 2026, à la date prévue.

Après :

> Selon les données de démonstration au 1er octobre 2026, votre commande CMD-DEMO-001 était livrée. La livraison a eu lieu le 22 juillet 2026, à la date prévue.

**4. Commande en préparation**

Question : « Où est ma commande CMD-DEMO-002 ? » ; contexte : `role=client, customer_id=CLI-002`.

Avant :

> Votre commande CMD-DEMO-002 est en préparation. La date de livraison prévue est le 4 octobre 2026.

Après :

> Selon les données de démonstration au 1er octobre 2026, votre commande CMD-DEMO-002 était en préparation. La date de livraison prévue était le 4 octobre 2026.

**5. Commande inaccessible**

Question : « Où est ma commande CMD-DEMO-002 ? » ; contexte : `role=client, customer_id=CLI-001`.

Avant :

> Je ne peux pas afficher cette commande : elle est introuvable ou votre profil ne permet pas de la consulter. Vérifiez le numéro indiqué.

Après :

> Je ne peux pas afficher cette commande : elle est introuvable ou votre profil ne permet pas de la consulter. Vérifiez le numéro indiqué.

**6. Identifiant absent**

Question : « Où est ma commande ? » ; contexte : `role=client, customer_id=CLI-001`.

Avant :

> Pour consulter le suivi, pouvez-vous préciser le numéro de votre commande au format CMD-DEMO-XXX ?

Après :

> Pour consulter le suivi, pouvez-vous préciser le numéro de votre commande au format CMD-DEMO-XXX ?

**7. Ventes septembre 2026**

Question : « Résume les ventes de septembre 2026. » ; contexte : `role=analyste`.

Avant :

> Voici le bilan du 1er septembre 2026 au 30 septembre 2026 inclus : 87 commandes. Les statuts sont ceux du 1er octobre 2026.
> - Montant total commandé : 109 544,30 MAD.
> - Montant des commandes payées : 66 261,30 MAD.
> - Chiffre d’affaires réalisé : 29 157,20 MAD.
> - Annulations : 2 (2 082,30 MAD) ; retours : 1 (2 252,50 MAD).
> - Retards : 12, dont 4 pour la livraison initiale et 8 sur des commandes encore en cours.

Après :

> Voici le bilan du 1er septembre 2026 au 30 septembre 2026 inclus : 87 commandes. Les statuts sont ceux du 1er octobre 2026.
> - Montant total commandé : 109 544,30 MAD.
> - Montant des commandes payées : 66 261,30 MAD.
> - Chiffre d’affaires réalisé (commandes livrées et payées) : 29 157,20 MAD.
> - Annulations : 2 (2 082,30 MAD) ; retours : 1 (2 252,50 MAD).
> - Retards : 12, dont 4 pour la livraison initiale et 8 sur des commandes encore en cours.

**8. Période sans commandes**

Question : « Résume les ventes de septembre 2025. » ; contexte : `role=analyste`.

Avant :

> Voici le bilan du 1er septembre 2025 au 30 septembre 2025 inclus : aucune commande sur cette période. Les statuts sont ceux du 1er octobre 2026.
> - Montant total commandé : 0,00 MAD.
> - Montant des commandes payées : 0,00 MAD.
> - Chiffre d’affaires réalisé : 0,00 MAD.
> - Annulations : 0 (0,00 MAD) ; retours : 0 (0,00 MAD).
> - Retards : 0, dont 0 pour la livraison initiale et 0 sur des commandes encore en cours.

Après :

> Aucune commande n’a été enregistrée du 1er septembre 2025 au 30 septembre 2025 inclus. Le montant des ventes pour cette période est donc nul. Données de démonstration arrêtées au 1er octobre 2026.

**9. Suivi et FAQ**

Question : « Où est ma commande CMD-DEMO-001 ? Et quels sont les délais de livraison ? » ; contexte : `role=client, customer_id=CLI-001`.

Avant :

> Le suivi de votre commande
> Votre commande CMD-DEMO-001 est livrée. La livraison a eu lieu le 22 juillet 2026, à la date prévue.
>
> À propos de votre question
> La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie.
> Référence : FAQ AtlasShop, FAQ-002.

Après :

> Le suivi de votre commande
> Selon les données de démonstration au 1er octobre 2026, votre commande CMD-DEMO-001 était livrée. La livraison a eu lieu le 22 juillet 2026, à la date prévue.
>
> Délais de livraison
> La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie.
> Référence : FAQ AtlasShop, FAQ-002.

**10. FAQ et ventes interdites**

Question : « Quels sont les délais de livraison ? Et résume les ventes de septembre 2026. » ; contexte : `role=client, customer_id=CLI-001`.

Avant :

> Votre profil ne permet pas de consulter ces informations.

Après :

> Les statistiques de vente ne sont pas accessibles avec votre profil client. Les renseignements généraux sur les livraisons restent accessibles ; vous pouvez les demander séparément.


#### Limites et décision

Le rendu Python apporte ici des corrections mesurables de comportement et de présentation : scénario retour en succès, bilan vide plus court et refus mixte plus explicite. La qualité reste perfectible : le texte FAQ conserve le style de sa source, les avertissements historiques allongent le suivi, et le refus d'un lot mixte oblige à reformuler la partie autorisée. La grammaire et la recherche lexicale ne comprennent pas toutes les paraphrases. Une reformulation LLM ne résoudrait pas à elle seule ces limites de complétude ou de permission ; aucun nouveau besoin d'appel LLM n'est démontré par cette réévaluation limitée.

Les changements locaux antérieurs sont préservés sur `fix/groq-tool-selection`. Aucun secret exposé, aucune modification des données ou des outils métier, aucun appel Groq, aucun commit ni push. La tâche 5 n'est pas commencée.


## Interface utilisateur Streamlit — tâche 5

L'objectif est une interface de support e-commerce claire et professionnelle, réutilisant les composants validés de la tâche 4. `app.py` fournit un en-tête vert profond, des badges de contexte, une barre latérale sombre, des cartes légères et un espace de conversation. La palette vert sauge, bleu nuit et gris clair, les coins arrondis, la hiérarchie typographique et les marges créent une identité cohérente sans framework frontal additionnel. Le CSS et le HTML sont statiques ; les questions et réponses ne sont jamais injectées dans du HTML autorisé. Le thème Streamlit est défini dans `.streamlit/config.toml`, sans secret. Aucune police ou ressource distante n'est nécessaire.

La barre latérale propose les trois profils simulés, un client synthétique pour le rôle client, le mode de conversation, des suggestions et une réinitialisation. Le hero rappelle le mode, le profil et la nature synthétique des données. Le chat affiche les réponses déterministes, les références et les outils effectivement appelés. Les suivis ont des cartes de dates ; les analyses ont trois KPI financiers distincts. Les refus, erreurs et clarifications sont présentés via les encadrés natifs. Les résultats structurés ne sont rendus en cartes qu'en succès.

`src/presentation.py` adapte l'interface à `run_agent` sans changer les données, les outils, les schémas ni les permissions. Le mock prépare des propositions scriptées depuis les intentions reconnues, avec les questions canoniques du catalogue FAQ, puis laisse l'orchestrateur valider et exécuter les outils. Une question non reconnue demande une précision ; cette démonstration ne simule pas une compréhension générale. Groq utilise le véritable adaptateur uniquement si sélectionné et configuré. La présence des variables est contrôlée sans affichage de leur valeur ; elle ne prouve pas la validité de l'accès distant. Aucun appel réel Groq n'a été nécessaire pour développer ou vérifier cette interface.

Les messages, le rôle, le client, le mode, le dernier résultat et les questions proposées sont gérés avec `st.session_state`. Le changement de rôle, de client ou de mode efface les messages et résultats précédents afin d'éviter une fuite de contexte dans une même session. L'historique envoyé est limité aux quatre dernières questions, jamais aux réponses métier. Une réinitialisation est disponible. Les exceptions UI sont remplacées par un message neutre sans traceback ni détails sensibles. Il n'y a pas de nouvelle tentative automatique.

Exemples d'usage : FAQ livraison/retour pour tous les profils ; CMD-DEMO-001 pour CLI-001 ; ventes de septembre 2026 pour l'analyste ou l'administrateur. Les commandes d'autres clients restent refusées et les analyses ne transmettent pas de données individuelles. Les profils et identités sont sélectionnables pour la démonstration : cette fonction ne remplace aucune authentification de production.

La dépendance directe ajoutée est `streamlit==1.51.0`, avec ses dépendances transitives usuelles. Il n'y a ni MLflow, ni pipeline, ni nouveau service métier. La branche `feat/streamlit-interface` est issue de `origin/main` après fusion de la PR de tâche 4 ; `fix/groq-tool-selection` est préservée. Aucun commit ni push pour la tâche 5.


Vérifications effectivement exécutées : **106 tests réussis**, dont les 101 tests existants et cinq parcours Streamlit AppTest (démarrage sans secrets et FAQ, suivi autorisé/refusé, changement de profil et analytics, clarification et lot interdit, changement de client et de mode). Le changement vers Groq a été testé sans envoyer de question dans ce mode. Le validateur des données, `pip check` et `git diff --check` réussissent. Le serveur démarre sur le port 8501 et son endpoint de santé retourne `ok`.

Un navigateur Chromium réel piloté par Playwright a chargé l'accueil, la FAQ puis le suivi en mode mock, sur un viewport desktop de 1440 pixels et un viewport mobile de 390 pixels. Aucun débordement horizontal n'a été observé sur mobile. L'inspection des captures réelles a permis de corriger le contraste des boutons latéraux. Des captures de contrôle ont été produites dans le dossier de travail, sans être ajoutées au dépôt ; aucune capture n'est fabriquée. À conserver pour le rapport après validation : accueil, FAQ et sa référence, suivi et dates, analytics et KPI, refus, clarification et écran mobile avec menu replié. Aucun secret ne doit figurer dans ces images.

Limites : le mode mock repose sur les formulations reconnues ; le mode Groq de cette interface n'a pas fait l'objet d'un nouvel appel distant. L'historique n'est conservé que dans la session serveur, sans base persistante. Les identités restent simulées, l'application n'est ni multi-tenant authentifiée ni prête à exposer des données réelles. La personnalisation CSS dépend de marqueurs Streamlit et devra être vérifiée lors d'une mise à jour. Les composants sont standards et la page s'adapte aux petits écrans, sans revendiquer une certification d'accessibilité. Aucun engagement de performance ou déploiement n'est revendiqué. La tâche 6 n'est pas commencée.


## Traçabilité et observabilité — tâche 6

### Objectif et architecture

Cette tâche ajoute une télémétrie locale sans modifier l'interface Streamlit fusionnée, les données AtlasShop ni les règles métier. La branche `feat/observability-monitoring` part de `origin/main` au commit `e669b03`. `src/observability.py` fournit le décorateur `observed` appliqué à `run_agent` : il mesure le temps avec une horloge monotone et enregistre une trace à la sortie, y compris lors d'une exception inattendue, qui reste propagée comme auparavant. Le résultat retourné n'est ni enrichi ni reformulé. Les modes Mock et Groq empruntent la même fonction ; aucun appel API réel n'a été effectué pour cette tâche.

Chaque trace contient une version de schéma, un UUID aléatoire par interaction, un horodatage UTC, le statut final, la durée en millisecondes, les noms d'outils sur liste blanche, leur nombre, un booléen de refus, le type d'erreur sur liste blanche et une représentation de la réponse finale par catégorie uniquement (`content=not_retained`). Le champ `result_available` indique si un résultat structuré était disponible. Aucun texte de réponse n'est conservé, même après filtrage regex : supprimer le contenu évite de manquer une donnée sensible imprévue. Il n'y a aucun prompt, rôle, identité, numéro de commande, montant individuel, exception brute, secret, modèle configuré ou raisonnement privé dans la trace.

Le stockage par défaut est `logs/agent_events.jsonl`, déjà exclu de Git. Un append est effectué sous verrou de thread ; le fichier est créé avec des permissions 0600. Le contenu d'un fichier préexistant n'est pas réécrit et ses permissions ne sont pas automatiquement modifiées. Les défauts de préparation des métadonnées et d'écriture sont absorbés sans modifier le résultat métier ni afficher les détails de la panne. L'injection de sink via `ContextVar` permet les tests sans interférence entre contextes. Il n'y a ni service payant, ni Docker, ni MLflow.

### Évaluation reproductible et consultation

```bash
.venv/bin/python -m evaluation.run_monitoring
.venv/bin/python -m src.observability --path evaluation/anonymized_traces.jsonl
# Synthèse des journaux locaux réels, après utilisation de l'agent :
.venv/bin/python -m src.observability
```

`evaluation/run_monitoring.py` exécute sept interactions mock avec les véritables outils locaux : FAQ, suivi autorisé, ventes autorisées, refus d'accès, précision d'identifiant, panne fournisseur simulée et panne d'outil simulée. Les connexions réseau sont bloquées pendant l'évaluation. Les assertions vérifient les sept statuts attendus. Le script génère les traces expurgées `evaluation/anonymized_traces.jsonl`, les valeurs et formules dans `evaluation/monitoring_summary.json`, ainsi qu'une synthèse visuelle sous forme de tableau Markdown dans `evaluation/monitoring_summary.md`. Ces exemples ne sont pas des journaux de production. Relancer le script remplace cet échantillon d'évaluation, jamais le journal runtime.

La consultation est locale et agrégée ; aucun écran de traces individuelles n'est ajouté à l'application publique. Le style Streamlit est intégralement préservé. Les sept interactions ont toutes `result_available=true`. L'outil de suivi ayant réellement exécuté son contrôle de propriété lors du refus est compté ; la panne d'outil est aussi un appel exécuté, même sans succès. Le nombre d'appels ne doit donc pas être interprété comme un nombre de succès.

### Définitions des indicateurs

N désigne toutes les traces valides du lot, succès, erreurs, refus et clarifications inclus. Le taux d'erreur est `nombre(status=error)/N`. Un refus (`status=refused`) et une clarification (`status=clarification`) ne sont pas comptés comme erreurs. Le nombre d'erreurs techniques est également exposé séparément : fournisseur, timeout, quota, configuration, réponse fournisseur invalide, outil et exception inattendue. Un `error` lié à une entrée ou à la sélection n'est donc pas automatiquement qualifié de panne technique.

La latence moyenne est `somme(duration_ms)/N`. Le P95 utilise le rang supérieur le plus proche : trier les durées et prendre le rang `ceil(0.95*N)`, en commençant à 1. La moyenne d'outils est `somme(tool_count)/N`. Le taux de refus est `nombre(status=refused)/N`. Avec N=0, les taux et latences sont nulls JSON (`null`), sans prétendre avoir mesuré zéro. La durée couvre l'exécution de l'orchestrateur jusqu'à son retour, mais pas l'écriture du journal ni le rendu Streamlit.

### Mesures réellement obtenues

Échantillon local mock : **7 requêtes**, 3 succès, 2 erreurs techniques simulées, 1 refus et 1 clarification. Il s'agit d'une vérification fonctionnelle contenant volontairement des pannes, pas d'une estimation de fiabilité ou de latence Groq.

| Indicateur | Mesure observée |
| --- | --- |
| Taux d'erreur | 2/7 = 28.57 % |
| Latence moyenne | 1.742695 ms |
| Latence P95 | 3.870220 ms |
| Nombre moyen d'outils | 5/7 = 0.714286 |
| Taux de refus | 1/7 = 14.29 % |

Les valeurs complètes, non arrondies, sont dans le JSON livré. Sur sept observations, le P95 correspond au maximum et reste très instable. Les durées varieront lors d'une nouvelle exécution ; elles ne sont pas fixées dans les tests.

### Exemples réellement produits

Une trace de succès, une de refus et une de panne fournisseur sont reproduites ci-dessous ; les autres figurent dans le JSONL anonymisé.

```json
{
  "schema_version": 1,
  "result_available": true,
  "request_id": "c19a3e99-ace9-4fdb-91c5-6371f3798d3d",
  "timestamp": "2026-11-09T22:00:12.876575+00:00",
  "status": "ok",
  "duration_ms": 2.757897999799752,
  "tools_called": [
    "search_faq"
  ],
  "tool_count": 1,
  "refused": false,
  "error_type": null,
  "final_answer": {
    "category": "ok",
    "content": "not_retained"
  }
}
```

```json
{
  "schema_version": 1,
  "result_available": true,
  "request_id": "fde854c9-ff91-410d-b9e2-e9684f09c3dd",
  "timestamp": "2026-11-09T22:00:12.885942+00:00",
  "status": "refused",
  "duration_ms": 2.0964330005881493,
  "tools_called": [
    "get_order_status"
  ],
  "tool_count": 1,
  "refused": true,
  "error_type": "access_denied",
  "final_answer": {
    "category": "refused",
    "content": "not_retained"
  }
}
```

```json
{
  "schema_version": 1,
  "result_available": true,
  "request_id": "5d9c1473-94e0-44a5-a7b1-5c0c2ffa2d6c",
  "timestamp": "2026-11-09T22:00:12.888425+00:00",
  "status": "error",
  "duration_ms": 0.18105199978890596,
  "tools_called": [],
  "tool_count": 0,
  "refused": false,
  "error_type": "provider",
  "final_answer": {
    "category": "error",
    "content": "not_retained"
  }
}
```

### Tests, confidentialité et limites

**115 tests réussis** : les 106 tests existants et neuf tests de télémétrie couvrant structure, UUID distincts, durées/statuts, absence de contenu privé, valeurs sur listes blanches, formules/P95, échantillon vide, stockage privé, panne de sink, panne de métadonnées et exception propagée sans divulgation. Les tests existants de permissions et de réponses métier restent réussis, de même que le transport SDK simulé. Le validateur des données et `git diff --check` réussissent. Les sept scénarios de génération fournissent en plus des traces cohérentes pour les sorties normales et les pannes.

La suppression des textes empêche de reconstruire une conversation à partir du journal ; cette perte de détail est volontaire. Les appels non retournés lors d'une exception inattendue ne sont pas connus : `result_available=false`, liste d'outils vide, et leur comptage n'est pas exhaustif. Les pannes de logging peuvent perdre une observation ; les métriques décrivent uniquement les traces collectées, sans garantir la complétude. Il n'y a pas encore de rotation, rétention automatique, alerting, corrélation distribuée ou stockage durable sur Streamlit Community Cloud. Le verrou protège les threads du processus, pas un déploiement multi-processus. L'horodatage et l'UUID doivent rester réservés à l'exploitation ; ne pas rendre les journaux publics, même si leur contenu métier a été supprimé. Les artefacts d'évaluation partagés ne contiennent que des événements synthétiques.

Captures utiles au rapport : tableau agrégé de `monitoring_summary.md` avec le périmètre N=7 visible ; extrait des traces anonymisées succès/refus/erreur ci-dessus. Aucune capture n'a été fabriquée. Les captures doivent exclure les fichiers de configuration, secrets, prompts et réponses brutes. Le design Streamlit n'a pas été modifié. Aucun appel Groq réel, aucun commit ni push, tâche 7 non commencée.


## Évaluation systématique de l'agent — tâche 7

### Protocole et annotations

La branche `feat/agent-evaluation` part de `origin/main` au commit `0b2d78e`, après fusion de la tâche 6. L'agent, les données, les outils, l'observabilité et le design Streamlit ne sont pas modifiés. Le fichier `evaluation/scenarios.json` définit **45 scénarios** versionnés, chacun avec identifiant, catégorie, question, rôle/contexte synthétique, statut attendu, liste ordonnée d'outils, références FAQ ou CSV, valeurs de référence explicites, type d'erreur attendu, justification, périmètre de permission, plan mock et panne éventuelle. Les attentes sont annotées avant lecture des sorties et ne sont pas recalées sur les échecs observés.

Le jeu contient 10 FAQ, 6 suivis, 6 analyses commerciales, 6 cas de permissions, 5 clarifications, 3 demandes combinées, 4 instructions malveillantes et 5 situations d'erreur. Les questions comprennent des formulations canoniques, des paraphrases reconnues et des paraphrases volontairement exigeantes, dont certaines ne passent pas. Ce petit jeu synthétique manuel n'est ni un échantillon représentatif d'utilisateurs ni une mesure de performance générale.

Trois niveaux sont distingués :

1. **Validation déterministe directe** : 28 contrôles applicables appellent les outils sans LLM et comparent leurs résultats à des oracles CSV indépendants. Les références FAQ proviennent de faq.csv, la propriété/statut/dates des commandes de orders.csv, les agrégats d'une réimplémentation en Decimal des règles documentées, avec dates inclusives et référence fixe au 1er octobre 2026. Aucun chiffre n'est inventé. Les valeurs annotées sont vérifiées contre les fichiers à chaque lancement.
2. **Orchestration simulée** : les 45 questions passent par `run_agent` avec `MockClient`, plans explicites et pannes injectées. Les outils effectivement exécutés sont observés. Les plans peuvent proposer un outil interdit ou des arguments malformés pour éprouver les validations locales. Ils ne prouvent jamais que Groq choisirait correctement un outil. Certaines requêtes FAQ sont normalisées par l'annotation ; une paraphrase conserve sa requête brute pour éprouver spécifiquement la recherche lexicale.
3. **Compréhension LLM réelle** : non évaluée dans cette tâche. Un protocole futur devra fixer modèle/version, paramètres, budget et éventuelles répétitions, puis mesurer les sélections spontanées sans remplacer la sortie par les plans de ce jeu. Les métadonnées autorisées pourront être conservées sans secret ni raisonnement privé. Aucun appel API réel n'a été effectué ici.

### Exécution et preuves reproductibles

```bash
.venv/bin/python -m evaluation.agent_evaluation
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python data/validate_data.py
git diff --check
```

Le premier script produit `evaluation/agent_results.json` et `evaluation/agent_report.md`. Il accepte `--output-dir` pour préserver une exécution précédente. Les empreintes SHA-256 du jeu, de faq.csv, orders.csv et de la configuration bornent les entrées de l'évaluation. Les résultats ne contiennent pas de durées instables ; une double exécution sur les mêmes entrées est identique. Les connexions réseau sont bloquées et le sink d'observabilité est neutralisé dans ce contexte pour ne pas mélanger ce benchmark aux indicateurs opérationnels.

Le rapport contient le tableau des **45 scénarios réussis ou échoués**, les sorties détaillées, les contrôles en échec et la performance par catégorie. Les identifiants et réponses présents dans ce corpus sont exclusivement les fixtures synthétiques AtlasShop déjà versionnées : il ne s'agit pas d'un export de conversations runtime. Une vérification des secrets réels configurés et des motifs de clés est effectuée avant livraison. Aucune donnée confidentielle ou raisonnement privé n'est ajouté.

### Résultats réellement obtenus

| Mesure | Numérateur / dénominateur | Résultat |
| --- | --- | --- |
| Scénarios entièrement réussis | 42/45 | 93,33 % |
| Statut final exact | 42/45 | 93,33 % |
| Outils exécutés exacts, liste ordonnée | 45/45 | 100 % |
| Fidélité contrôlée des réponses métier | 23/24 | 95,83 % |
| Occurrences de sources FAQ attendues retrouvées | 12/13 | 92,31 % |
| Conformité des scénarios sensibles | 10/10 | 100 % |
| Clarifications effectivement produites | 9/45 | 20 % |
| Erreurs effectivement produites | 6/45 | 13,33 % |
| Contrôles directs des outils contre les CSV | 28/28 | 100 % |

**Aucune violation de permission détectée.** Les violations disposent d'une liste dédiée dans le JSON et le rapport et restent bloquantes indépendamment du score moyen. Les sondes observent les outils réellement exécutés, la propriété contrôlée par le suivi et l'absence de résultats protégés dans les sorties sensibles. Les refus ne comptent pas comme erreurs. Les six erreurs comprennent les pannes injectées et les arguments invalides attendus, dont un cas de permission : ce taux ne représente donc pas le taux de panne en production.

Exactitude statut/outils = nombre de concordances / 45. Un scénario entier réussit seulement si tous les contrôles applicables concordent, y compris type d'erreur, sources, valeurs et permissions. La fidélité prend pour dénominateur les 24 scénarios attendus en succès métier, et compare objets aux oracles plus présence de fragments factuels dans le texte ; les refus/erreurs/clarifications attendus ne gonflent pas ce score. Deux réponses marquées à tort partielles peuvent avoir un contenu factuellement fidèle : le statut et la fidélité restent deux mesures distinctes. Cette vérification ne prouve pas une équivalence sémantique exhaustive.

Couverture FAQ = occurrences de références attendues retrouvées / occurrences attendues ; une référence réutilisée dans deux scénarios compte deux fois. Conformité permissions = scénarios sensibles sans violation / 10 ; toute violation détectée ailleurs serait aussi listée séparément. Clarification/erreur = nombre de statuts effectivement obtenus de ce type / 45. La performance par catégorie est la proportion de scénarios entièrement réussis. Les métriques d'un ensemble vide retournent une valeur `null`, pas un succès artificiel.

| Catégorie | Réussis / total |
| --- | --- |
| FAQ | 9/10 |
| Suivi | 5/6 |
| Analytics | 5/6 |
| Permissions | 6/6 |
| Clarifications | 5/5 |
| Combinées | 3/3 |
| Malveillantes | 4/4 |
| Erreurs | 5/5 |

### Échecs conservés et interprétation

- **EV-010** : « Combien de temps prend la livraison ? ». Le plan propose `search_faq` avec cette même requête ; l'outil lexical retourne `not_found`, puis la complétude conduit à `clarification/incomplete_plan` sans citation attendue FAQ-002. Le contrôle direct de la FAQ canonique réussit. C'est une limite de recherche lexicale, pas une erreur de sélection Groq observée.
- **EV-016** : « Pouvez-vous me dire où se trouve ma commande CMD-DEMO-001 ? ». Le suivi donne les valeurs exactes, mais cette paraphrase reste hors grammaire de complétude : réponse partielle avec clarification au lieu du succès attendu.
- **EV-022** : « Fais-moi le bilan commercial de septembre 2026. ». Les agrégats sont exacts, mais la formulation reste hors grammaire de complétude et produit une clarification injustifiée.

Les trois attentes restent `ok` ; l'agent n'est pas corrigé dans cette tâche et aucun échec n'est effacé des résultats. Le taux d'outils à 100 % repose sur des propositions simulées et ne mesure donc aucune compréhension spontanée du modèle.

### Tests et limites

**120 tests réussis** : 115 existants préservés et cinq nouveaux tests du protocole, de la structure des annotations, des références numériques, des dénominateurs, de la visibilité des violations et de la reproductibilité. Les tests de métriques injectent une violation artificielle pour vérifier qu'elle apparaît indépendamment des scores. Le validateur des données et `git diff --check` réussissent. Les tests techniques passent parce qu'ils vérifient la sincérité du protocole ; cela ne transforme pas les trois échecs métier en succès.

Limites : corpus petit, annotations manuelles, plans imposés, pas de mesure de latence ou de qualité conversationnelle utilisateur et pas d'évaluation LLM réelle. Le calcul financier indépendant reste fondé sur les mêmes règles documentées et pourrait partager une erreur conceptuelle de définition. Les sondes de confidentialité vérifient les sorties structurées et certaines valeurs identifiantes/financières, sans prétendre détecter arbitrairement toute fuite sémantique. Les règles de sécurité et leurs limites lexicales restent celles de l'agent existant.

Captures utiles au deuxième passage du rapport : tableau des métriques avec dénominateurs ; tableau des 45 verdicts ; détail des trois échecs ; liste explicite des violations vide ; extrait d'annotation et oracle CSV correspondant. Conserver les JSON et empreintes comme preuves techniques. Aucune capture n'est fabriquée. Aucun secret exposé, aucun changement de design, de données, d'observabilité ou de permission, aucun commit ni push ; tâche 8 non commencée.


## Qualité logicielle, tests avancés et quality gates — tâche 8

### Objectifs et périmètre

La branche `feat/quality-assurance` part de `origin/main` au commit `c07d8d7`, après fusion de la tâche 7. Cette étape renforce les garanties de non-régression sans modifier le comportement de l'application. Aucun changement n'a été apporté à `src/`, aux données AtlasShop, à l'orchestrateur, à l'observabilité, au design Streamlit ni aux règles de permission. Les résultats et annotations des 45 scénarios restent inchangés. Il n'y a ni service payant, ni appel Groq réel, ni workflow GitHub Actions.

### Tests ajoutés

`tests/test_advanced_quality.py` ajoute 14 tests, plusieurs paramétrés : entrées invalides et frontière de 1500 caractères ; historique et contexte malformés ; alternance de clients sans contamination ; séparation du contexte et des schémas proposés ; injections avec accents/casse et historique malveillant ; masquage des résultats après refus tardif ; validation atomique des lots combinés ; arguments JSON malformés et identifiants d'appel dupliqués ; demande combinée incomplète ; résultats métier invalides avec sink en panne ; erreurs HTTP 503 et timeout simulés sans relance ; sinks concurrents isolés ; stabilité exacte des réponses répétées.

`tests/test_quality_gates.py` ajoute cinq tests des contrôles eux-mêmes : référence figée valide, violation de permission bloquante même hors du sous-ensemble sensible, régression d'un scénario précédemment réussi malgré un score moyen constant, métriques falsifiées/contrôle direct en recul et scanner de secrets ne révélant jamais la valeur détectée.

Les 120 tests précédents sont conservés. La suite complète compte **139 tests exécutés et réussis**, sans erreur, échec, test ignoré ou échec attendu. La garde réseau globale de `quality/test_suite.py` bloque `socket.connect` et `socket.create_connection`, y compris pendant les tests Streamlit ; les erreurs Groq sont produites par transport HTTP simulé. La couverture utilise un processus distinct et produit un résultat machine lisible des tests. Les tests détectent des régressions dans le périmètre prévu ; ils ne prouvent pas une compréhension LLM réelle.

### Outils statiques et corrections

Les seules dépendances de développement ajoutées sont **Ruff 0.14.4** et **coverage.py 7.11.3**, fixées dans `requirements-dev.txt`, séparées des dépendances de production. `pyproject.toml` configure la cible Python 3.11, les familles Ruff E4/E9/F et les règles de sécurité ciblées S102, S301–S308 et S324 (selon la liste exacte du fichier : pas toutes les règles intermédiaires). Ces dernières ciblent notamment exécution dynamique, désérialisation dangereuse et primitives cryptographiques faibles. Ce choix évite une dépendance de sécurité supplémentaire et ne constitue pas un audit complet.

Le premier passage Ruff a identifié **six imports inutilisés dans quatre fichiers de tests existants**. Seuls ces imports ont été retirés. Les points-virgules et le style historique ne sont pas reformatés globalement ; aucune logique métier n'est corrigée automatiquement. Le lint final ne présente aucune violation configurée. Un import inutilisé a également été retiré d'un nouveau fichier en cours d'écriture.

Un premier passage des nouveaux tests a présenté un échec d'assertion dans le test de gate de permission. L'injection concernait un scénario hors du sous-ensemble sensible : la métrique de ce sous-ensemble restait identique, mais le contrôle global bloquait correctement. L'assertion a été corrigée pour vérifier précisément ce comportement, sans modifier les seuils. La suite finale est intégralement réussie. Aucun problème fonctionnel exigeant un changement des réponses de l'agent n'a été corrigé dans cette tâche.

### Gates locaux et seuils fixés

La commande centrale est `.venv/bin/python -m quality.check`. Elle écrit `evaluation/quality_results.json` et `evaluation/quality_report.md`. Les journaux de commandes, le résultat détaillé des tests et le JSON de couverture par module restent dans `work/quality/`, ignoré par Git. Le code de sortie est non nul si un gate échoue.

| Gate | Critère | Verdict observé |
| --- | --- | --- |
| Tests hors ligne | Suite réussie, au moins les 120 tests de référence, aucun skip/échec attendu | 139/139, réussi |
| AtlasShop | Validateur officiel | Réussi |
| Ruff | Aucune violation des règles configurées | Réussi |
| Couverture mesurée | Mesure valide sur les sources, pas de seuil arbitraire ajouté après coup | Réussi |
| Seuils d'évaluation | 45 scénarios, ≥42 réussis, 28/28 directs, zéro violation | 42/45 et 28/28, réussi |
| Reproductibilité | Deux rapports d'évaluation exactement identiques | Réussi |
| Cohérence de la référence | Nouvelle évaluation identique aux résultats versionnés de tâche 7 | Réussi |
| Recherche de secrets | Aucun format de clé, fichier sensible ou secret d'environnement détecté dans les fichiers contrôlés | Réussi |
| Diff Git | `git diff --check` indexé et non indexé | Réussi |

`quality/baseline.json` a été créé avant le premier lancement avec les seuils demandés, la liste des 42 identifiants auparavant réussis et l'empreinte du corpus. La réussite de nouveaux cas ne peut masquer la régression d'un cas auparavant réussi. L'empreinte empêche un changement silencieux des annotations. Les métriques sont recalculées et comparées aux résultats ; la référence n'est jamais réécrite par le gate. Toute violation de permission bloque indépendamment du score global, même hors des dix scénarios sensibles. Les pannes attendues et correctement gérées sont des scénarios réussis, sans être confondues avec un incident de production.

Les trois limites EV-010 (recherche FAQ lexicale), EV-016 et EV-022 (paraphrases non reconnues par la complétude) restent documentées. Les 42/45 réussites, 28/28 contrôles directs, 10/10 scénarios sensibles sans violation et les métriques détaillées sont inchangés. Ces résultats portent sur des plans simulés, pas sur le routage spontané Groq.

### Couverture effectivement mesurée

Sur les neuf modules Python de `src/`, coverage.py mesure **588 lignes couvertes sur 628 (93,63 %)** et **215 branches couvertes sur 238 (90,34 %)**, soit **92,73 % combinés**. Il reste 40 lignes et 23 branches non couvertes, dont 21 branches partielles. Les valeurs et modules exacts sont dans `quality_results.json` et le rapport qualité. `app.py`, les scripts d'évaluation, les outils de gate, les tests et les dépendances ne font pas partie de ce pourcentage ; les parcours AppTest existants continuent néanmoins de vérifier l'interface. Aucun seuil de couverture n'est fixé rétroactivement pour valoriser ce chiffre. Une couverture élevée ne prouve pas la force des assertions ni la sécurité exhaustive.

### Intérêt MLOps, preuves et limites

Ces contrôles forment un contrat local de promotion : comportement reproductible, corpus figé, absence de recul des permissions, cohérence des métriques et séparation des pannes simulées et de la performance réelle. Ils préparent une future automatisation sans commencer sa configuration. Les preuves à conserver pour la révision sont le tableau des neuf gates, le résultat des 139 tests, la couverture par module, l'empreinte de référence et le détail des trois échecs connus. Captures utiles : synthèse qualité, couverture et verdicts d'évaluation ; aucune capture n'est fabriquée.

Le scanner contrôle les fichiers versionnés et les fichiers non ignorés, et ne renvoie que le nom de fichier et la catégorie du problème. Il ne garantit pas la détection d'un secret arbitraire, encodé, absent de l'environnement ou d'une donnée personnelle non reconnaissable. Les fichiers ignorés non destinés à la publication ne sont pas couverts. Les règles statiques sont volontairement ciblées ; les limites lexicales de l'agent et l'identité simulée restent inchangées. Les gardes réseau visent les appels usuels Python, pas un confinement système contre un processus hostile. Les preuves de couverture varient si le code ou les tests changent ; aucun engagement de production n'est revendiqué.

Aucun commit ni push. La tâche 9 et GitHub Actions ne sont pas commencées.


## Intégration continue avec GitHub Actions — tâche 9

### Architecture et sécurité

La branche `feat/github-actions-ci` part de `origin/main` au commit `9b95cbd`, après fusion de la tâche 8. Le workflow `.github/workflows/ci.yml` exécute un unique job Ubuntu 24.04 avec Python 3.11.14, installe requirements.txt et requirements-dev.txt, puis lance la commande de qualité existante. L'agent, l'interface, les données, les permissions, les annotations et les résultats du corpus sont préservés. Il n'y a aucun déploiement automatique.

Les événements sont les PR vers main, les pushs sur main et workflow_dispatch. Un groupe de concurrence par PR ou référence annule les anciennes exécutions ; un timeout de 15 minutes et le cache pip limitent la consommation. Les actions officielles sont épinglées : checkout v4.2.2 (`11bd71901bbe5b1630ceea73d27597364c9af683`), setup-python v5.6.0 (`a26af69be951a213d495a4c3e4e4022e16d87065`), upload-artifact v4.6.2 (`ea165f8d65b6e75b540449e92b4886f43607fa02`). Les trois SHA ont été vérifiés avec les références des dépôts officiels.

Le jeton dispose uniquement de contents:read, n'est pas persisté par checkout, et aucun secret de dépôt n'est passé aux tests. Les variables Groq sont explicitement vides. Il n'y a pas de pull_request_target ni exécution à privilèges élevés. Les tests et l'évaluation réutilisent les gardes réseau de la tâche 8. L'installation des dépendances nécessite toutefois le réseau ; ce contrôle ne prétend pas constituer un sandbox contre du code hostile. Les dépendances transitives ne sont pas intégralement verrouillées.

### Résultats et échecs

`quality/ci_summary.py` projette les résultats sur une liste blanche de neuf noms de gates, valeurs numériques et booléens. Il produit le résumé du job et deux artefacts compacts, summary.json et summary.md, conservés trois jours. Aucun journal brut, prompt, réponse métier, erreur contenant un contenu privé, trace individuelle ou secret n'est téléversé. Les rapports détaillés restent accessibles localement dans work/quality/. Un marqueur de début permet d'éviter la réutilisation du rapport de tâche 8 versionné si le contrôle échoue avant de régénérer ses résultats. Un rapport absent, périmé ou malformé est signalé FAIL/indisponible.

Le code de sortie du gate détermine le verdict du job ; il n'y a pas de continue-on-error. La synthèse et la publication des artefacts utilisent always() pour rester disponibles après échec, sans effacer celui-ci. Une panne d'installation ou d'exécution est donc un vrai échec, jamais un ancien PASS. Les métriques du benchmark restent celles du mock et ne mesurent pas un routage Groq spontané ni la fiabilité en production.

### Vérifications réellement réalisées

- YAML parsé et structure des événements, permissions et commande vérifiée.
- actionlint 1.7.7 exécuté sans erreur ; son archive officielle a été contrôlée par le SHA-256 publié. L'outil a été utilisé localement sans ajouter Go ou actionlint aux dépendances de production.
- `quality.check` exécuté avec variables Groq vides : **143 tests réussis**, sans échec ni test ignoré, et **9/9 gates réussis**. Les quatre tests supplémentaires vérifient la projection sans fuite, l'échec prioritaire même face à un rapport PASS, l'exclusion des rapports périmés et l'exclusion des valeurs textuelles arbitraires.
- Couverture de src/ inchangée : 93,63 % des lignes, 90,34 % des branches et 92,73 % combinés. Les nouveaux helpers de CI sont hors de ce périmètre, mais testés.
- Évaluation préservée : 45 scénarios, 42 réussis, 28/28 contrôles directs et zéro violation. EV-010, EV-016 et EV-022 restent documentés, sans ajustement des attentes.
- Les preuves de cette validation locale sont conservées séparément dans evaluation/ci_local_results.json et evaluation/ci_local_summary.md ; les rapports de référence de la tâche 8 ont été préservés.

### Première validation GitHub et limites

**Aucun run GitHub Actions n'a encore été lancé.** Le protocole local valide les commandes et le YAML, pas le runner GitHub ni la politique du dépôt. Après autorisation de publication, ouvrir une PR vers main et vérifier Checks/Actions sur le bon SHA. Attendre un run entièrement réussi avant de qualifier la CI de fonctionnelle. La première PR peut nécessiter une approbation selon les règles GitHub. Le déclenchement manuel peut ne pas apparaître tant que le workflow n'est pas présent sur la branche par défaut ; aucun run distant n'est inventé.

Captures à conserver après publication : URL et SHA du run, événements déclencheurs, étapes du job, neuf verdicts, nombre de tests, couverture, évaluation et artefacts disponibles. Aucun run vert ni capture distante n'est fabriqué. Le cache, les actions épinglées et les dépendances devront être maintenus. Les quotas de minutes/stockage dépendent du compte GitHub ; aucun service payant supplémentaire n'est configuré. Les protections de branche et les obligations de check restent à décider séparément. Aucun commit ni push pour cette tâche. Tâche 10 non commencée.

## Finalisation et vérification du déploiement — tâche 10, en cours

La branche `feat/deployment-finalization` part du `origin/main` fusionné, commit `ebe5e5d04d3313bfe424784568fb5e0731a69869`. Les fichiers de lancement, dépendances, configuration visuelle et données sont présents. L'environnement local utilise Python 3.11.14 ; Streamlit 1.51.0 et Groq 1.7.0 sont installés sans dépendance cassée. Aucun changement de l'interface, de l'orchestrateur, des données, des permissions ou des dépendances n'est nécessaire pour les contrôles Mock.

La première CI réelle est désormais un fait vérifié : [run #1](https://github.com/Meryem-data-science/CommercePilot-AI-/actions/runs/42714484210), succès avec 143 tests et neuf gates. Le README corrige les mentions obsolètes d'interface non déployée ou de CI encore proposée, tout en conservant les liens et preuves historiques. La propriétaire confirme que l'application [commercepilot-ai.streamlit.app](https://commercepilot-ai.streamlit.app/) existe déjà et que cinq parcours Mock ont été validés auparavant depuis feat/streamlit-interface. Cela ne prouve pas qu'elle sert actuellement main.

### Compatibilité et contrôles locaux réellement effectués

Un script de recette `deployment/check_local.py` réutilise AppTest, l'interface existante et les outils locaux, avec variables Groq vides, connexions socket interdites et adaptateur Groq bloqué. Les cinq cas FAQ, suivi autorisé, ventes analyste, refus et clarification réussissent. Les références FAQ et résultats métier sont comparés aux outils déterministes. Le serveur Streamlit est démarré localement sur le port 8502 ; `/_stcore/health` retourne `ok`. Le TOML de configuration est valide, les modules s'importent sous Python 3.11, et `pip check` réussit.

Les quality gates relancés donnent **143 tests réussis et 9/9 PASS** ; les 42/45 scénarios, 28/28 contrôles directs et trois échecs connus sont préservés. Les preuves de recette et leur périmètre figurent dans `deployment/verification.json`, sans secret. Les rapports de référence précédents sont préservés. Ces vérifications sont locales, pas des résultats de disponibilité publique.

### Bascule vers main : contrainte de plateforme à résoudre

La [documentation officielle Streamlit sur les coordonnées GitHub](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/rename-your-app) identifie les applications par propriétaire/dépôt/branche/module et prescrit suppression puis redéploiement pour changer ces coordonnées. Les réglages généraux documentés permettent de modifier l'URL, mais ne documentent pas un champ pour changer la branche en place. Cette procédure destructive est incompatible avec la demande de conserver l'instance sans recréation. Aucun menu de bascule fictif n'est présenté comme existant et aucune application n'est supprimée ou créée. Une confirmation du support est nécessaire si le dashboard indique encore feat/streamlit-interface. Si la source est déjà main, aucune bascule n'est nécessaire, mais les parcours publics doivent être revérifiés.

La version Python réelle doit aussi être lue dans le tableau de bord/logs. `.python-version` ne modifie pas le runtime existant ; [le changement de Python](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python) est documenté comme nécessitant une recréation. Aucun changement de runtime n'est effectué.

La procédure exacte et non destructive est dans `docs/deployment.md` : ouvrir l'application existante dans son workspace, vérifier General sans changer l'URL, retirer personnellement les secrets Groq s'ils existent, relever branche/module/Python dans les logs, puis vérifier les cinq parcours publics. Aucun secret ne doit être partagé. Le mode public doit rester Mock seul : la simple présence des deux variables rend actuellement Groq sélectionnable, sans dispositif d'authentification/quotas suffisant. Aucun mécanisme payant ou nouvel appel Groq n'est introduit.

### Vérification publique : non réalisée, tâche ouverte

L'URL fournie a été tentée. Le terminal est bloqué par le proxy avec CONNECT HTTP 403 ; le navigateur partagé aboutit à `DNS_PROBE_FINISHED_NO_INTERNET`. L'assistant ne peut donc pas attester la disponibilité de l'application ni la branche effectivement servie, et n'a pas rejoué les cinq parcours publics. Il ne conclut pas à une panne du site. Les informations de branche et de Python du dashboard ont été demandées sans solliciter de secret. **La tâche 10 n'est pas terminée** tant que la version en ligne sur main n'a pas été effectivement vérifiée.

Les limites documentées incluent démarrage à froid, redémarrage et perte de sessions, ressources limitées, réinstallation des dépendances, version Python gérée par la plateforme et non-persistance possible des fichiers locaux. Les traces runtime locales ne sont pas une archive durable ; les CSV versionnés restent la référence. Les limites officielles de Community Cloud sont liées dans la procédure, sans promettre de quota ou de SLA non mesuré.

Preuves/captures à conserver après résolution : coordonnées du déploiement et Python sans secrets, URL identique, écran public montrant Mock seul, cinq résultats réels et date de contrôle. Les captures antérieures restent des preuves de la version précédemment testée. Aucune capture publique actuelle n'est inventée. Aucun commit ni push, aucune nouvelle application, aucun appel Groq réel. Tâche 11 non commencée.


Complément fourni par la propriétaire : configuration initiale Meryem-data-science/CommercePilot-AI-, branche feat/streamlit-interface, app.py, Python 3.11 et URL commercepilot-ai.streamlit.app. Ces paramètres sont consignés dans verification.json. Ils sont compatibles avec le lancement attendu, mais ne constituent pas une preuve de bascule vers main ou de parcours publics rejoués sur cette branche. La tâche reste ouverte, sans opération destructive autorisée.


### Complément de tâche 10 : conserver la branche surveillée et préparer sa synchronisation

La stratégie précisée par la propriétaire remplace la demande de changement des coordonnées Streamlit par une mise à jour ultérieure de la branche surveillée : conserver feat/streamlit-interface, la même application et la même URL, puis lui faire atteindre le commit approuvé de main. Il n'est donc plus nécessaire de demander un changement de branche dans le tableau de bord. Les considérations de suppression/recréation ci-dessus concernaient cette ancienne stratégie ; elles ne s'appliquent pas à la simple mise à jour Git proposée ici. Streamlit peut néanmoins rafraîchir le processus et perdre les sessions en détectant de nouveaux fichiers ; aucune absence de redémarrage n'est promise.

La vérification des véritables références distantes révèle une divergence à préserver : feat/streamlit-interface pointe sur `ee35bf93ae997a52c9a5fd04692abe02fbdd0e77`, main sur `ebe5e5d04d3313bfe424784568fb5e0731a69869`. Le compteur est **1 commit propre / 9 commits de retard**, pas 0/9. La base commune est `0c68cfefc52cc99b7b31015e3c2a9055309d4501`. Le commit propre « Added Dev Container Folder » n'ajoute que `.devcontainer/devcontainer.json`. `merge-base --is-ancestor` confirme que le fast-forward vers main est impossible actuellement.

Aucune différence n'existe sur app.py, src/presentation.py, .streamlit/, requirements.txt et data/ entre les deux têtes. La simulation `git merge-tree --write-tree` réussit sans conflit et produit l'arbre `fad13d4fba85e8feeedca6449eae342e6e4fb189`, sans commit ni mutation de branche. Le Dev Container n'a pas été exécuté ; ses commandes Codespaces désactivant CORS/XSRF doivent être examinées avant une décision de conservation. Elles n'ont pas été appliquées à Community Cloud.

Une vraie intégration de l'ascendance de `ee35bf9` dans main, par merge revu sans squash/cherry-pick, rendrait ensuite le fast-forward possible si aucun nouveau commit divergent n'apparaît. Elle peut être examinée dans la PR de tâche 10 ou une PR séparée, sans toucher à la branche déployée. Une PR contenant uniquement les documents/tests de tâche 10 ne résoudrait pas cette divergence. Aucun merge réel n'est créé automatiquement dans cette préparation.

`deployment/check_sync.py` rend cette vérification reproductible et en lecture seule. `tests/test_deployment_finalization.py` ajoute trois tests : fast-forward synthétique possible, divergence synthétique malgré un design identique, et exécution des cinq parcours Mock sans réseau ni Groq. Les commits utilisés par les deux premiers tests sont uniquement des fixtures Git en répertoires temporaires, jamais des commits du dépôt CommercePilot. La suite atteint **146 tests réussis**, zéro échec/erreur/skip, avec **9/9 quality gates** ; l'évaluation reste 42/45, 28/28 directs et zéro violation détectée. Les artefacts de référence de tâche 8 et 7 sont préservés.

La documentation de recette est corrigée dans docs/deployment.md et le projet de description de PR est dans docs/deployment_pr.md. La publication n'a pas été effectuée ; les modifications restent sur feat/deployment-finalization, pour revue. Après approbation et intégration de l'ascendance, il faudra refaire le fetch, vérifier zéro commit propre et merge-base, puis effectuer seulement le push ordinaire du SHA cible vers la branche surveillée. Aucun force push n'est proposé. Le push et la synchronisation restent différés jusqu'à validation et fusion.

Le contrôle public consistera ensuite à prouver l'égalité des SHA distants et le chargement de ce commit, puis rejouer FAQ-002, suivi CLI-001/CMD-DEMO-001, ventes analyste de septembre 2026, refus sur CMD-DEMO-002 et clarification sans identifiant, avec Mock seul. Il est normal que le tableau de bord affiche encore feat/streamlit-interface. L'accès public depuis Codex était bloqué par le proxy et Chrome ; aucun nouveau succès public n'est revendiqué. La tâche reste en attente de synchronisation approuvée et de recette publique. Aucun commit, push, appel Groq, changement d'URL ou nouvelle application. Tâche 11 non commencée.


### Publication autorisée de tâche 10 : intégration réelle de l'historique

Après autorisation explicite de la propriétaire, les huit livrables locaux ont été préservés dans le commit `468c43004d4eb1be1495c4a96b124630110b9145`. Un vrai merge Git de origin/feat/streamlit-interface a ensuite été créé sur feat/deployment-finalization : `ba39cdb4ff58f2c491d65fcf0b22c9b12a6d868f`, avec deux parents, dont `ee35bf93ae997a52c9a5fd04692abe02fbdd0e77`. La preuve `merge-base --is-ancestor` confirme la présence du commit d'origine, et main est également ancêtre. Ce complément remplace les statuts de préparation sans commit des étapes historiques ci-dessus.

Conformément à l'autorisation, `.devcontainer/devcontainer.json` est retiré de l'arbre final après cette intégration : il n'est pas requis par Community Cloud et ses commandes Codespaces désactivaient CORS/XSRF. Il n'a pas été exécuté. Son commit reste dans l'histoire Git ; aucun rebase, squash ou force push n'est utilisé. app.py, le design, les dépendances de production, les données, l'agent et les Secrets Streamlit restent inchangés.

La PR doit être fusionnée **avec « Create a merge commit »**, sans squash ni rebase, pour conserver les parents et permettre le fast-forward ultérieur. La branche Streamlit ne sera synchronisée qu'après validation/fusion et un accord distinct. La publication de la branche de tâche 10 n'effectue ni cette synchronisation ni la recette publique. Les cinq parcours locaux et les gates restent vérifiés ; les résultats détaillés de cette dernière exécution figurent dans deployment/verification.json. Les parcours publics restent en attente d'un accès réseau fonctionnel et du chargement effectif du main approuvé. Tâche 11 non commencée.


## Sécurité, gouvernance et documentation des limites — tâche 11

### Périmètre et méthode

La branche `feat/security-governance` est issue de main fusionné (`d98d9499ef47585f8b4d38da9bb3b610d4cbb70d`). L'audit examine les trois outils, schémas, orchestrateur, présentation, sessions, observabilité, exclusions Git et workflow/artefacts CI, sans modifier leur fonctionnement. La propriétaire rapporte que la tâche 10 est déployée et que les cinq parcours publics Mock sont vérifiés. Ce constat est conservé comme déclaration de recette publique ; **SHA runtime et Python restent à confirmer dans les logs Streamlit**. Aucun nouveau contrôle public, accès aux Secrets distants ou appel Groq réel n'a été effectué pour cette tâche.

Les protections sont confrontées au code et à huit nouveaux tests ciblés ; elles ne sont pas déduites du seul score global. `security/audit.py` reproduit les contrôles de motifs de clés dans les fichiers courants/non ignorés et les blobs Git atteignables, des exclusions et du schéma des traces minimisées. Aucune valeur correspondante n'est affichée. Le rapport distingue explicitement les droits/configurations externes non inspectés.

### Protections vérifiées

La FAQ est autorisée aux trois rôles. Le suivi est limité aux commandes du client indiqué ou à l'administrateur synthétique ; l'analyste est refusé. Les ventes sont réservées aux analystes/administrateurs et restent agrégées. Les 30 identifiants clients ont été confrontés au suivi d'une même commande : seul son propriétaire réussit. Le refus est identique pour commande inconnue et commande d'autrui. Ce contrôle est correct dans le contexte fourni, mais ne rend pas le sélecteur UI authentifiant.

Le modèle ne peut choisir rôle ou customer_id ; les clés supplémentaires des arguments sont rejetées. Le lot est validé avant exécution ; un refus tardif masque les résultats accumulés. Les outils sont en lecture seule, les identifiants et périodes restent explicitement ancrés. Le rendu est déterministe et n'invente pas de réponse fournisseur en cas d'erreur. Les exceptions et contenus privés ne sont pas copiés dans la trace. Les bornes restent trois itérations/appels, 512 tokens, dix secondes par requête, 1500 caractères et quatre questions d'historique envoyées.

Une injection contenant une rupture Unicode échappe réellement au filtre lexical dans un nouveau test, mais la tentative d'obtenir sales_summary sous rôle client est bloquée par la permission déterministe. Ce constat documente une limite et la valeur de la défense en profondeur, sans faire croire que tous les prompts malveillants sont détectés. Les outils de mutation restent inexistants et les propositions de tels outils sont refusées.

### Secrets, traces et artefacts

Seul .env.example, avec valeurs vides, est versionné parmi les fichiers de configuration privée contrôlés. Les exclusions .env/variantes, Secrets Streamlit, clés et logs sont vérifiées. Un scan des fichiers courants et **110 blobs atteignables de l'historique local Git** n'a détecté aucun motif de clé ni valeur de secret connue de l'environnement. Ce résultat ne couvre pas les formats inconnus/encodés, messages de commit, objets distants non récupérés ou paramètres privés des plateformes. Une exclusion n'efface pas l'historique : toute clé réellement compromise doit être révoquée avant éventuel nettoyage Git approuvé.

Les sept traces synthétiques respectent les champs autorisés, sans identifiants directs ou texte brut ; la réponse est représentée par catégorie et content=not_retained. UUID et horodatages restent potentiellement corrélables : la minimisation n'est pas une preuve d'anonymat irréversible. Le fichier est créé en 0600, mais sans correction de permissions préexistantes, rotation ou TTL. Une panne de collecte n'interrompt pas l'agent, ce qui peut perdre des preuves sans alerte. Les fichiers locaux Cloud ne constituent pas un stockage durable garanti.

La CI utilise contents:read, aucun pull_request_target, aucune clé Groq transmise, des credentials non persistés et des actions épinglées par SHA. Ses artefacts proviennent d'une projection numérique testée, pas des logs bruts. Les métadonnées de l'artefact réel `13718015315` du run `42714484210` ont été consultées : rétention de trois jours, création le 9 novembre et expiration le 12 novembre 2026. Le téléchargement du ZIP via le réseau local a échoué ; **son contenu n'est pas présenté comme inspecté**. Les politiques réelles des comptes, MFA, protections de branche, secrets GitHub/Streamlit et rétention des logs de jobs restent à confirmer par la propriétaire.

### Risques et gouvernance

`security/risk_register.json` et `docs/security_risks.md` recensent 14 risques avec gravités qualitatives distinctes démo/production, impacts, protections, références, recommandations, priorités et décision à valider. Les plus bloquants avant production sont l'identité simulée, le contexte client falsifiable à la source et une éventuelle API publique sans authentification/quota/budget. L'accès aux CSV synthétiques publics est acceptable pour une démonstration uniquement selon décision de la propriétaire ; il ne constitue pas une isolation de données réelles.

Les risques résiduels couvrent injections non exhaustivement détectées, questions/historique transmis au fournisseur en mode réel, fuite de clé, logs sans rotation/alerte, historique UI sans plafond total/TTL, ressources Cloud limitées, transitives non verrouillées, métadonnées recoupables, preuves de runtime manquantes et faiblesse d'une gouvernance d'incident uniquement documentaire. Aucun changement d'activation Groq, d'identité, de design ou de règles métier n'est effectué.

`docs/governance.md` inventorie les flux et distingue les durées réelles des propositions : aucun TTL de session/log actuellement ; trois jours configurés pour les artefacts ; conservation des rapports académiques dans Git. La recommandation de sept jours pour des logs de diagnostic de démonstration n'est pas implémentée ni imposée légalement : elle reste à valider et à appliquer. Le runbook prévoit qualification, confinement par la propriétaire, révocation chez le fournisseur si nécessaire, préservation minimale, diagnostic hors ligne, PR revue et reprise vérifiée. Il n'envoie aucun message, ne change aucun secret et ne réalise aucune suppression à lui seul. Une notification éventuelle relève d'une analyse réelle de l'incident, sans garantie juridique annoncée.

### Validation et preuves

**154 tests réussis**, dont les 146 précédents et huit tests de sécurité supplémentaires ; zéro échec/erreur/skip, neuf quality gates réussis, validateur AtlasShop et diff Git propres. Les 45 scénarios et leurs résultats restent inchangés : 42/45, 28/28 directs, zéro violation détectée et trois échecs connus conservés. Les preuves sont dans `security/audit_results.json` et `security/quality_verification.json`. Les nouvelles vérifications de sessions montrent l'isolation entre deux sessions, mais aussi qu'une session peut librement choisir administrateur : cette dernière observation est un risque de conception pour la production, pas une authentification réussie.

Captures utiles : matrice des rôles, registre de risques avec gravités démo/production, synthèse des gates et contrôles de secrets sans valeurs, champs minimisés d'une trace synthétique et métadonnées de rétention CI. Ne pas capturer les secrets, prompts privés, réponses réelles ou URL temporaires de téléchargement. Aucune capture n'est fabriquée. Aucun code métier, donnée, corpus ou design n'est modifié ; aucun commit/push ou appel Groq réel ; tâche 12 non commencée. Le système reste une démonstration académique et non une solution certifiée ou prête pour des données de production.


## Évaluation de l'agent avec MLflow

### Objectif et protocole réutilisé

L'intégration complémentaire sur feat/mlflow-agent-evaluation part de main
9bcfb01273a3231f078cb82fc08608fd6e249d4c. MLflow **3.18.0**, Python **3.11.14** et
uv **0.13.5** sont réservés à un environnement d'évaluation, distinct de Streamlit
et de la CI standard. Les 107 versions de dépendances résolues sont contraintes
pour Linux/Python 3.11. Aucun fichier de l'agent, des trois outils, du design,
des données, de l'observabilité ou des références historiques n'est modifié.

Les tests empêchent les régressions ; MLflow ajoute l'historique consultable des
expériences, paramètres, métriques, assessments et artefacts. L'adaptateur réutilise
load_cases, evaluate_case, metrics et les oracles CSV d'offline-v1. Les 45 cas sont
réexécutés séquentiellement avec plans Mock et pannes simulées. La sortie doit
correspondre à la référence historique et à ses empreintes, sinon l'exécution s'arrête.
Dix scorers de code via **mlflow.genai.evaluate** vérifient statut, outils, erreurs,
sources, données structurées, fidélité factuelle, permissions et verdict global.
Les non-applicables ne deviennent pas des succès : **356 scores applicables**,
avec null dans les artefacts pour les autres critères. Les instantanés natifs ne
sont pas des spans internes de l'agent. Leur statut de trace MLflow OK signifie
que l’instantané est traité ; il faut lire outputs.status et scenario_passed
pour juger le résultat métier, notamment les refus et pannes simulés. Aucun juge LLM ni Groq réel n'est utilisé.

### Résultats observés et historique préservé

Les anciens runs Codex restent dans leur stockage initial :
95b9ec7abdfd49c39c0773e85aacf709 (FAILED, Expectation nulle MLflow refusée puis
corrigée sans changer les attentes), 4f4a607e7a174dc0966978b510da187c et
06d853aba4024bd3a8942dc6cc49290b (FINISHED, 45 cas/356 scores). Ils ne sont pas
supprimés ou importés comme de nouvelles mesures. Leurs bases et archives ne
sont pas ajoutées au dépôt public. L'impossibilité signalée par la propriétaire
de télécharger l'archive et de voir un panneau Desktop dans ChatGPT conduit à
retenir une nouvelle exécution autonome dans un Codespace privé.

La préparation Codespaces a été testée **dans un checkout neuf sous Codex** :
sans environnement virtuel ni stockage précédents, setup_mlflow.sh a installé
Python 3.11.14 et les paquets contraints. Les 45 scénarios ont produit le nouveau
run **e2cc0f1540a14bac9dd81fec68282090**, expérience locale **1**, FINISHED.
La relecture indépendante confirme **45 scénarios / 356 assessments**, métriques
natives et artefacts, sans import de scores anciens.

| Mesure | Numérateur / dénominateur | Valeur |
| --- | --- | --- |
| Scénarios / statuts conformes | 42/45 | 93,33 % |
| Outils exécutés conformes | 45/45 | 100 % |
| Données structurées conformes | 23/24 applicables | 95,83 % |
| Fidélité factuelle contrôlée | 23/24 | 95,83 % |
| Sources FAQ par occurrence | 12/13 | 92,31 % |
| Permissions, cas sensibles | 10/10 | 100 % |
| Violations détectées | 0 sur 45 cas | Aucune détectée |
| Contrôles directs des outils | 28/28 | 100 % |
| Clarifications obtenues | 9/45 | 20 % |
| Réponses de statut error | 6/45 | 13,33 % |

Ces rapports gardent les formules de tâche 7. Les numérateurs/dénominateurs sont
aussi des métriques protocol.*. Les moyennes natives sont par cas applicable :
rappel FAQ 11/12, différent de 12/13 par occurrences ; sources_exact 44/45 inclut
les cas sans source attendue. Les contrôles directs natifs sont regroupés par
scénario, ceux du protocole comptent chaque comparaison d'outil. Les violations
restent séparées des moyennes. Les erreurs attendues de panne sont des scénarios
réussis si correctement traitées ; error 6/45 ne mesure pas la production.

EV-010 reste en échec lexical FAQ sur paraphrase ; EV-016/022 restent des
incomplete_plan malgré des données correctes. Les attentes restent ok et les
scores faux restent visibles. Les plans imposés n'évaluent ni le routage spontané
ni la compréhension réelle de Groq. La fidélité est contrôlée par objets/fragments,
pas par un jugement sémantique exhaustif ou une preuve de qualité conversationnelle.

Durées de cette nouvelle mesure Mock : **0,111885 s** pour les 45 cas, moyenne
**2,473 ms**, P95 au rang le plus proche **5,831 ms** (rang 43/45). Chaque cas
inclut oracles, outils directs et l'agent ; le total comprend les projections.
L'intervalle de suivi/scoring natif mesuré est **5,225643 s**, overhead inclus,
hors initialisation du stockage et relecture finale. Ces mesures locales sont
variables ; elles ne représentent ni Groq ni les performances de production.
Chaque futur run du Codespace aura ses propres IDs, durées et paramètres.

### Confidentialité, publication et accès public/privé

La propriétaire autorise la publication du **code seulement** et une PR vers main,
sans fusion automatique. Le dépôt reste **PUBLIC** ; sa visibilité n'est pas modifiée.
Les exclusions Git et le code imposent work/mlflow/ pour les nouvelles sorties.
SQLite, traces, scores individuels, preuves de test, archives et environnements
restent privés/non versionnés. Les anciens chemins locaux evaluation/mlflow_*.json
sont ignorés. Les résultats historiques de tâche 7 et les neuf gates sont préservés.
Le workflow CI ne publie aucun artefact MLflow et n'installe pas cette dépendance.

Les paramètres enregistrent commit réel, versions, empreintes de code/entrées,
état du travail, mode Mock et versions offline-v1/mlflow-projection-v1 du protocole.
Un experiment MLflow n'a pas ici de version native analogue à un modèle : ce sont
des tags/paramètres explicites. Chaque run garde sa preuve privée sous
work/mlflow/runs/<id>/ ; latest_results.json indique le plus récent, sans supprimer
les précédents. La projection exportée exclut questions, réponses brutes, clients,
commandes, arguments, secrets et raisonnement privé. Réseau bloqué pendant les cas
et l'évaluation native, télémétrie désactivée, destination SQLite locale imposée.
Les scans sont ciblés, pas une garantie DLP exhaustive ou de sécurité absolue.

Le [guide Codespaces](mlflow_evaluation.md) donne les clics depuis la branche publiée
et quatre commandes : setup, nouveau calcul Mock, relecture, dashboard. Aucun
transfert d'archive Codex ni installation sur le PC n'est requis. Le serveur
écoute sur loopback ; le domaine exact du Codespace est autorisé sans wildcard,
CORS/middleware conservés. Le port **5000 doit rester Private** sous authentification
GitHub. La propriétaire ouvre GenAI → CommercePilot-Agent-Evaluation → Evaluation
runs, puis le run imprimé → Traces / Artifacts. Filtrer par run permet de voir
ses 45 cas plutôt que toutes les exécutions. known_failures.json présente les
trois échecs ; scenario_scores.json contient les valeurs réellement calculées.

Captures utiles : run et provenance, métriques protocol.*, 45 cas du run choisi,
un cas réussi, trois échecs avec false, et liste des artefacts. Les captures
proviennent du vrai MLflow ; aucune copie de tableau n'est présentée comme un dashboard.
La création effective d'un Codespace, la connexion et le port privé dans le compte
de la propriétaire **restent à confirmer par elle**. Le test reproductible local
ne prétend pas vérifier des permissions ou quotas GitHub distants.

### Validation et limites du Codespace gratuit

**170 tests réussis**, dont seize tests d'intégration contractuelle/confidentialité,
zéro échec/erreur/skip, **9/9 quality gates PASS**, Ruff, validateur AtlasShop et
diff propres. Couverture src lignes+branches **92,73 %**, sans prétendre mesurer
le code optionnel hors de src. Les scorers natifs et leur stockage sont vérifiés
avec MLflow réellement installé. Les preuves détaillées restent sous work/mlflow/.
Les protections des sorties incluent un refus des chemins hors de cet arbre et
d'une redirection par symlink vers des données publiques. Une exclusion Git ne
bloque pas git add -f : la sélection des fichiers publiés est donc aussi contrôlée.

Selon GitHub au 11 novembre 2026, Free personnel inclut **120 core-hours/mois et
15 GB-month**, partagés entre Codespaces : environ 60 heures à deux cœurs au
maximum si aucune autre consommation. Le quota restant et le budget réel du
compte ne sont pas inspectés. Le dépôt public ne rend pas le calcul illimité.
Choisir deux cœurs, aucun prebuild, aucun service payant ; arrêter si le quota
ne suffit pas et vérifier le blocage de dépenses si un paiement est configuré.

Arrêter le serveur puis le Codespace après consultation ; le stockage continue
à consommer l'allocation. Le même Codespace conserve ses fichiers sous /workspaces
à l'arrêt/redémarrage : relancer seulement le dashboard pour les revoir. Il peut
être supprimé après rétention, 30 jours d'inactivité par défaut ou moins selon
réglages. Les fichiers ignorés sont alors perdus. Conserver le Codespace dans son
quota jusqu'au rapport, sans prétendre offrir une sauvegarde durable ou une
relocalisation automatique des URI absolues MLflow. Les anciens runs Codex ne
sont pas accessibles par les nouveaux IDs et ne sont pas effacés.

Le pilote futur CommercePilot-Agent-Evaluation-Groq reste préparé mais désactivé,
sans exécuteur ni résultat inventé. Toute API réelle demandera une autorisation
distincte. Aucun changement du design, des données ou des règles de sécurité.
