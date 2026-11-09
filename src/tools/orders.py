"""Suivi en lecture seule ; rôle et identité de démonstration fournis par l'appelant."""
import re
from .common import ROLES, NEUTRAL, DATA_ERRORS, read_orders, result, invalid, unavailable


def get_order_status(order_id, role, customer_id):
    if not isinstance(role, str) or role not in ROLES:
        return invalid()
    if not isinstance(order_id, str) or not re.fullmatch(r'CMD-DEMO-\d{3}', order_id):
        return invalid()
    if role == 'analyste':
        return result('access_denied', NEUTRAL)
    if role == 'client' and (not isinstance(customer_id, str) or not re.fullmatch(r'CLI-\d{3}',customer_id)):
        return invalid()
    if role == 'administrateur' and customer_id is not None:
        return invalid()
    try:
        rows = read_orders()
        row = next((r for r in rows if r['order_id'] == order_id), None)
        if row is None or (role == 'client' and row['customer_id'] != customer_id):
            return result('access_denied', NEUTRAL)
        return result('ok', 'Suivi disponible.', {k:row[k] for k in
                      ('order_id','order_status','delivery_status','expected_delivery_date','actual_delivery_date')})
    except DATA_ERRORS:
        return unavailable()
