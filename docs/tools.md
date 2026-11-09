# Outils métier indépendants du LLM — tâche 3.B

Python 3.11.14, bibliothèque standard, lecture locale uniquement. Aucun outil n'écrit de données, n'appelle le réseau ou n'exécute de contenu documentaire. Imports depuis la racine : `from src.tools.faq import search_faq`, `from src.tools.orders import get_order_status`, `from src.tools.analytics import sales_summary`.

## Contrat commun

Chaque appel retourne un dictionnaire sérialisable JSON : `{"status": ..., "message": ..., "data": ...}`. `message` est un diagnostic générique, sans traceback ni chemin. `data` vaut `null` hors succès. Statuts : `ok`, `invalid_input`, `access_denied`, `not_found` (FAQ uniquement), `data_error`. Les erreurs d'argument et refus sont décidés avant toute lecture. Le code commun résout un dossier `data/` fixe relativement aux sources ; aucun chemin ne provient des arguments publics. Les tests seuls peuvent substituer ce dossier avec `unittest.mock`.

Les CSV sont relus à chaque appel. Schéma, lignes incomplètes, clés dupliquées et tables vides sont rejetés. Les commandes font l'objet d'une validation de format, montants, dates, combinaison d'états et retard. Les erreurs d'ouverture, d'encodage, de parsing et de données déclenchent `data_error`, sans détail interne. La validation exhaustive des relations intertables et sommes des lignes reste assurée par `data/validate_data.py`, à exécuter avant utilisation. Les outils ne reconstituent pas les totaux depuis les lignes à chaque requête.

## `search_faq(query)`

Question textuelle non vide, au plus 500 caractères bruts, sans caractère de contrôle. La normalisation applique casse uniforme, décomposition Unicode et suppression des accents. Les mots sont extraits par expression régulière ; une liste explicite de mots peu informatifs est retirée. Une question sans terme restant est invalide.

Chaque question du corpus est comparée aux termes de la requête. Le score est le nombre de termes communs divisé par le nombre de termes distincts de la requête. Un résultat exige au moins un terme commun et un score supérieur ou égal à 0,5 : seuil heuristique de couverture lexicale, sans prétention de calibration statistique. Le meilleur score est choisi, puis le plus grand nombre de correspondances, puis l'identifiant de source croissant pour départager. Les réponses ne servent pas au classement, afin de limiter les correspondances à des mentions secondaires.

En succès, `data` contient `answer` (texte documentaire), `source_id`, `version` et `score` (nombre arrondi à quatre décimales). Sinon `not_found` signale l'absence de correspondance suffisante, sans réponse inventée. Le score n'est pas une probabilité de justesse. Le lexique ne traite pas les synonymes, négations, intentions complexes ou paraphrases ; une question ambiguë peut sélectionner un résultat imparfait. Une requête composée pourra nécessiter une décomposition ultérieure par l'orchestrateur.

Les instructions présentes dans la FAQ restent des chaînes non exécutées. Leur restitution n'est pas un filtrage d'injection : un futur modèle devra continuer à les traiter comme des données non fiables. L'outil ne reçoit pas de rôle ; il est accessible aux trois profils dont le contexte valide sera garanti en amont.

## `get_order_status(order_id, role, customer_id)`

- `order_id` : texte strict `CMD-DEMO-` et trois chiffres, sans espace supplémentaire.
- `role` : `client`, `analyste` ou `administrateur`, sans conversion implicite.
- Pour `client`, `customer_id` doit être un texte `CLI-` et trois chiffres ; la propriété est comparée à la ligne de commande.
- Pour `administrateur`, `customer_id` doit être `None` (identité client sans objet).
- Pour `analyste`, l'accès est refusé sans lecture ; `customer_id` n'est pas utilisé.

Le client lit ses seules commandes ; l'administrateur lit toutes les commandes synthétiques. En succès, `data` contient uniquement `order_id`, `order_status`, `delivery_status`, `expected_delivery_date`, `actual_delivery_date` (vide en l'absence de livraison). Ni propriétaire, ni montant, ni paiement, ni coordonnées ne sont exposés.

Commande inexistante, propriété non autorisée et accès analyste produisent exactement `access_denied`, le message « Je ne peux pas consulter cette commande avec ce profil. » et `data: null`. Un format invalide ou un contexte client manquant produit `invalid_input` avant lecture.

## `sales_summary(period, role)`

`period` est exactement un dictionnaire contenant deux clés : `start_date` et `end_date`, chaînes ISO strictes `YYYY-MM-DD`, dates calendaires valides avec début inférieur ou égal à fin. Les clés supplémentaires sont refusées. Les bornes sur `order_date` sont inclusives. La période peut être extérieure à celle des données : un résultat vide reste un succès, distinct d'une panne. Seuls `analyste` et `administrateur` sont autorisés ; les autres rôles sont refusés avant lecture.

Le résultat `data` contient `period`, `reference_date` (2026-10-01), `currency` (MAD), et :

| Champ | Définition |
| --- | --- |
| order_count | Toutes les commandes sélectionnées |
| ordered_amount_mad | Montant brut, tous statuts |
| paid_amount_mad | Paiements `paid`, avances comprises, remboursements exclus |
| realized_revenue_mad | Commandes `livree` et `paid` seulement |
| cancelled_count / cancelled_amount_mad | Nombre et montant brut des annulations |
| returned_count / returned_amount_mad | Nombre et montant brut des retours |
| delivered_late_count | Livrées ou retournées dont la livraison initiale dépasse l'échéance |
| ongoing_late_count | Préparation ou expédition au-delà de l'échéance à la référence |
| delayed_count | Somme des deux groupes de retards |

Les montants utilisent `Decimal` et sont sérialisés en chaînes à deux décimales. Les comptes sont entiers. Les périodes vides ont tous leurs comptes et montants à zéro. Aucun identifiant individuel n'est renvoyé. Les conventions du [dictionnaire](data_dictionary.md) sont conservées ; il s'agit d'états à la référence, pas de flux d'événements historiques.

## Exemples réellement exécutés

```python
search_faq('Quels sont les délais de livraison ?')
# ok, source FAQ-002, version 1.0, score 1.0 ; échéance cinq jours calendaires.
get_order_status('CMD-DEMO-001', 'client', 'CLI-001')
# ok, livree, delivered, livraison prévue et réelle : 2026-07-22.
get_order_status('CMD-DEMO-002', 'client', 'CLI-001')
# access_denied, message neutre, data=None.
sales_summary({'start_date':'2026-04-01', 'end_date':'2026-09-30'}, 'analyste')
# ok : 300 commandes, brut 355677.20 MAD, payé 280738.30 MAD,
# CA réalisé 243634.20 MAD ; 18 annulations, 12 retours, 46 retards.
```

## Validation et limites de sécurité

```bash
.venv/bin/python data/validate_data.py
.venv/bin/python -m unittest discover -s tests -p test_tools.py -v
.venv/bin/python -m unittest discover -s tests -v
```

Quinze tests d'outils couvrent entrées, FAQ, sources, absence de correspondance, permissions, refus neutres, périodes, montants et retards, fichiers absents ou invalides et absence de lecture avant refus. L'oracle de calcul utilise six commandes contrôlées : brut 242.61, payé 121.41, CA réalisé 101.21 MAD, une annulation à 40.40, un retour à 50.50 et quatre retards. Les attentes sont établies manuellement, indépendamment de la fonction. Les trois tests de données existants complètent la suite.

Le contexte de rôle est une simulation, pas une authentification. Un appelant pouvant choisir `administrateur` peut obtenir les résultats correspondants. Les tâches 4/5 devront imposer côté application la provenance fiable de `role` et `customer_id`, sans délégation au message ni au LLM. Aucune résistance générale aux injections, aucun service de production ni orchestrateur n'est revendiqué.
