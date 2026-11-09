# Description de PR — tâche 10

## Fusion : Create a merge commit obligatoire

**Utiliser « Create a merge commit », jamais « Squash and merge » ni « Rebase and merge ».** Le but est de préserver l'ascendance de `ee35bf9`, puis de rendre possible une synchronisation fast-forward ultérieure de la branche Streamlit. Ne pas fusionner automatiquement.

## Changements

- Livrables locaux préservés par `468c430` : documentation, vérifications et tests de recette.
- Vrai merge `ba39cdb4ff58f2c491d65fcf0b22c9b12a6d868f`, dont le second parent est `ee35bf93ae997a52c9a5fd04692abe02fbdd0e77`.
- Retrait de `.devcontainer/devcontainer.json` de l'arbre final après intégration de son historique. Ses commandes désactivant CORS/XSRF ne sont pas nécessaires à Community Cloud et n'ont jamais été exécutées.
- Procédure de synchronisation différée et de cinq parcours publics Mock, sans modification de app.py, du design, des données ou des Secrets.

## Vérifications

La preuve d'ascendance repose sur `git merge-base --is-ancestor ee35bf93ae997a52c9a5fd04692abe02fbdd0e77 HEAD`. `origin/main` doit également être ancêtre de la branche préparée. Les 146 tests et neuf gates doivent rester réussis, avec 42/45 scénarios et 28/28 contrôles directs, zéro violation. La branche déployée reste sur son SHA d'origine et n'est pas mise à jour par cette PR.

## Après revue et fusion uniquement

Refaire un fetch et le contrôle d'ascendance ; après accord de synchronisation distinct, pousser le SHA exact du main approuvé vers feat/streamlit-interface sans force. Garder la même instance, le même nom de branche surveillée et la même URL. Vérifier le commit servi puis FAQ, suivi, analytics, refus et clarification en Mock seul.

La recette publique reste en attente : l'accès depuis Codex était bloqué par le réseau. Aucun succès public actuel n'est revendiqué. Aucun appel Groq réel, aucun changement des réglages Streamlit. Tâche 11 non commencée.
