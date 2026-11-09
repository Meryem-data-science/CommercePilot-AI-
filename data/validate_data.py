"""Validation indépendante des relations et règles des données AtlasShop."""
import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
import re
import sys

REFERENCE = date(2026, 10, 1)
START, END = date(2026, 4, 1), date(2026, 9, 30)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def amount(value):
    require(bool(re.fullmatch(r'\d+\.\d{2}', value)), f'Montant invalide : {value}')
    return Decimal(value)


def table(folder, name, key, count):
    with (folder / f'{name}.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    require(len(rows) == count, f'{name} : volume incorrect')
    require(all(r[key] for r in rows) and len({r[key] for r in rows}) == count, f'{name} : identifiants dupliqués ou vides')
    require(all(None not in r and all(v is not None for v in r.values()) for r in rows), f'{name} : ligne mal formée')
    return {r[key]: r for r in rows}


def validate(folder):
    products = table(folder, 'products', 'product_id', 50)
    customers = table(folder, 'customers', 'customer_id', 30)
    orders = table(folder, 'orders', 'order_id', 300)
    items = table(folder, 'order_items', 'order_item_id', 600)
    faq = table(folder, 'faq', 'source_id', 35)
    for p in products.values():
        require(amount(p['price_mad']) > 0 and int(p['stock']) >= 0, 'Prix ou stock invalide')
        require(p['availability'] == ('disponible' if int(p['stock']) > 0 else 'rupture'), 'Disponibilité incohérente')
        require(all(p[k].strip() for k in ('name','description','category')), 'Produit incomplet')
    require(all(c['city'].strip() for c in customers.values()), 'Ville manquante')
    sums = {oid: Decimal('0.00') for oid in orders}
    pairs = set()
    for item in items.values():
        oid, pid = item['order_id'], item['product_id']
        require(oid in orders and pid in products, f'Clé étrangère invalide : {oid}/{pid}')
        require((oid,pid) not in pairs, 'Produit dupliqué dans une commande')
        pairs.add((oid,pid))
        qty = int(item['quantity'])
        unit, total = amount(item['unit_price_mad']), amount(item['line_total_mad'])
        require(qty > 0 and unit > 0, 'Quantité ou prix non positif')
        require(unit == amount(products[pid]['price_mad']), 'Prix différent du catalogue figé')
        require(total == qty * unit, 'Montant de ligne incohérent')
        sums[oid] += total
    rules = {'livree':({'paid'},'delivered',True), 'retournee':({'refunded'},'returned',True),
             'annulee':({'unpaid'},'cancelled',False), 'en_preparation':({'paid','pending'},'not_shipped',False),
             'expediee':({'paid','pending'},'in_transit',False)}
    for oid, o in orders.items():
        require(o['customer_id'] in customers, f'Clé étrangère client invalide : {oid}')
        require(amount(o['total_mad']) == sums[oid] and sums[oid] > 0, f'Total incohérent : {oid}')
        require(o['order_status'] in rules, f'Statut inconnu : {oid}')
        payments, delivery, has_actual = rules[o['order_status']]
        require(o['payment_status'] in payments and o['delivery_status'] == delivery, f'Statuts incompatibles : {oid}')
        d = date.fromisoformat(o['order_date'])
        e = date.fromisoformat(o['expected_delivery_date'])
        a = date.fromisoformat(o['actual_delivery_date']) if o['actual_delivery_date'] else None
        require(START <= d <= END and (e-d).days == 5, f'Dates invalides : {oid}')
        require(bool(a) == has_actual, f'Date réelle incompatible : {oid}')
        if a:
            require(d <= a <= REFERENCE, f'Chronologie livraison : {oid}')
        late = a > e if a else (o['order_status'] in ('en_preparation','expediee') and REFERENCE > e)
        require(o['is_delayed'] == str(late).lower(), f'Retard incohérent : {oid}')
    for oid, cid, status in [('CMD-DEMO-001','CLI-001','livree'), ('CMD-DEMO-002','CLI-002','en_preparation'), ('CMD-DEMO-005','CLI-005','retournee')]:
        require(oid in orders and orders[oid]['customer_id'] == cid
                and orders[oid]['order_status'] == status, 'Référence stable perdue')
    require(len({r['question'].strip().casefold() for r in faq.values()}) == 35, 'FAQ répétée')
    require(len({r['answer'] for r in faq.values()}) == 35, 'Réponse FAQ répétée')
    require(len({r['category'] for r in faq.values()}) == 9, 'Couverture FAQ incorrecte')
    for r in faq.values():
        require(all(r[k].strip() for k in ('question','answer','category','source_id','version')), 'FAQ incomplète')
        require(r['version'] == '1.0', 'Version FAQ inconnue')
    expected = '# FAQ AtlasShop — règles entièrement fictives\n\n' + ''.join(
        f"## {r['source_id']} — {r['question']}\n\nCatégorie : {r['category']} | Version : {r['version']}\n\n{r['answer']}\n\n" for r in faq.values())
    require((folder/'faq.md').read_text(encoding='utf-8') == expected.rstrip() + '\n', 'FAQ Markdown différente du CSV')
    print('VALIDATION OK : 50 produits, 30 clients, 300 commandes, 600 lignes, 35 FAQ ; relations, montants, dates, statuts et retards cohérents.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    try:
        validate(args.data_dir)
    except (ValueError, KeyError, OSError, InvalidOperation, csv.Error) as error:
        print(f'VALIDATION ÉCHOUÉE : {error}', file=sys.stderr)
        sys.exit(1)
