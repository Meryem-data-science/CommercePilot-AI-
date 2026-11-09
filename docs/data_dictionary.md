# Dictionnaire des données — AtlasShop, tâche 3.A

Les six fichiers de données sont entièrement synthétiques, encodés en UTF-8 avec fins de ligne LF. Les CSV utilisent une virgule, une ligne d'en-tête et le point comme séparateur décimal. Les montants représentent des MAD à deux décimales, jamais des flottants binaires. Les chaînes vides représentent les dates réelles non applicables. Aucun nom de personne, contact ou adresse personnelle n'est généré.

## Tables et colonnes

### products.csv — 50 lignes

| Colonne | Type | Signification et contrainte |
| --- | --- | --- |
| product_id | texte, clé primaire | `PRD-001` à `PRD-050`, identifiant unique |
| name | texte | Désignation synthétique non vide |
| category | texte | Électronique, habillement, accessoires, maison ou beauté |
| price_mad | décimal (2 décimales) | Prix final strictement positif, catalogue figé |
| stock | entier | Photographie du stock à la référence, supérieur ou égal à zéro |
| availability | enum | `disponible` si stock positif, sinon `rupture` |
| description | texte | Description fictive du produit et de sa gamme |

Le stock n'est pas reconstitué à partir des ventes historiques. Un produit vendu dans le passé peut être en rupture à la date de référence.

### customers.csv — 30 lignes

| Colonne | Type | Signification et contrainte |
| --- | --- | --- |
| customer_id | texte, clé primaire | `CLI-001` à `CLI-030`, stable |
| city | texte | Ville marocaine, sans adresse ni contact |

Les noms de villes désignent des lieux publics, sans identifier des personnes. Les identifiants permettront de vérifier ultérieurement la propriété des commandes, sans constituer une authentification.

### orders.csv — 300 lignes

| Colonne | Type | Signification et contrainte |
| --- | --- | --- |
| order_id | texte, clé primaire | `CMD-DEMO-001` à `CMD-DEMO-300` |
| customer_id | texte, clé étrangère | Référence `customers.customer_id` |
| order_date | date ISO `YYYY-MM-DD` | Entre le 2026-04-01 et le 2026-09-30 inclus |
| order_status | enum | `livree`, `en_preparation`, `expediee`, `annulee`, `retournee` |
| payment_status | enum | `paid`, `pending`, `unpaid`, `refunded` selon la matrice ci-dessous |
| delivery_status | enum | État logistique compatible avec la commande |
| total_mad | décimal (2 décimales) | Somme exacte des lignes ; positive, conservée même en cas d'annulation ou retour |
| expected_delivery_date | date ISO | Date de commande + 5 jours calendaires, même pour une commande ensuite annulée |
| actual_delivery_date | date ISO ou vide | Livraison initiale d'une commande livrée ou retournée ; vide autrement |
| is_delayed | booléen textuel | `true` ou `false` calculé selon la règle de retard |

| Commande | Paiement autorisé | Livraison | Date réelle |
| --- | --- | --- | --- |
| `livree` | `paid` | `delivered` | Obligatoire |
| `en_preparation` | `paid` ou `pending` | `not_shipped` | Vide |
| `expediee` | `paid` ou `pending` | `in_transit` | Vide |
| `annulee` | `unpaid` | `cancelled` | Vide |
| `retournee` | `refunded` | `returned` | Obligatoire, livraison initiale |

Une annulation précède ici tout encaissement ou expédition. Une commande retournée est intégralement retournée et remboursée ; la date réelle désigne sa livraison initiale, pas son retour. Les dates d'encaissement, d'expédition, d'annulation, de retour et de remboursement ne sont pas modélisées. Une livraison réelle respecte `order_date <= actual_delivery_date <= 2026-10-01`. Une commande en transit avec paiement en attente représente le paiement à la livraison.

### order_items.csv — 600 lignes

| Colonne | Type | Signification et contrainte |
| --- | --- | --- |
| order_item_id | texte, clé primaire | `ITM-0001` à `ITM-0600` |
| order_id | texte, clé étrangère | Référence `orders.order_id` |
| product_id | texte, clé étrangère | Référence `products.product_id` |
| quantity | entier positif | Entre 1 et 3 dans le générateur |
| unit_price_mad | décimal (2 décimales) | Prix catalogue figé, strictement positif |
| line_total_mad | décimal (2 décimales) | `quantity × unit_price_mad`, calcul exact |

Chaque commande contient 1, 2 ou 3 produits distincts. Le catalogue ne varie pas dans le temps. Les prix incluent les frais simulés : ni livraison supplémentaire, ni remise, ni ventilation fiscale. Les entiers en centimes servent à la génération, `Decimal` à la validation.

### faq.csv — 35 lignes ; faq.md — rendu lisible

| Colonne CSV | Type | Signification et contrainte |
| --- | --- | --- |
| source_id | texte, clé primaire | `FAQ-001` à `FAQ-035`, source stable |
| category | texte | Une des neuf catégories documentaires |
| question | texte non vide | Question distincte après normalisation de casse |
| answer | texte non vide | Réponse éditoriale précise et fictive |
| version | texte | `1.0` |

La FAQ couvre livraison, paiement, suivi, retours, remboursements, annulations, disponibilité, service client et conditions générales. Le contenu éditorial est défini une seule fois dans `faq_rows()` du générateur ; `faq.csv` est sa référence structurée exportée pour les futurs consommateurs. `faq.md` en est un rendu strictement synchronisé, vérifié automatiquement. Toute évolution passe par la source du générateur puis une régénération contrôlée, jamais par une modification indépendante du Markdown.

## Définitions prévisionnelles des KPI

Le futur outil `sales_summary` n'est pas implémenté. Les définitions ci-dessous constituent le contrat métier de cette base. Toute période utilise `order_date`, avec bornes inclusives. Tous les états sont observés au **2026-10-01**, pas à la fin historique de la période. Aucun indicateur de flux d'encaissement ou de livraison par date d'événement ne peut être calculé avec ces seules colonnes.

| Indicateur | Définition et inclusion |
| --- | --- |
| Nombre de commandes | Comptage des commandes de la période, tous statuts inclus ; afficher séparément les annulations et retours |
| Montant total commandé | Somme de `total_mad` de toutes les commandes de la période, y compris annulées et retournées ; volume brut d'intention d'achat, pas un revenu |
| Montant des commandes payées | Somme de `total_mad` lorsque `payment_status = paid` ; inclut les avances des commandes en cours, exclut `pending`, `unpaid`, `refunded` ; paiement actuellement conservé, pas encaissements historiques bruts |
| Chiffre d'affaires réalisé | Somme de `total_mad` uniquement pour `order_status = livree` ET `payment_status = paid` ; exclut commandes en cours, annulées et retournées ; convention pédagogique, pas une norme comptable |
| Annulations | Nombre et montant brut des commandes `annulee` ; jamais incluses dans le paiement conservé ni dans le CA |
| Retours | Nombre et montant brut des commandes `retournee` ; remboursement intégral, donc exclus du paiement conservé et du CA |
| Retards de livraison constatés | Pour `livree` ou `retournee` : date réelle strictement postérieure à la date prévue ; un retour ne supprime pas le retard initial |
| Retards en cours | Pour `en_preparation` ou `expediee` : référence strictement postérieure à la date prévue et date réelle vide |
| Nombre total de retards | Somme des deux groupes précédents ; `is_delayed = true` ; annulations exclues |

Une échéance égale à la date de référence n'est pas encore dépassée. Une période valide sans commande donnera des comptes et montants nuls ; un éventuel taux à dénominateur nul devra être indiqué non applicable. Aucun taux de retard n'est défini ici. Les sommes restent en centimes ou en décimaux exacts ; leur affichage conserve deux décimales, sans cumul de nombres binaires flottants.

## Références d'autorisation futures

| Commande | Propriétaire | État |
| --- | --- | --- |
| CMD-DEMO-001 | CLI-001 | livree |
| CMD-DEMO-002 | CLI-002 | en_preparation |
| CMD-DEMO-005 | CLI-005 | retournee |

Par exemple, `CLI-001` devra être autorisé sur la première et refusé sur la deuxième. Ces références suivent les règles ordinaires ; aucune exception d'accès n'est introduite. Aucun test d'outil ou de permission applicative n'est encore exécuté.

Voir [la méthode de génération](data_generation.md) pour les paramètres, limites et preuves.
