# Sécurité et gouvernance — démonstration CommercePilot AI

## Décision de périmètre

Ce projet est une démonstration académique sur AtlasShop synthétique, pas un espace client authentifié. Le site public doit rester **Mock uniquement**, sans secrets Groq. Les rôles client/analyste/administrateur sont sélectionnables : les contrôles de permission ne valent que pour le contexte fourni par une application de confiance. Il ne faut pas y charger de données personnelles, secrets ou commandes réelles. Cette politique ne prétend pas garantir une sécurité absolue.

Les cinq parcours publics de tâche 10 sont déclarés réussis par la propriétaire. Le SHA du runtime et Python restent à confirmer dans les logs Streamlit. L'audit de tâche 11 n'a pas consulté les Secrets du tableau de bord, modifié l'application ni refait la recette publique.

## Responsabilités et changements

La propriétaire/responsable du projet valide l'acceptation des risques, les droits des plateformes, toute activation d'API, les accès aux journaux et les décisions de publication/reprise. La revue par PR doit distinguer changement de présentation, de permissions, de données et de fournisseur. Les tests/gates doivent passer, mais ne remplacent pas une revue humaine. Les recommandations du registre ne sont pas des protections déjà déployées.

Avant toute production : authentification, rôles issus du serveur, rattachement client/compte, isolation du stockage, quotas d'API, minimisation des entrées, politique fournisseur, rétention appliquée et surveillance opérationnelle. Sans ces prérequis, le projet n'est pas prêt pour des données réelles ou une API ouverte au public.

## Frontières vérifiées

| Outil | Client | Analyste | Administrateur |
| --- | --- | --- | --- |
| search_faq | Autorisé | Autorisé | Autorisé |
| get_order_status | Ses commandes seulement | Refusé | Toutes les commandes synthétiques |
| sales_summary | Refusé | Agrégats | Agrégats |

Le rôle et customer_id ne sont pas des paramètres LLM. Les schémas n'acceptent que query, order_id ou period et rejettent les clés supplémentaires. L'outil de suivi réapplique la propriété et retourne le même refus pour une commande absente ou appartenant à un autre client. Aucun nom, ville, montant ou identité client n'est exposé dans le suivi autorisé ; seuls identifiant/statuts/dates utiles sont renvoyés. Les ventes sont agrégées sans détail individuel. Aucun outil de mutation n'existe.

Les appels d'un lot sont tous validés avant exécution. Un appel interdit refuse le lot ; un refus sur un tour ultérieur masque les données accumulées. Le contexte est copié, les IDs doivent être explicites et les périodes proposées doivent correspondre aux bornes déterministes. Les limites d'itérations, appels, tokens et longueur sont conservées. Les réponses privées de raisonnement ne sont ni utilisées pour l'affichage ni journalisées.

Le filtre d'injection est lexical, avec une exception étroite aux remboursements informatifs reconnus. Une obfuscation peut échapper au filtre ; le nouveau test démontre qu'une demande de ventes obfusquée reste bloquée par la permission client. Ce test ne prouve pas que toutes les injections sont détectées. La protection principale est la liste d'outils en lecture seule et les contrôles locaux d'arguments/permission, pas le prompt système.

Les messages utilisateur et assistant sont affichés sans unsafe_allow_html ; le HTML/CSS autorisé est réservé à la présentation statique et à des valeurs de sélection contrôlées. Cela ne vaut pas une validation universelle de tout Markdown ou contenu futur. Les erreurs UI sont masquées par un message neutre, et les erreurs fournisseur par catégories. L'observabilité n'enregistre pas d'exception brute.

## Minimisation et flux de données

| Donnée | Usage et destination | Situation actuelle | Règle |
| --- | --- | --- | --- |
| CSV AtlasShop | Outils locaux ; dépôt public | Synthétiques, clients = identifiant et ville fictifs | Ne jamais remplacer par des données réelles sans nouvelle conception |
| Question et historique UI | Session serveur Streamlit | Texte brut, historique de conversation sans plafond total ; quatre questions au plus envoyées au planificateur | Ne pas saisir de secret/PII ; plafonner/expirer avant production |
| Contexte role/customer_id | Application et outils locaux | Sélecteur de démonstration ; pas transmis comme identité au LLM | Serveur authentifié obligatoire avant production |
| Requête Groq | Fournisseur externe si mode explicitement utilisé | Peut contenir le texte de la question et quatre questions antérieures ; aucun résultat métier réinjecté | Pas de Groq public ; revue fournisseur et minimisation avant données réelles |
| Réponse structurée | Session UI | Données locales autorisées uniquement ; masquées en refus/erreur | Ne pas exposer de résultat privé dans les diagnostics |
| Trace runtime | logs/agent_events.jsonl local | UUID, horodatage, durée, outils/statut/erreur sur listes blanches ; aucun texte | Accès opérateur uniquement ; ne pas exposer en UI publique |
| Corpus et rapports d'évaluation | Dépôt | Questions et identifiants synthétiques explicites | Ne pas les confondre avec des conversations runtime anonymisées |
| Artefacts CI | GitHub Actions | Projection numérique et verdicts ; deux fichiers, trois jours configurés | Ni logs bruts, ni traces individuelles ; revue des accès |

L'expression « traces anonymisées » désigne ici la suppression du contenu métier et des identifiants directs, **pas une anonymisation irréversible garantie** : UUID et horodatages restent des métadonnées opérationnelles potentiellement recoupables. Ne pas publier les journaux runtime. Les agrégats issus de sept scénarios Mock ne sont pas une mesure de trafic ou de sécurité en production.

## Conservation : état réel et politique recommandée

- **Sessions** : mémoire du serveur/session, reset lors d'un changement de rôle/client/mode. Pas de TTL explicite, plafond de messages ou stockage persistant. La fermeture d'un onglet n'est pas une preuve de purge immédiate des mémoires ou journaux de la plateforme.
- **Logs runtime** : création en 0600, dossier ignoré par Git. Pas de rotation, durée maximale ou purge automatique. Le système ne modifie pas les droits d'un fichier préexistant. Le disque Cloud est potentiellement éphémère et ne constitue pas une archive durable.
- **Politique proposée pour la démo** : limiter manuellement les journaux utiles au diagnostic à sept jours, puis supprimer les copies inutiles après revue de l'incident. Cette durée n'est **pas implémentée**, n'est pas un délai légal imposé et doit être validée par la propriétaire. Avant production, appliquer techniquement rotation/TTL, droits et règles de sauvegarde adaptés.
- **Artefacts CI** : rétention configurée à trois jours ; les logs de job GitHub ont leur propre rétention, qui n'a pas été inspectée dans les paramètres du compte.
- **Rapports et corpus synthétiques versionnés** : conservation dans l'historique académique. Un secret découvert dans l'historique doit être révoqué immédiatement ; sa suppression du dernier arbre ne le retire pas de Git.
- Les garanties de suppression des copies hébergées et les paramètres réels des plateformes ne sont pas attestés par ce document. Aucune conformité réglementaire ou certification n'est revendiquée.

## Secrets, GitHub et CI

.env, variantes, .streamlit/secrets.toml, clés et logs sont exclus ; seul .env.example vide est versionné. Les exclusions ne sont ni chiffrement ni protection rétroactive. Le scanner détecte des motifs et les valeurs de secrets connues de l'environnement sans les imprimer ; les secrets encodés, formats inconnus, secrets non accessibles à cet environnement, LFS et messages de commit peuvent échapper au contrôle.

La CI est à contents:read, sans pull_request_target, sans secret de dépôt injecté, avec variables Groq vides et credentials de checkout non persistés. Les actions officielles sont épinglées par SHA, les dépendances directes fixées mais pas toutes les transitives. Les tests bloquent les connexions Python usuelles ; ce n'est pas un sandbox système contre une PR malveillante. La revue de code reste indispensable. Protections de branche, MFA, inventaire réel des tokens et secrets GitHub/Streamlit : à confirmer par la propriétaire, pas vérifiés depuis le code.

Le run réel de référence 42714484210 présente un artefact non expiré lors de l'inspection, avec création le 9 novembre et expiration le 12 novembre 2026. La configuration/projection locale est testée, mais le ZIP distant n'a pas pu être récupéré par le réseau local : son contenu binaire n'est pas réputé audité. Aucun lien temporaire de téléchargement n'est conservé dans les livrables.

## Gestion d'incident : procédure proposée, pas automatisée

1. Qualifier le signal : panne technique, refus normal, injection sans effet, fuite de données ou clé compromise. Une clarification n'est pas une panne de sécurité.
2. Contenir : en cas d'abus/fuite, la propriétaire retire la configuration Groq publique et **révoque la clé chez le fournisseur** si compromise ; le retrait d'un fichier ou d'un secret Streamlit seul ne la révoque pas. Restreindre l'accès au site ou le suspendre si nécessaire, avec autorisation adaptée. Aucun changement de compte n'est effectué par cet audit.
3. Préserver le minimum : heure, request_id, SHA du runtime s'il est connu, version Python, catégorie d'erreur, compteurs et gates. Ne pas copier question, réponse privée, clé ou raisonnement dans un ticket public. Conserver toute preuve nécessaire à accès restreint, limitée au besoin ; ne pas créer de nouveau journal de PII pour enquêter.
4. Diagnostiquer hors ligne, reproduire avec fixtures, examiner la portée et les accès autorisés. Les pannes de logging peuvent avoir perdu des événements : ne pas interpréter l'absence de trace comme absence d'incident.
5. Corriger par PR revue, relancer les gates et vérifier la recette de reprise en Mock. Toute nouvelle activation Groq réclame d'abord les protections P0 du registre, pas une simple sélection UI.
6. Consigner décision, impact, mesures de confinement, validation de reprise et suppression des copies devenues inutiles. La communication aux personnes/autorités éventuellement concernées relève d'une analyse de l'incident réel, pas d'une garantie juridique du projet.

## Audit et preuves

`python -m security.audit` contrôle les fichiers courants/non ignorés, les blobs atteignables de l'historique Git par motifs, les exclusions et les sept traces d'exemple. Les résultats sont dans security/audit_results.json. Le scan historique concerne les références locales récupérées, pas une preuve d'absence de secrets sur tout objet distant ou toute copie. Le script ne lit aucune valeur de secret distant depuis GitHub ou Streamlit.

Le registre est dans [security_risks.md](security_risks.md), avec sa version structurée dans security/risk_register.json. Les tests de tâche 11 complètent les tests existants de permissions, lots, erreurs et journaux. Le bilan final, les limites de déploiement restantes et les mesures réellement obtenues sont consignés dans le rapport progressif. Les droits des plateformes et l'acceptation des risques doivent être validés par la propriétaire avant de qualifier le système pour un autre usage.
