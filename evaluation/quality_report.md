# Rapport qualité — tâche 8

Contrôles locaux, aucun appel Groq réel.

| Quality gate | Verdict |
| --- | --- |
| tests_offline | RÉUSSI |
| atlasshop | RÉUSSI |
| ruff | RÉUSSI |
| coverage_measured | RÉUSSI |
| evaluation_thresholds | RÉUSSI |
| evaluation_reproducible | RÉUSSI |
| reference_results_consistent | RÉUSSI |
| secret_scan | RÉUSSI |
| git_diff_check | RÉUSSI |

## Tests et couverture

{"run": 139, "failures": 0, "errors": 0, "skipped": 0, "expected_failures": 0, "unexpected_successes": 0, "successful": true}

Couverture de `src/`, mesurée avec branches (hors app.py, scripts, tests et dépendances) :

```json
{
  "covered_lines": 588,
  "num_statements": 628,
  "percent_covered": 92.72517321016166,
  "percent_covered_display": "93",
  "missing_lines": 40,
  "excluded_lines": 0,
  "num_branches": 238,
  "num_partial_branches": 21,
  "covered_branches": 215,
  "missing_branches": 23
}
```

| Module | Couverture lignes + branches (%) |
| --- | --- |
| src/agent.py | 95.19 |
| src/llm_client.py | 96.43 |
| src/observability.py | 88.04 |
| src/presentation.py | 93.94 |
| src/schemas.py | 91.49 |
| src/tools/analytics.py | 100.00 |
| src/tools/common.py | 77.53 |
| src/tools/faq.py | 95.24 |
| src/tools/orders.py | 100.00 |

## Référence d'évaluation

Seuils fixés dans `quality/baseline.json` avant exécution : 45 scénarios, au moins 42 réussis,
28/28 contrôles directs, zéro violation. Chaque scénario précédemment réussi doit le rester.
L'empreinte du jeu interdit une modification silencieuse des annotations. Les résultats versionnés
et leurs métriques doivent correspondre à la nouvelle exécution, sans être réécrits par le gate.
EV-010 (recherche FAQ lexicale), EV-016 et EV-022 (complétude de paraphrases) restent les trois
échecs connus documentés. Les pannes attendues et correctement gérées sont des scénarios réussis.
Aucun score ne mesure le choix spontané de Groq ni le taux de panne en production.

## Anomalies et corrections

Ruff a initialement détecté six imports inutilisés dans quatre fichiers de tests.
Seuls ces imports ont été retirés ; aucun code métier n'a été corrigé ou reformaté.
Un premier essai des nouveaux tests a échoué sur une assertion du test de gate : une
violation hors du sous-ensemble sensible ne change pas nécessairement son agrégat,
mais doit toujours être bloquée globalement. L'assertion a été corrigée pour tester
ce cas précis ; aucun seuil ni comportement métier n'a été modifié.
Le style historique à points-virgules n'est pas soumis à un reformatage global.
Les limites fonctionnelles connues du benchmark ne sont pas corrigées dans cette tâche.

## Outils, reproductibilité et limites

Ruff 0.14.4 et coverage.py 7.11.3 sont fixés dans requirements-dev.txt. Les règles de lint et
sécurité ciblées figurent dans pyproject.toml ; ce n'est pas un audit de sécurité complet.
Les tests et l'évaluation bloquent les connexions socket ; les réponses SDK utilisent des transports
HTTP simulés. Les preuves détaillées sont dans work/quality/ (ignoré par Git), dont la couverture
par module et les sorties des commandes. Les résultats agrégés sont dans quality_results.json.
Le scanner examine les fichiers versionnés et non ignorés, sans imprimer les valeurs suspectes.
Il détecte des formats de clés, des fichiers sensibles et les secrets présents dans l'environnement,
mais ne garantit pas la détection de toute information confidentielle, clé encodée ou secret absent
de l'environnement. Les fichiers ignorés non publiés ne sont pas couverts.
La couverture est une mesure, sans seuil arbitraire ajouté après son calcul ; elle ne prouve pas
la qualité des assertions ni une sécurité exhaustive. Les erreurs de fournisseur et de journalisation
sont simulées, pas représentatives des incidents de production. Aucun CI distant, service payant,
Docker, GitHub Actions, commit ou push n'est ajouté. Tâche 9 non commencée.

Reproduction : `.venv/bin/python -m quality.check` après installation de requirements.txt et
requirements-dev.txt. Le code de sortie vaut 1 si un gate échoue, 0 sinon. Les preuves sont régénérées,
les artefacts de tâche 7 restent inchangés.
