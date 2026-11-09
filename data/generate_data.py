"""Génération déterministe AtlasShop ; Python 3.11.14, bibliothèque standard."""
import argparse
import csv
from datetime import date, timedelta
from pathlib import Path
import random

SEED = 202627
REFERENCE = date(2026, 10, 1)
START = date(2026, 4, 1)
END = date(2026, 9, 30)
FILES = ('products.csv', 'customers.csv', 'orders.csv', 'order_items.csv', 'faq.csv', 'faq.md')


def money(cents):
    return f'{cents // 100}.{cents % 100:02d}'


def faq_rows():
    """Source éditoriale unique des deux rendus FAQ ; règles fictives."""
    groups = {
        'Livraison': [
            ('Où livrez-vous ?', 'AtlasShop livre uniquement au Maroc dans les villes desservies de cette démonstration.'),
            ('Quels sont les délais de livraison ?', 'La date prévue est fixée à cinq jours calendaires après la commande ; il ne s’agit pas d’une garantie.'),
            ('Quels sont les frais de livraison ?', 'Dans cette simulation, la livraison est incluse : aucun frais supplémentaire ne figure dans le total.'),
            ('Livrez-vous le week-end ?', 'Les dates simulées utilisent des jours calendaires, y compris les week-ends.'),
            ('Comment reconnaître un retard ?', 'Une livraison effectuée après la date prévue est tardive ; une commande en cours est en retard si la date de référence dépasse la date prévue.'),
        ],
        'Paiement': [
            ('Quels moyens de paiement sont prévus ?', 'La boutique fictive prévoit le paiement anticipé et le paiement à la livraison ; aucune transaction réelle n’est possible.'),
            ('Que signifie un paiement en attente ?', 'Aucun encaissement n’est enregistré. Une commande en préparation peut rester en attente de paiement.'),
            ('Une commande livrée peut-elle être impayée ?', 'Dans cette base de démonstration, toute commande livrée est payée.'),
            ('Dans quelle devise sont les prix ?', 'Tous les prix et totaux sont exprimés en dirhams marocains, MAD, avec deux décimales.'),
        ],
        'Suivi': [
            ('Comment suivre ma commande ?', 'Fournissez son identifiant ; le profil client ne peut consulter que ses propres commandes.'),
            ('Où trouver mon identifiant de commande ?', 'La démonstration utilise des identifiants CMD-DEMO suivis de trois chiffres, séparés par des tirets.'),
            ('Puis-je suivre la commande d’un autre client ?', 'Non. La consultation par un client est limitée aux commandes qui lui appartiennent.'),
            ('Que signifie en préparation ?', 'La commande est enregistrée mais n’a pas encore été remise au transporteur fictif.'),
            ('Que signifie expédiée ?', 'La commande a été remise au transporteur fictif ; aucune date réelle de livraison n’est encore enregistrée.'),
        ],
        'Retours': [
            ('Quel est le délai de retour ?', 'La politique fictive prévoit une demande dans les sept jours calendaires suivant la livraison.'),
            ('Quels produits peuvent être retournés ?', 'Les articles doivent être inutilisés, complets et dans leur emballage ; les produits d’hygiène descellés sont exclus dans cette politique fictive.'),
            ('Comment demander un retour ?', 'La FAQ explique la procédure ; une demande doit être traitée par un support humain fictif, hors de l’agent.'),
            ('Que signifie une commande retournée ?', 'Dans la simulation, tous les articles de la commande ont été retournés et le remboursement intégral est enregistré.'),
        ],
        'Remboursements': [
            ('L’agent peut-il me rembourser ?', 'Non. L’agent fournit des informations et n’exécute aucun remboursement.'),
            ('Quel est le délai de remboursement ?', 'La politique fictive prévoit cinq jours calendaires après acceptation du retour par le support ; ces dates de traitement ne sont pas modélisées.'),
            ('Le remboursement est-il partiel ?', 'La base actuelle représente uniquement des retours et remboursements complets ; les cas partiels sont exclus.'),
            ('Que signifie remboursé ?', 'Le paiement initial a été restitué intégralement ; il ne contribue plus au montant actuellement payé.'),
        ],
        'Annulations': [
            ('Quand une annulation est-elle possible ?', 'La politique fictive autorise une demande avant expédition, à traiter hors de l’agent.'),
            ('L’agent peut-il annuler une commande ?', 'Non. Aucun outil prévu ne modifie les commandes.'),
            ('Une commande annulée est-elle facturée ?', 'Les annulations simulées surviennent avant encaissement et avant livraison ; elles ne contribuent pas au chiffre d’affaires.'),
        ],
        'Disponibilité': [
            ('Comment connaître la disponibilité ?', 'Le catalogue fictif indique disponible si le stock est positif, sinon rupture.'),
            ('Un article en rupture sera-t-il réapprovisionné ?', 'Aucune date de réapprovisionnement n’est prévue dans la base ; il ne faut pas en inventer.'),
            ('Le stock reflète-t-il les ventes historiques ?', 'Le stock est une photographie synthétique à la date de référence, sans registre de mouvements historiques.'),
        ],
        'Service client': [
            ('Comment contacter le support ?', 'La démonstration ne fournit aucun contact réel ; utiliser le canal humain fictif prévu dans le scénario académique.'),
            ('Quels sont les horaires du support ?', 'Les horaires fictifs sont du lundi au vendredi, de 9 h à 17 h, heure du Maroc.'),
            ('Que faire si le suivi est indisponible ?', 'Réessayer ultérieurement ; un incident technique ne permet pas de déduire le statut de la commande.'),
        ],
        'Conditions générales': [
            ('AtlasShop est-elle une véritable boutique ?', 'Non. AtlasShop est une boutique entièrement fictive créée pour un projet académique.'),
            ('Les prix incluent-ils des taxes supplémentaires ?', 'Les montants simulés sont des montants finaux ; aucune taxe supplémentaire ni ventilation fiscale n’est modélisée.'),
            ('Mes données personnelles sont-elles utilisées ?', 'Non. Seuls des identifiants synthétiques et des villes sont conservés pour les clients.'),
            ('Les conditions de vente ont-elles une portée juridique ?', 'Non. Toutes ces règles sont fictives et servent uniquement à la démonstration pédagogique.'),
        ],
    }
    return [dict(source_id=f'FAQ-{i:03}', category=c, question=q, answer=a, version='1.0')
            for i, (c, q, a) in enumerate(((c, q, a) for c, rows in groups.items() for q, a in rows), 1)]


def render_faq(rows):
    return '# FAQ AtlasShop — règles entièrement fictives\n\n' + ''.join(
        f"## {r['source_id']} — {r['question']}\n\nCatégorie : {r['category']} | Version : {r['version']}\n\n{r['answer']}\n\n" for r in rows)


def generate(output, seed=SEED):
    output.mkdir(parents=True, exist_ok=True)
    if any((output / f).exists() for f in FILES):
        raise FileExistsError('Sortie déjà présente : choisir un nouveau dossier pour éviter tout écrasement.')
    rng = random.Random(seed)
    catalogue = {
        'Électronique': ('Casque audio|Souris sans fil|Clavier compact|Enceinte portable|Chargeur USB|Batterie externe|Support téléphone|Webcam|Câble USB|Lampe de bureau', 5900, 89900),
        'Habillement': ('T-shirt coton|Chemise lin|Sweat léger|Pantalon toile|Veste mi-saison|Pyjama coton|Polo|Pull maille|Jupe longue|Tenue sport', 7900, 59900),
        'Accessoires': ('Sac à dos|Portefeuille|Ceinture|Casquette|Écharpe|Trousse|Sac bandoulière|Porte-cartes|Bonnet|Pochette voyage', 3900, 44900),
        'Maison': ('Coussin|Plaid|Mug|Boîte rangement|Tapis entrée|Carafe|Serviette|Panier|Horloge|Rideau', 2900, 49900),
        'Beauté': ('Savon doux|Crème mains|Shampooing|Brosse cheveux|Baume lèvres|Gel douche|Huile soin|Peigne|Trousse beauté|Lait corps', 1900, 24900),
    }
    products = []
    prices = {}
    for category, (names, low, high) in catalogue.items():
        for name in names.split('|'):
            pid = f'PRD-{len(products)+1:03}'
            cents = rng.randrange(low // 100, high // 100 + 1) * 100 + 90
            stock = 0 if len(products) % 9 == 0 else rng.randint(1, 120)
            products.append(dict(product_id=pid, name=name, category=category, price_mad=money(cents), stock=stock,
                                 availability='disponible' if stock else 'rupture',
                                 description=f'{name}, gamme {rng.choice(["Essentiel", "Confort", "Évasion"])} AtlasShop ; article fictif de la catégorie {category.lower()}.'))
            prices[pid] = cents
    cities = ['Casablanca', 'Rabat', 'Fès', 'Meknès', 'Marrakech', 'Tanger', 'Agadir', 'Oujda', 'Tétouan', 'Kénitra']
    customers = [dict(customer_id=f'CLI-{i:03}', city=cities[(i-1) % len(cities)]) for i in range(1, 31)]
    # Quotas pédagogiques, mélangés sans calcul du statut depuis le client.
    schedule_rng = random.Random(seed ^ 0xA71A5)
    quotas = {'livree': 210, 'en_preparation': 24, 'expediee': 36,
              'annulee': 18, 'retournee': 12}
    references = {1: 'livree', 2: 'en_preparation', 5: 'retournee'}
    pool = [status for status, count in quotas.items()
            for _ in range(count - list(references.values()).count(status))]
    # Écarter les tirages où un client n'aurait qu'un statut sur ses dix achats.
    for _ in range(1000):
        schedule_rng.shuffle(pool)
        remaining = iter(pool)
        statuses = [references[i] if i in references else next(remaining)
                    for i in range(1, 301)]
        if all(len(set(statuses[c::30])) >= 2 for c in range(30)):
            break
    else:
        raise ValueError("Impossible de construire un calendrier diversifié avec cette graine.")
    active_ages = {}
    for status, count, overdue in [('en_preparation', 24, 2), ('expediee', 36, 6)]:
        normal_range = (1, 3) if status == 'en_preparation' else (2, 5)
        ages = ([schedule_rng.randint(*normal_range) for _ in range(count-overdue)]
                + [schedule_rng.randint(8, 10) if status == 'en_preparation'
                   else schedule_rng.randint(6, 12) for _ in range(overdue)])
        schedule_rng.shuffle(ages)
        active_ages[status] = iter(ages)
    orders, items = [], []
    for i in range(1, 301):
        oid = f'CMD-DEMO-{i:03}'
        status = statuses[i-1]
        if status in active_ages:
            day = REFERENCE - timedelta(days=next(active_ages[status]))
        else:
            latest = date(2026, 9, 15) if status == 'retournee' else date(2026, 9, 23)
            day = START + timedelta(days=schedule_rng.randint(0, (latest-START).days))
        expected = day + timedelta(days=5)
        actual = expected + timedelta(days=schedule_rng.choice([-2, -1, 0, 0, 0, 0, 0, 0, 1, 3])) if status in ('livree', 'retournee') else None
        payment = {'livree':'paid', 'en_preparation':rng.choice(['paid', 'pending']), 'expediee':rng.choice(['paid', 'pending']), 'annulee':'unpaid', 'retournee':'refunded'}[status]
        delivery = {'livree':'delivered', 'en_preparation':'not_shipped', 'expediee':'in_transit', 'annulee':'cancelled', 'retournee':'returned'}[status]
        total = 0
        # 1, 2 ou 3 produits distincts, soit exactement 600 lignes.
        for pid in rng.sample(list(prices), 1 + (i-1) % 3):
            qty = rng.randint(1, 3)
            cents = prices[pid]
            items.append(dict(order_item_id=f'ITM-{len(items)+1:04}', order_id=oid, product_id=pid,
                              quantity=qty, unit_price_mad=money(cents), line_total_mad=money(qty*cents)))
            total += qty*cents
        late = (actual > expected) if actual else (status in ('en_preparation', 'expediee') and REFERENCE > expected)
        orders.append(dict(order_id=oid, customer_id=f'CLI-{1+(i-1)%30:03}', order_date=day.isoformat(), order_status=status,
                           payment_status=payment, delivery_status=delivery, total_mad=money(total),
                           expected_delivery_date=expected.isoformat(), actual_delivery_date=actual.isoformat() if actual else '', is_delayed=str(late).lower()))
    faq = faq_rows()
    for name, rows in [('products',products), ('customers',customers), ('orders',orders), ('order_items',items), ('faq',faq)]:
        with (output / f'{name}.csv').open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
            writer.writeheader()
            writer.writerows(rows)
    (output / 'faq.md').write_text(render_faq(faq).rstrip() + '\n', encoding='utf-8', newline='\n')
    print(f'Génération : {len(products)} produits, {len(customers)} clients, {len(orders)} commandes, {len(items)} lignes, {len(faq)} FAQ ; seed={seed}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--seed', type=int, default=SEED)
    args = parser.parse_args()
    generate(args.output_dir, args.seed)
