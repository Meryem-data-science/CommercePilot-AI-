"""Contrats JSON et lecture locale stricte ; aucun chemin fourni par l'utilisateur."""
import csv
from datetime import date
from decimal import Decimal
from pathlib import Path
import re

DATA_DIR = Path(__file__).resolve().parents[2] / 'data'
REFERENCE = date(2026, 10, 1)
ROLES = ('client', 'analyste', 'administrateur')
NEUTRAL = 'Je ne peux pas consulter cette commande avec ce profil.'


def result(status, message, data=None):
    return {'status': status, 'message': message, 'data': data}


def invalid():
    return result('invalid_input', 'Paramètres invalides ou incomplets.')


def unavailable():
    return result('data_error', 'Les données sont temporairement indisponibles.')


def iso(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('date')
    return date.fromisoformat(value)


def money(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d+\.\d{2}', value):
        raise ValueError('montant')
    return Decimal(value)


def read_table(name, columns, key):
    with (DATA_DIR / name).open(encoding='utf-8', newline='') as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != columns:
            raise ValueError('schéma')
        rows = list(reader)
    if not rows:
        raise ValueError("table vide")
    ids = set()
    for row in rows:
        if None in row or any(v is None or not v.strip() for k,v in row.items() if k != 'actual_delivery_date'):
            raise ValueError('ligne')
        if row[key] in ids:
            raise ValueError('doublon')
        ids.add(row[key])
    return rows


def read_orders():
    rows = read_table('orders.csv', ['order_id','customer_id','order_date','order_status',
                     'payment_status','delivery_status','total_mad','expected_delivery_date',
                     'actual_delivery_date','is_delayed'], 'order_id')
    rules = {'livree':({'paid'},'delivered',True), 'retournee':({'refunded'},'returned',True),
             'annulee':({'unpaid'},'cancelled',False), 'en_preparation':({'paid','pending'},'not_shipped',False),
             'expediee':({'paid','pending'},'in_transit',False)}
    for row in rows:
        if not re.fullmatch(r'CMD-DEMO-\d{3}',row['order_id']) or not re.fullmatch(r'CLI-\d{3}',row['customer_id']):
            raise ValueError('identifiant')
        if row['order_status'] not in rules:
            raise ValueError('statut')
        payments, delivery, delivered = rules[row['order_status']]
        ordered, expected = iso(row['order_date']), iso(row['expected_delivery_date'])
        actual = iso(row['actual_delivery_date']) if row['actual_delivery_date'] else None
        if not (date(2026,4,1) <= ordered <= date(2026,9,30)) or (expected-ordered).days != 5:
            raise ValueError('chronologie')
        if bool(actual) != delivered or (actual and not ordered <= actual <= REFERENCE):
            raise ValueError('livraison')
        if row['payment_status'] not in payments or row['delivery_status'] != delivery or money(row['total_mad']) <= 0:
            raise ValueError('cohérence')
        late = actual > expected if actual else (row['order_status'] in ('en_preparation','expediee') and REFERENCE > expected)
        if row['is_delayed'] != str(late).lower():
            raise ValueError('retard')
    return rows


DATA_ERRORS = (OSError, UnicodeError, csv.Error, ValueError, KeyError, TypeError)
