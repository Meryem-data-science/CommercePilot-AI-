"""Agrégats par date de commande, états observés au 2026-10-01."""
from decimal import Decimal
from .common import REFERENCE, DATA_ERRORS, read_orders, iso, money, result, invalid, unavailable


def sales_summary(period, role):
    if not isinstance(role, str) or role not in ('analyste','administrateur'):
        return result('access_denied', 'Accès aux analyses commerciales refusé.')
    if not isinstance(period, dict) or set(period) != {'start_date','end_date'}:
        return invalid()
    try:
        start, end = iso(period['start_date']), iso(period['end_date'])
        if start > end:
            return invalid()
    except (TypeError, ValueError):
        return invalid()
    try:
        rows = [r for r in read_orders() if start <= iso(r['order_date']) <= end]
        totals = {k:Decimal('0.00') for k in ('ordered_amount_mad','paid_amount_mad','realized_revenue_mad','cancelled_amount_mad','returned_amount_mad')}
        counts = dict(order_count=len(rows), cancelled_count=0, returned_count=0, delivered_late_count=0, ongoing_late_count=0)
        for r in rows:
            amount = money(r['total_mad'])
            status = r['order_status']
            totals['ordered_amount_mad'] += amount
            if r['payment_status'] == 'paid':
                totals['paid_amount_mad'] += amount
            if status == 'livree' and r['payment_status'] == 'paid':
                totals['realized_revenue_mad'] += amount
            for value, prefix in [('annulee','cancelled'),('retournee','returned')]:
                if status == value:
                    counts[prefix+'_count'] += 1
                    totals[prefix+'_amount_mad'] += amount
            if r['is_delayed'] == 'true':
                counts['delivered_late_count' if status in ('livree','retournee') else 'ongoing_late_count'] += 1
        counts['delayed_count'] = counts['delivered_late_count'] + counts['ongoing_late_count']
        return result('ok', 'Aucune commande sur cette période.' if not rows else 'Synthèse disponible.',
                      {'period':dict(period), 'reference_date':REFERENCE.isoformat(), 'currency':'MAD',
                       **counts, **{k:format(v,'.2f') for k,v in totals.items()}})
    except DATA_ERRORS:
        return unavailable()
