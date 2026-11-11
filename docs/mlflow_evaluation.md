# Évaluation de l'agent avec MLflow — GitHub Codespaces

## Accès depuis un navigateur, dépôt public conservé

Le dépôt **reste public**. Un Codespace personnel et son port transféré **Private**
restent protégés par la connexion GitHub de sa propriétaire ; la visibilité du
dépôt ne rend pas automatiquement le port public. Aucun téléchargement depuis
Codex, panneau Desktop, archive ancienne ou installation sur le PC n'est requis.

Seuls le code, les tests, les dépendances figées et cette documentation sont publiés.
SQLite, traces, scores individuels, preuves JSON, archives et environnements restent
sous **work/mlflow/** ou **work/mlflow-env/**, ignorés par Git. Les anciens fichiers
locaux evaluation/mlflow_results.json, mlflow_verification.json et
mlflow_quality_verification.json sont également exclus ; ils ne sont pas publiés.
Les résultats historiques de tâche 7 déjà versionnés ne sont ni réécrits ni supprimés.

## 1. Vérifier son allocation gratuite

Avant de créer le Codespace, consulter les paramètres GitHub **Billing and licensing**
et l'usage Codespaces du compte personnel. Selon la documentation consultée le
11 novembre 2026, GitHub Free inclut **120 core-hours et 15 GB-month par mois** :
120 core-hours représentent au plus environ **60 heures avec deux cœurs**, à
partager entre tous ses Codespaces. Un dépôt public ne donne pas un quota illimité.
Les comptes d'organisation n'ont pas le même quota personnel inclus.

Choisir **2-core**, sans prebuild ni machine plus grande. Ne pas activer d'usage
payant. Si un moyen de paiement est déjà configuré, vérifier le budget et l'option
**Stop usage when budget limit is reached** ; une alerte seule n'est pas un blocage.
Si le quota disponible ne suffit pas ou qu'une facturation est demandée, arrêter
et attendre son renouvellement. Les quotas, budgets et droits de la propriétaire
n'ont pas été inspectés ou modifiés par Codex.

## 2. Créer le Codespace sur la bonne branche

1. Ouvrir [feat/mlflow-agent-evaluation](https://github.com/Meryem-data-science/CommercePilot-AI-/tree/feat/mlflow-agent-evaluation).
2. Cliquer **Code → Codespaces → Create codespace on feat/mlflow-agent-evaluation**.
   Si nécessaire, utiliser **… → New with options**, sélectionner cette branche
   et la machine **2-core**. Ne pas choisir main tant que la PR n'est pas fusionnée.
3. Attendre l'éditeur web. Utiliser son terminal, depuis la racine du dépôt :

```bash
git branch --show-current
git rev-parse HEAD
bash evaluation/setup_mlflow.sh
```

La branche doit être feat/mlflow-agent-evaluation. Le script prépare **Python
3.11.14**, **MLflow 3.18.0** et les dépendances contraintes dans un environnement
séparé. Il utilise **uv 0.13.5** pour obtenir Python si nécessaire, depuis les
sources officielles. Tout s'installe dans le Codespace, sans sudo, sans clé Groq
et sans nouvelle application Streamlit. Ce script ne crée pas de run.

requirements-evaluation-constraints.txt fixe les 107 versions résolues pour
Linux/Python 3.11. Les dépendances de production et celles de CI restent inchangées.
L'installation nécessite Internet pour les paquets ; **l'évaluation elle-même
bloque les connexions réseau**. Les versions figées facilitent la reproduction,
sans promettre des durées identiques ou une installation hors ligne.

## 3. Calculer un nouveau run Mock

```bash
work/mlflow-env/bin/python -m evaluation.mlflow_evaluation
work/mlflow-env/bin/python -m evaluation.mlflow_verify
```

La première commande réexécute réellement les **45 scénarios** existants, puis
utilise **mlflow.genai.evaluate()** avec dix scorers déterministes. Elle n'importe
aucun score depuis un ancien run. Chaque exécution reçoit un **nouvel ID**.
Les outils, permissions, résultats et empreintes doivent rester conformes à la
référence historique ; une divergence interrompt le protocole sans changer les attentes.

La seconde commande **ne réexécute pas l'agent** : elle relit le run, les métriques,
les assessments de chaque scénario et les artefacts réellement persistés. Elle
contrôle également l'absence de motifs de secrets connus et de questions/identifiants
bruts du corpus dans le stockage. Ce scan limité n'est pas une garantie DLP exhaustive.

Les sorties attendues d'après la référence, à confronter à la nouvelle exécution :

| Contrôle | Référence historique |
| --- | --- |
| Scénarios et statuts conformes | 42/45 |
| Outils exécutés conformes | 45/45 |
| Données structurées conformes | 23/24 applicables |
| Fidélité factuelle contrôlée | 23/24 |
| Sources FAQ par occurrence | 12/13 |
| Permissions sur cas sensibles | 10/10 |
| Violations détectées, tous cas | 0 |
| Contrôles directs des outils | 28/28 |
| Clarifications obtenues | 9/45 |
| Réponses de statut error | 6/45 |
| Assessments applicables persistés | 356 sur 45 scénarios |

Les valeurs réellement mesurées et durées seront dans le run créé, pas dans une
copie de ce tableau. **FINISHED** signifie fin du suivi MLflow, pas 45 réussites.
Les faux scores EV-010/016/022 restent visibles. Les pannes attendues correctement
traitées sont des scénarios réussis. Le taux error du corpus ne mesure pas la production.

## 4. Ouvrir le serveur MLflow privé

```bash
work/mlflow-env/bin/python -m evaluation.mlflow_dashboard
```

Garder ce terminal ouvert. Le script affiche le lien exact du dernier run, avec
les nouveaux IDs d'expérience/run, puis sert la véritable interface MLflow.

1. Dans le panneau inférieur de l'éditeur, cliquer **PORTS**, à côté de TERMINAL.
   Si l'onglet est masqué, utiliser le menu des autres onglets du panneau.
2. Si 5000 n'apparaît pas, cliquer **Add Port / Forward a Port**, saisir **5000**.
3. Clic droit sur la ligne **5000 → Port Visibility → Private**. Vérifier l'indication.
4. Cliquer l'icône **Open in Browser** (globe), ou ouvrir le lien affiché par le script.
5. Garder le protocole du serveur local sur HTTP : GitHub fournit l'URL externe
   **HTTPS** authentifiée. Ne pas choisir Public et ne pas désactiver les protections.

Le serveur écoute uniquement sur 127.0.0.1:5000 ; seuls les hôtes localhost et le
nom exact du Codespace sont autorisés. CORS et le middleware de sécurité restent
actifs, sans wildcard. MLflow n'ajoute pas ici une authentification applicative :
la protection d'accès externe dépend du port **Private** et de GitHub. Le compte
GitHub est nécessaire même si le code est public. Ne pas utiliser l'Assistant
MLflow ou configurer un juge LLM ; ils ne sont pas nécessaires à cette évaluation.

## 5. Voir les métriques, les 45 cas et les trois échecs

1. Sélectionner **GenAI → CommercePilot-Agent-Evaluation → Evaluation runs**.
2. Ouvrir le run **Mock-offline-v1** dont l'ID vient d'être imprimé. Ses paramètres
   contiennent le commit réel, Python, MLflow, le mode Mock et les versions du protocole.
3. **Overview / Model metrics** : consulter scenario_count, les métriques
   **protocol.*** avec leurs numérateurs et dénominateurs, les moyennes natives,
   les catégories, les durées mesurées et permission_violation_count.
4. Dans l'onglet **Traces de ce run**, consulter les **45 lignes** (pagination si
   nécessaire). Chaque entrée contient inputs.scenario_id et ses assessments.
   Le mode de comptage est **356 scores applicables**, pas 450 réussites forcées.
   Le statut de trace MLflow OK décrit son traitement ; lire **outputs.status**
   et **scenario_passed** pour juger l’agent, même en cas de refus/panne simulée.
5. **Artifacts → known_failures.json** : retrouver **EV-010**, **EV-016**, **EV-022**.
   Dans Traces, leurs valeurs scenario_passed/status_correct sont false ; les détails
   figurent aussi dans **scenario_scores.json**, où null signifie non applicable.
6. Les liens/IDs individuels sont dans le fichier privé
   **work/mlflow/latest_results.json**, champ trace_ids. Capturer les vrais écrans
   des métriques, d'un cas réussi et des trois échecs pour le rapport.

Ne pas consulter seulement le total de l'expérience si plusieurs runs existent :
le filtre par run évite de confondre 45 nouveaux cas avec plusieurs séries de 45.
Une moyenne native par cas peut différer du protocole : rappel FAQ natif 11/12,
contre 12/13 pondéré par occurrences ; sources_exact 44/45 inclut les cas sans
source attendue. Le contrôle direct natif agrège par scénario, alors que les
28/28 contrôles directs du protocole comptent chaque comparaison d'outil.
Les violations de permission sont toujours affichées séparément d'une moyenne.

## 6. Conserver et reprendre sans publier les résultats

Les fichiers privés du Codespace sont organisés ainsi :

- work/mlflow/store/mlflow.db : base native, tous les runs locaux ;
- work/mlflow/store/artifacts/ : artefacts MLflow ;
- work/mlflow/runs/<run_id>/results.json et verification.json : preuves par run ;
- work/mlflow/latest_results.json et latest_verification.json : dernière exécution ;
- work/mlflow-env/ : dépendances séparées.

Les nouvelles preuves ne remplacent pas les anciennes preuves par run. Les trois
runs initiaux créés dans Codex restent dans leur stockage initial : ils ne sont
ni transférés, ni supprimés, ni présentés comme des runs du nouveau Codespace.
Les anciens JSON à la racine evaluation sont ignorés pour éviter une publication.
Le dépôt et les 45 annotations historiques restent inchangés.

Pour vérifier que les sorties ne sont pas proposées au commit :

```bash
git check-ignore work/mlflow/store/mlflow.db work/mlflow/latest_results.json
git status --short
```

**Ne jamais utiliser git add -f sur ces sorties, joindre une trace/base/archive à
une PR ou publier le port.** Les règles d'exclusion n'empêchent pas une publication
volontaire forcée ; aucune base ni trace MLflow n'est incluse dans cette PR.
Les artefacts CI existants restent limités aux rapports techniques historiques
minimisés ; aucun upload MLflow n'est ajouté au workflow GitHub Actions.

Après consultation, arrêter le serveur avec **Ctrl+C**, puis **Stop Codespace**
via le menu distant ou github.com/codespaces. Fermer l'onglet seul ne garantit
pas l'arrêt immédiat. La prochaine fois, rouvrir **le même Codespace** et lancer
uniquement le dashboard, sans les deux commandes d'évaluation/vérification.
Le stockage sous /workspaces persiste à l'arrêt/redémarrage du même Codespace ;
le serveur doit être relancé. Le calcul s'arrête, mais le stockage continue à
consommer l'allocation. Vérifier la rétention : par défaut, GitHub supprime les
Codespaces inactifs après **30 jours**, éventuellement plus tôt selon les réglages.
Les fichiers ignorés non poussés sont perdus à la suppression. Le Codespace n'est
pas une sauvegarde durable garantie ; le conserver dans son quota jusqu'au rapport.
Une archive privée réalisée après arrêt est possible, mais n'est pas requise par
la procédure. Les URI MLflow sont absolues : leur déplacement entre machines
peut empêcher la lecture des artefacts. Aucune restauration d'archive ni migration
SQL n'est nécessaire pour les nouveaux runs calculés sur place.

## Protocole, confidentialité et limites

Le code réutilise load_cases, evaluate_case et metrics d'offline-v1, avec oracles
CSV indépendants et calculs Decimal. Les cas sont séquentiels à cause des outils
remplacés temporairement. Les dix scorers couvrent statut, outils, type d'erreur,
sources exactes, rappel FAQ, données structurées, fidélité, permissions, contrôles
directs et verdict global. Aucun juge LLM ou nouvel outil métier n'est ajouté.
Les instantanés natifs contiennent uniquement les résultats minimisés, pas des
spans internes, questions, réponses brutes, identités, arguments ou raisonnements.
Le réseau est bloqué pendant les cas et l'évaluation native ; télémétrie désactivée.

L'expérience s'appelle CommercePilot-Agent-Evaluation ; les tags/paramètres
protocol_version=offline-v1 et integration_version=mlflow-projection-v1 versionnent
le protocole. MLflow ne donne pas ici de version native à un experiment comme à
un modèle. Le mode Mock ne mesure **ni le routage spontané ni la compréhension de
Groq**, et les contrôles de fidélité restent des objets/fragments, pas une analyse
sémantique exhaustive. Les latences Mock ne sont pas celles d'un fournisseur réel.
EV-010 est un échec de recherche FAQ lexicale ; EV-016/022 sont des incomplete_plan
sur paraphrases malgré des données correctes. Leurs attentes restent ok.

Le manifeste groq_evaluation_plan.json est préparé mais **désactivé**, sans exécuteur
réel. Une future évaluation Groq exige une autorisation distincte. Cette procédure
n'appelle pas Groq, ne configure pas ses secrets et ne modifie pas Streamlit.

## Vérifications effectivement réalisées

Les trois runs historiques de Codex sont conservés :

| Run | État historique | Observation |
| --- | --- | --- |
| 95b9ec7abdfd49c39c0773e85aacf709 | FAILED | Expectation nulle MLflow refusée, corrigée sans changer les attentes métier. |
| 4f4a607e7a174dc0966978b510da187c | FINISHED | Première série complète, 45 cas / 356 scores relus. |
| 06d853aba4024bd3a8942dc6cc49290b | FINISHED | Run de référence précédent, mêmes résultats. |

La procédure d'installation et de calcul est vérifiée dans un checkout neuf sous
Codex, avec Python 3.11.14 et le stockage MLflow vide, sans import de scores anciens.
Les détails de la nouvelle mesure et du contrôle qualité sont consignés dans la
section MLflow du rapport progressif ; les preuves détaillées restent privées
sous work/mlflow. Une création de Codespace, ses quotas, l'authentification GitHub
et le transfert privé du port ne sont **pas présentés comme testés à distance**.
Ils doivent être confirmés par la propriétaire dans son compte. Le protocole local
reproduit les commandes et dépendances, sans prétendre reproduire ces réglages GitHub.

## Sources officielles consultées

Documentation consultée le 11 novembre 2026, confrontée au SDK installé 3.18.0.

- [MLflow 3.18.0](https://www.mlflow.org/releases/3.18.0/).
- [API GenAI evaluate](https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html#mlflow.genai.evaluate).
- [Scorers de code](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/custom/).
- [Protection réseau MLflow](https://mlflow.org/docs/latest/self-hosting/security/network/).
- [Ports Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace).
- [Quotas inclus](https://docs.github.com/en/billing/reference/product-usage-included).
- [Consommation et limites gratuites](https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage).
- [Arrêt et reprise](https://docs.github.com/en/codespaces/developing-in-a-codespace/stopping-and-starting-a-codespace).
- [Rétention et suppression](https://docs.github.com/en/codespaces/setting-your-user-preferences/configuring-automatic-deletion-of-your-codespaces).
