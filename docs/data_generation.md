# Génération et validation AtlasShop

## Paramètres et hypothèses

- Python vérifié : **3.11.14**, bibliothèque standard uniquement.
- Graine par défaut : **202627**, instance locale `random.Random` sans état aléatoire global.
- Période fixe : **2026-04-01 au 2026-09-30** ; date de référence : **2026-10-01**.
- 50 produits (10 par catégorie), 30 clients (10 villes), 300 commandes, 600 lignes et 35 FAQ.
- Quotas pédagogiques : 210 livrées (70 %), 24 en préparation (8 %), 36 expédiées (12 %), 18 annulées (6 %), 12 retournées (4 %). Il ne s'agit pas de proportions calibrées sur un commerce réel : les livraisons sont majoritaires et les cas minoritaires restent assez nombreux pour des scénarios.
- Les propriétaires restent cycliques parmi 30 identifiants (10 commandes chacun). Les statuts sont mélangés par un générateur pseudo-aléatoire dédié, initialisé avec `seed ^ 0xA71A5`, sans dérivation depuis le client. Trois références sont réservées ; les tirages où un client aurait un seul statut sont rejetés, avec une limite de 1 000 essais. Cette contrainte pédagogique assure la diversité sans prétendre à une indépendance statistique parfaite.
- Chaque commande contient cycliquement 1, 2 ou 3 produits distincts, chacun en quantité de 1 à 3. Les prix vont approximativement de 20 à 900 MAD selon la catégorie et restent constants sur la période.
- Les stocks sont une photographie indépendante, avec des ruptures prévues. Il ne s'agit pas d'une simulation de gestion des stocks historiques.
- Échéance : commande + 5 jours calendaires. Livraison initiale : échéance décalée de -2, -1, 0, 1 ou 3 jours ; 0 est répété six fois dans le tirage à dix possibilités pour favoriser la ponctualité. Les livrées et annulées sont datées au plus tard du 23 septembre ; les retournées au plus tard du 15 septembre, pour laisser du temps à la livraison et au traitement du retour.
- En préparation : 22 commandes âgées de 1 à 3 jours et 2 exceptions âgées de 8 à 10 jours. Expédiées : 30 commandes âgées de 2 à 5 jours et 6 exceptions âgées de 6 à 12 jours. Ces exceptions représentent des incidents fictifs, pas des enregistrements invalides. Toutes les commandes en cours ont au plus 12 jours à la référence.
- Retours et remboursements intégraux uniquement, annulations avant paiement ; pas de remboursement partiel, évolution du catalogue, remise, taxe séparée ou contact personnel.
- FAQ éditoriale française, neuf catégories, politiques exclusivement fictives. Les délais de retour et remboursement sont des règles documentaires ; leurs événements datés ne sont pas simulés.

Les définitions des revenus, annulations, retours et retards sont spécifiées dans le [dictionnaire](data_dictionary.md). Les états à la référence ne permettent pas de reconstruire l'état d'une commande à une date antérieure. Les quotas, dix commandes par client et la concentration des commandes en cours en fin de période sont des choix de démonstration, pas un modèle de demande réelle. La diversité des statuts est imposée et trois références sont fixées ; aucune indépendance statistique universelle n'est revendiquée.

## Exécution depuis la racine

```bash
.venv/bin/python --version
.venv/bin/python data/generate_data.py
.venv/bin/python data/validate_data.py
.venv/bin/python -m unittest discover -s tests -p test_data_validation.py -v
```

La première génération dans `data/` a été exécutée avec succès. Le générateur **refuse d'écraser** une sortie existante. Pour une nouvelle génération sans toucher la référence, choisir un dossier absent ou vide :

```bash
.venv/bin/python data/generate_data.py --output-dir /tmp/atlasshop-nouveau --seed 202627
.venv/bin/python data/validate_data.py --data-dir /tmp/atlasshop-nouveau
```

Les deux dernières commandes sont un exemple d'utilisation ; les sorties indépendantes réellement vérifiées ont été créées par les tests avec `TemporaryDirectory`. Le changement de graine conserve les volumes et références mais modifie les tirages. La reproductibilité est revendiquée pour les mêmes scripts, paramètres et version Python, pas pour toutes les futures versions de l'interpréteur. Aucune horloge système ni requête externe n'intervient.

## Validation exécutée

Le validateur séparé utilise des contrôles explicites levant des erreurs, indépendants de l'option Python `-O`. Une violation renvoie un code de sortie 1 avec un diagnostic. Il contrôle volumes, unicité des clés, relations, quantités et prix positifs, sommes exactes, stock/disponibilité, dates, compatibilité des statuts, retards, références stables, unicité et synchronisation FAQ. Les schémas et données mal formés essentiels sont également rejetés. La vérification éditoriale de la FAQ reste une revue humaine ; un contrôle structurel ne prouve pas sa qualité sémantique.

Résultats observés : validation de référence réussie ; trois méthodes de tests réussies, sans échec ni omission. La méthode de reproductibilité génère deux dossiers indépendants, valide chacun et compare les SHA-256 des six fichiers entre eux et à la référence. Elle vérifie aussi le refus d'écrasement. Une méthode vérifie aussi les quotas, la diversité des statuts par client et l’âge des commandes en cours. La méthode négative rejette huit copies altérées (client inconnu, produit inconnu, total incohérent, paiement incompatible, date réelle future, retard incorrect, disponibilité incorrecte et quantité nulle), chacune avec le code 1 et le diagnostic attendu. Les fichiers de référence ne sont jamais altérés par ces tests. Aucun outil métier, LLM ou test d'agent n'est exécuté.

### Empreintes des fichiers identiques dans les trois jeux

| Fichier | SHA-256 |
| --- | --- |
| products.csv | `d883c6f87732166b43859711e9ca0201da3cd8b5fb27ffbcb1ec84776dae9479` |
| customers.csv | `30055ce094ce983a2c04b5766b16921c769de26e31aae2c42e0f786815407777` |
| orders.csv | `9e5ac1e1315badc0a222140c210e6716a9fb37c984d23e4f9b2fad9e7f6b623d` |
| order_items.csv | `ef21d2ed6b05d585e9a98af9913a4add535add32f0634dab79b8b0fee5714376` |
| faq.csv | `8f1e475715ac1b6df1e2de21ce49b44aba8a000a0e36cf9c4e21ad937bb69c0b` |
| faq.md | `685afc860031bf54f2eaec1e9f6919031518f80793ed96bdf6d36a34432d8c68` |

## Preuves techniques utiles

Conserver les sorties du validateur, de `unittest` et des empreintes. Pour le rapport, une capture du résumé de validation et un extrait de quelques commandes reliées à leurs lignes suffisent ; ne pas capturer des centaines de lignes ni une conversation. Aucune capture n'est créée dans cette tâche. Les contrôles sont reproductibles via les commandes ci-dessus et restent locaux avant publication.

## Vérification ciblée du réalisme

Le diagnostic initial a confirmé une dépendance déterministe : `customer_id = 1 + (i-1) % 30` et statut selon `(i-1) % 5`, avec 30 divisible par 5. Les 30 clients n'avaient chacun qu'un seul statut. Après mélange sous contrainte de diversité, les 30 clients ont plusieurs statuts : 7 en ont deux, 16 en ont trois et 7 en ont quatre. La propriété et l'état de CMD-DEMO-001, CMD-DEMO-002 et CMD-DEMO-005 restent inchangés. Aucun droit d'accès n'est introduit par le générateur.

| Statut | Avant | Après | Retards avant → après |
| --- | --- | --- | --- |
| Livrée | 60 (20 %) | 210 (70 %) | 29 → 37 |
| En préparation | 60 (20 %) | 24 (8 %) | 58 → 2 |
| Expédiée | 60 (20 %) | 36 (12 %) | 57 → 6 |
| Annulée | 60 (20 %) | 18 (6 %) | 0 → 0 |
| Retournée | 60 (20 %) | 12 (4 %) | 31 → 1 |

Auparavant, 100 des 120 commandes en cours avaient plus de 30 jours (49 en préparation et 51 expédiées), jusqu'à 180 jours. Après correction, les 60 commandes en cours ont de 1 à 11 jours observés : préparation 1–10 jours, expédition 2–11 jours, avec 8 retards. Les 46 retards totaux incluent également 37 livraisons tardives et un retour dont la livraison initiale était tardive. Les retours, annulations et incidents restent représentés sans saturer le jeu. Ces proportions sont des hypothèses pédagogiques plus plausibles, sans preuve d'adéquation à une boutique réelle.

La nouvelle génération a d'abord été produite dans `/tmp/atlasshop-realism-candidate`, puis validée par le validateur et les trois méthodes de tests via `ATLASSHOP_DATA_DIR=/tmp/atlasshop-realism-candidate`. L'ancienne référence a été conservée dans `/tmp/atlasshop-realism-before`. Seuls `orders.csv` et `order_items.csv` ont ensuite été remplacés : produits, clients et FAQ sont inchangés. Le fichier de lignes change car le nouveau calendrier modifie la consommation des tirages aléatoires ; les prix et sommes exactes restent validés. La suite complète et le validateur ont ensuite été relancés sur la référence retenue. Les KPI, la période, la graine et la date de référence ne changent pas.
