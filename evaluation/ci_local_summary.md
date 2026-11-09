# Validation locale du workflow proposé

**Aucune exécution GitHub Actions n’a encore été réalisée.**

# CommercePilot · PASS

Résultats de cette exécution uniquement. Tests hors ligne ; aucun appel réel Groq.

| Quality gate | Verdict |
| --- | --- |
| tests_offline | PASS |
| atlasshop | PASS |
| ruff | PASS |
| coverage_measured | PASS |
| evaluation_thresholds | PASS |
| evaluation_reproducible | PASS |
| reference_results_consistent | PASS |
| secret_scan | PASS |
| git_diff_check | PASS |

Tests : 143 exécutés ; 0 échecs ; 0 erreurs ; 0 ignorés.
- Lignes : 93.63 %.
- Branches : 90.34 %.
- Couverture combinée de src/ : 92.73 %.
- scenario_successes : 42/45.
- direct_checks : 28/28.
- permission_violation_count : 0.

Référence : 45 scénarios, au moins 42 réussis, 28/28 contrôles directs, zéro violation.
Les limites connues EV-010, EV-016 et EV-022 restent documentées dans evaluation/agent_report.md.
Un FAIL ou une donnée indisponible impose une revue du step concerné. Reproduire avec python -m quality.check ;
les diagnostics détaillés restent dans work/quality/ en local et ne sont pas téléversés.
Les artefacts ne contiennent ni questions, ni réponses métier, ni traces individuelles, ni erreurs brutes.
