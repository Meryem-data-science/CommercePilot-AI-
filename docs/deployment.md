# Finalisation Streamlit Community Cloud — tâche 10

**Statut : préparation locale ; synchronisation différée et vérification publique encore requises.**

Application existante : https://commercepilot-ai.streamlit.app/ . L'existence du déploiement et la validation publique antérieure des cinq parcours Mock sont rapportées par la propriétaire. Aucune nouvelle application ne doit être créée, aucune URL changée et aucune application supprimée dans cette tâche.

## Configuration attendue

| Élément | Valeur |
| --- | --- |
| Dépôt | Meryem-data-science/CommercePilot-AI- |
| Branche de référence du code | main |
| Branche conservée par l’application | feat/streamlit-interface |
| Point d'entrée | app.py |
| Python | 3.11 ; version locale/CI 3.11.14 |
| Dépendances | requirements.txt à la racine |
| Thème | .streamlit/config.toml existant, inchangé |
| Mode public | Mock uniquement |
| Secrets Groq publics | Aucun |

Les fichiers nécessaires sont présents sur le commit `ebe5e5d04d3313bfe424784568fb5e0731a69869` de `origin/main` vérifié au début de la tâche : app.py, src/, configs/agent.yaml, dépendances, configuration Streamlit et données AtlasShop. Aucun binaire système supplémentaire ni service externe n'est nécessaire au mode Mock. La compatibilité est vérifiée dans l'environnement Python 3.11.14 local ; elle ne remplace pas le contrôle du runtime effectivement provisionné par Community Cloud. Les dépendances directes sont fixées (Streamlit 1.51.0, Groq 1.7.0), les transitives ne sont pas entièrement verrouillées.

## Synchronisation Git différée : pas de changement des coordonnées Streamlit

La solution retenue conserve la branche surveillée `feat/streamlit-interface` et l'URL existante. Elle consiste à avancer cette branche jusqu'au commit validé de `main`, après revue/fusion de la PR de tâche 10. Il ne s'agit ni de modifier le tableau de bord ni de créer une nouvelle application. Streamlit peut rafraîchir ou redémarrer le processus en détectant le nouveau commit ; on ne peut pas garantir la conservation des sessions, même si l'instance et l'URL restent les mêmes.

### État initial observé avant intégration (preuve historique)

- `origin/feat/streamlit-interface` : `ee35bf93ae997a52c9a5fd04692abe02fbdd0e77`.
- `origin/main` : `ebe5e5d04d3313bfe424784568fb5e0731a69869`.
- `git rev-list --left-right --count deployed...main` : **1 / 9**, pas 0 / 9.
- Base commune : `0c68cfefc52cc99b7b31015e3c2a9055309d4501`.
- Commit propre : `ee35bf9`, « Added Dev Container Folder », qui ajoute seulement `.devcontainer/devcontainer.json`.
- `merge-base --is-ancestor deployed main` échoue : **fast-forward strict actuellement impossible**.
- `git merge-tree --write-tree origin/main origin/feat/streamlit-interface` réussit sans conflit, arbre simulé `fad13d4fba85e8feeedca6449eae342e6e4fb189`. Aucun commit de merge, aucune référence locale de travail ni branche distante n'ont été modifiés par cette simulation.
- Aucune différence sur app.py, src/presentation.py, .streamlit/, requirements.txt ou data/ : design, dépendances de production et données sont identiques.

Le fichier Dev Container n’a jamais été exécuté. Après autorisation explicite, son historique a été intégré puis le fichier a été retiré de l’arbre final, car il n’est pas nécessaire à Community Cloud et ses options Codespaces désactivaient CORS/XSRF. Les réglages et le code de l’application déployée n’ont pas été modifiés.

### Intégration autorisée réalisée dans la branche de PR

Les modifications locales de tâche 10 ont d'abord été préservées par le commit `468c430`. Un **vrai merge Git** a ensuite été créé : `ba39cdb4ff58f2c491d65fcf0b22c9b12a6d868f`, avec deux parents `468c43004d4eb1be1495c4a96b124630110b9145` et `ee35bf93ae997a52c9a5fd04692abe02fbdd0e77`. Le commit d'origine est donc conservé dans l'ascendance. Le fichier `.devcontainer/devcontainer.json` a ensuite été supprimé de l'arbre de travail et cette suppression fait partie de la publication finale autorisée. Aucune instruction du fichier n'a été exécutée.

La branche de PR contient les changements de main et ceux de la tâche 10. La commande `git merge-base --is-ancestor ee35bf93ae997a52c9a5fd04692abe02fbdd0e77 HEAD` réussit. La branche distante déployée reste inchangée à `ee35bf9`.

### Fusion de PR et synchronisation ultérieure

1. Examiner la PR de `feat/deployment-finalization` vers `main`, y compris la conservation d'historique et le retrait du fichier Dev Container.
2. **Utiliser impérativement « Create a merge commit ». Ne pas utiliser « Squash and merge » ni « Rebase and merge ».** Sinon, la présence des fichiers ne suffit pas à préserver l'ascendance de `ee35bf9` dans main et le fast-forward futur pourrait rester impossible.
3. Aucune fusion automatique n'est autorisée. Après validation et fusion manuelle, refaire le fetch et contrôler l'ascendance sur les références distantes fraîches. Il doit y avoir zéro commit propre sur la branche déployée ; si elle a avancé entre-temps, arrêter et réexaminer la divergence.
4. Après un accord distinct de synchronisation, pousser le SHA exact de main vers `feat/streamlit-interface` sans force, puis vérifier l'égalité des SHA distants. **Cette synchronisation n'est pas effectuée par la publication de la PR.**
5. Attendre que l'application existante charge le nouveau commit, sans changement d'URL ni de coordonnées, puis exécuter les cinq parcours publics ci-dessous. Ne pas confondre ascendance Git correcte, succès de CI et recette du site public.

Commandes prévues pour l'étape future, **non exécutées maintenant** :

```bash
git fetch origin refs/heads/main:refs/remotes/origin/main refs/heads/feat/streamlit-interface:refs/remotes/origin/feat/streamlit-interface
deployed_sha=$(git rev-parse origin/feat/streamlit-interface)
target_sha=$(git rev-parse origin/main)
git rev-list --left-right --count "$deployed_sha...$target_sha"
git merge-base --is-ancestor "$deployed_sha" "$target_sha"
# Arrêter immédiatement si la commande précédente échoue.
git push --dry-run origin "$target_sha:refs/heads/feat/streamlit-interface"
# Après accord explicite seulement, et si tous les contrôles restent bons :
git push origin "$target_sha:refs/heads/feat/streamlit-interface"
git ls-remote origin refs/heads/feat/streamlit-interface refs/heads/main
```

Les deux SHA distants devront être identiques. Le push ordinaire protège contre une mise à jour concurrente divergente ; aucun `--force` ou `--force-with-lease` n'est utilisé. Le script `python -m deployment.check_sync` lit les références locales après fetch et n'effectue jamais de push, merge ou changement de branche.

## Réglages de l'application existante à contrôler, pas à recréer

Dans share.streamlit.io, sélectionner le workspace Meryem-data-science et l'application existante. Dans `Settings` → `General`, vérifier l'URL sans la changer. Dans `Secrets`, ne configurer aucune variable Groq sur le site public ; toute suppression éventuelle est effectuée personnellement par la propriétaire sans partager la clé. Le code actuel rend Groq sélectionnable si les deux variables existent, donc un simple choix Mock dans une session n'est pas une protection publique.

Dans `Manage app`, relever la branche source, le commit si disponible et le Python du runtime, sans diffuser de lignes confidentielles. Après synchronisation, il est **normal que la branche reste feat/streamlit-interface** : c'est son commit qui doit correspondre au main approuvé. Python 3.11 est la configuration initiale communiquée ; confirmer qu'elle reste inchangée. Aucun changement d'URL, de version Python ou de coordonnées GitHub n'est nécessaire. La procédure de suppression/recréation documentée par Streamlit ne s'applique pas à une simple mise à jour de contenu sur la même branche.

## Recette de disponibilité et de démarrage

- Ouvrir l'URL existante dans une session privée, sans connexion administrateur, et attendre le réveil éventuel.
- Vérifier l'absence de traceback, de boucle de chargement et d'erreur de dépendances ; confirmer la présence du hero, de la sidebar et de la saisie.
- Confirmer que le mode public proposé est uniquement **Mock**, sans cliquer sur Groq s'il apparaît. S'il apparaît, arrêter la recette et revoir les secrets du serveur avant toute question.
- Le contrôle technique `/_stcore/health` peut compléter l'observation, mais un HTTP 200 ou une page HTML ne prouve ni le bon chargement du chat, ni le commit réellement servi.
- Vérifier le SHA déployé et Python par le tableau de bord/logs ; conserver une preuve sans secret avant d’annoncer que le code approuvé de main est effectivement en ligne, même si le nom de branche reste feat/streamlit-interface.

## Les cinq parcours publics à confirmer

Commencer chaque parcours par « Nouvelle conversation ». Le changement de profil efface également les messages précédents.

| Cas | Profil | Question | Résultat attendu |
| --- | --- | --- | --- |
| FAQ | client CLI-001 | Quels sont les délais de livraison ? | Réponse documentaire, FAQ-002, cinq jours calendaires, sans garantie |
| Suivi autorisé | client CLI-001 | Où est ma commande CMD-DEMO-001 ? | Livrée, livraison du 22 juillet 2026, données de démonstration au 1er octobre 2026 |
| Analytics | analyste, sans client | Résume les ventes de septembre 2026. | 87 commandes ; 109 544,30 MAD commandés ; 66 261,30 MAD payés ; 29 157,20 MAD réalisés ; aucun détail individuel |
| Refus | client CLI-001 | Où est ma commande CMD-DEMO-002 ? | Refus neutre, aucune carte de données protégées |
| Clarification | client CLI-001 | Où est ma commande ? | Demande du numéro, aucun identifiant inventé |

Conserver une preuve d’égalité des SHA distants, puis vérifier dans les logs le chargement de ce commit. Attendre la fin du rafraîchissement avant la recette ; si le site ne sert pas le nouveau commit, ne pas annoncer de succès.

Vérifier aussi le rechargement de page et une nouvelle session : aucune conversation d'un autre utilisateur ne doit être affichée. Le rechargement peut perdre l'état, ce qui est acceptable pour cette démonstration. Conserver les captures réelles et la date du contrôle ; les observations antérieures sur l'ancienne branche ne valent pas validation de `main`.

## Contrôles locaux reproductibles

```bash
.venv/bin/python -m deployment.check_local
.venv/bin/python -m quality.check
.venv/bin/python -m pip check
```

`deployment.check_local` exécute les cinq parcours sous AppTest avec variables Groq vides, socket réseau bloquée et adaptateur Groq interdit. Le résultat machine est dans `work/deployment/local_smoke.json`. Le serveur local a également été démarré en mode Mock avec `streamlit run app.py` et le contrôle de santé a répondu `ok`. Les gates ont donné 143 tests réussis et neuf PASS, sans changement des 42/45 scénarios ni des trois échecs connus. `deployment/verification.json` distingue ces résultats des contrôles publics non effectués.

## Limites de Community Cloud

- Mise en veille/réveil possible, démarrages à froid et redémarrages lors de modifications des dépendances ; la disponibilité n'est pas une garantie de service de production.
- Mémoire/CPU partagés et limités, capacité dépendante de la plateforme : ne pas extrapoler les latences locales aux visiteurs. Un dépassement de ressources peut provoquer un arrêt ou un redémarrage.
- Les changements de requirements.txt peuvent déclencher une réinstallation ; les transitives évoluent. Les outils de développement ne sont pas requis au lancement de l'application.
- `st.session_state` dépend de la session et du processus. Les fichiers locaux, dont `logs/agent_events.jsonl`, ne sont pas un stockage durable garanti après remplacement de l'environnement. Les journaux opérationnels ne doivent pas être exportés publiquement ni considérés comme une archive persistante.
- Les CSV et rapports versionnés sont restaurés depuis Git ; l'application ne les modifie pas. Aucune base de données persistante ni sauvegarde distante payante n'est ajoutée.
- Les profils sont simulés et sélectionnables ; ils ne constituent pas une authentification. La démonstration publique reste sur données fictives et sans API facturable.
- Le thème et le comportement visuel sont conservés. La plateforme peut imposer certaines options (notamment sécurité du serveur et télémétrie) indépendamment du config.toml local : voir les [limites officielles](https://docs.streamlit.io/deploy/streamlit-community-cloud/status).

## Résultat actuel : tâche non clôturée

L'URL a été fournie, mais la connexion terminal est rejetée par le proxy (CONNECT HTTP 403) et Chrome partagé termine par `DNS_PROBE_FINISHED_NO_INTERNET`. Aucun des cinq parcours publics n'a donc été rejoué par l'assistant et aucune bascule n'est revendiquée. Ce sont des blocages de l'environnement de vérification, pas une preuve que le site est en panne. La propriétaire a confirmé la configuration initiale : branche feat/streamlit-interface, app.py, Python 3.11, même URL. Cette déclaration ne confirme pas une bascule ultérieure vers main ni une lecture actuelle des logs ; ces preuves restent attendues.

Critères de clôture : instance et URL conservées, commit de la branche déployée identique au main approuvé, Python 3.11, Mock seul, disponibilité et cinq parcours publics effectivement vérifiés. Le fast-forward vers le main actuel reste impossible avant la fusion de la PR ; l’ascendance requise est désormais préparée dans la branche de PR. Des commits et la publication de cette seule branche sont autorisés. Aucun push de la branche déployée, redémarrage public, nouvelle application ou modification de secrets n’est effectué. Tâche 11 non commencée.
