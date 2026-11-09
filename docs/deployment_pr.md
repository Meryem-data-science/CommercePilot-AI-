# Proposition de PR — tâche 10 (non publiée)

Titre : `docs: prepare deployment finalization and public smoke checks`

## Objet

Conserver l'application Streamlit et son URL en synchronisant ultérieurement sa branche surveillée avec le main validé. Cette PR prépare uniquement documentation, preuves d'inspection Git et tests de recette. Aucun changement visuel, métier, de données ou activation Groq.

## Condition Git à résoudre avant synchronisation

Le contrôle distant constate 1 commit propre et 9 commits de retard, pas 0/9. Le commit `ee35bf9` ajoute `.devcontainer/devcontainer.json`. Le fast-forward actuel est impossible. Une simulation de merge dans main est sans conflit, mais le fichier doit être revu, notamment ses options Codespaces CORS/XSRF désactivées.

L'ascendance de ce commit doit être préservée dans main par un vrai merge approuvé (dans cette PR ou une PR séparée), sans squash/cherry-pick. Les seuls documents/tests de cette PR ne suffisent pas à résoudre la divergence. Aucun merge ou commit de cette intégration n'a été créé à cette étape. La branche déployée n'est pas modifiée.

## Recette et limites

`python -m deployment.check_local` exécute cinq parcours AppTest avec réseau/Groq interdits. `python -m deployment.check_sync` inspecte les références locales sans mutation. Les gates existants restent obligatoires. La publication puis la fusion de cette PR nécessitent la validation de la propriétaire. La synchronisation de la branche surveillée ne sera effectuée qu'ensuite, avec contrôles d'ascendance frais et sans force.

Les contrôles publics restent en attente : réseau Codex bloqué lors de la tentative précédente. Après égalité des SHA distants et confirmation du chargement du commit, vérifier FAQ, suivi, analytics, refus et clarification en Mock seul. Ne pas confondre réussite locale et validation publique. Aucun appel Groq réel. Tâche 11 non commencée.
