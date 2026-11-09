"""Contrôles des données synthétiques, sans outil métier ni appel externe."""
import csv
import hashlib
import os
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = Path(os.environ.get('ATLASSHOP_DATA_DIR', ROOT/'data'))
FILES = ('products.csv','customers.csv','orders.csv','order_items.csv','faq.csv','faq.md')


def run(script, *args):
    return subprocess.run([sys.executable, str(ROOT/'data'/script), *map(str,args)], capture_output=True, text=True)


class DataValidationTests(unittest.TestCase):
    def test_status_diversity_and_age(self):
        with (REFERENCE_DIR/'orders.csv').open(encoding='utf-8', newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(Counter(r['order_status'] for r in rows),
                         {'livree':210, 'en_preparation':24, 'expediee':36,
                          'annulee':18, 'retournee':12})
        by_client = defaultdict(set)
        for row in rows:
            by_client[row['customer_id']].add(row['order_status'])
        self.assertEqual(len(by_client), 30)
        self.assertTrue(all(len(statuses) >= 2 for statuses in by_client.values()))
        active = [r for r in rows if r['order_status'] in ('en_preparation', 'expediee')]
        self.assertTrue(all(1 <= (date(2026,10,1)-date.fromisoformat(r['order_date'])).days <= 12
                            for r in active))
        for status, count in [('en_preparation', 2), ('expediee', 6)]:
            self.assertEqual(sum(r['is_delayed']=='true' for r in active
                                 if r['order_status']==status), count)
        print('Réalisme contrôlé : 30 clients avec plusieurs statuts ; 60 commandes en cours récentes, dont 8 en retard.')

    def test_reproducibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            outputs = [Path(tmp)/n for n in ('a','b')]
            for out in outputs:
                result = run('generate_data.py','--output-dir',out)
                self.assertEqual(result.returncode, 0, result.stderr)
                result = run('validate_data.py','--data-dir',out)
                self.assertEqual(result.returncode, 0, result.stderr)
            for name in FILES:
                hashes = [hashlib.sha256((out/name).read_bytes()).hexdigest() for out in outputs]
                self.assertEqual(hashes[0], hashes[1], name)
                self.assertEqual(hashes[0], hashlib.sha256((REFERENCE_DIR/name).read_bytes()).hexdigest(), name)
                print(f'SHA-256 identique (2 sorties + référence) : {name} {hashes[0]}')
            result = run('generate_data.py','--output-dir',outputs[0])
            self.assertNotEqual(result.returncode, 0, 'Écrasement interdit')

    def test_corrupt_copies_rejected(self):
        cases = [
            ('orders.csv','customer_id','CLI-INEXISTANT','Clé étrangère client invalide'),
            ('order_items.csv','product_id','PRD-INEXISTANT','Clé étrangère invalide'),
            ('orders.csv','total_mad','0.01','Total incohérent'),
            ('orders.csv','payment_status','pending','Statuts incompatibles'),
            ('orders.csv','actual_delivery_date','2027-01-01','Chronologie livraison'),
            ('orders.csv','is_delayed','invalide','Retard incohérent'),
            ('products.csv','availability','invalide','Disponibilité incohérente'),
            ('order_items.csv','quantity','0','Quantité ou prix non positif'),
        ]
        for file, column, value, message in cases:
            with self.subTest(column=column), tempfile.TemporaryDirectory() as tmp:
                folder = Path(tmp)
                for name in FILES:
                    shutil.copyfile(REFERENCE_DIR/name,folder/name)
                with (folder/file).open(encoding='utf-8',newline='') as f:
                    reader = csv.DictReader(f)
                    fields, rows = reader.fieldnames, list(reader)
                rows[0][column] = value
                with (folder/file).open('w',encoding='utf-8',newline='') as f:
                    writer = csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
                    writer.writeheader()
                    writer.writerows(rows)
                result = run('validate_data.py','--data-dir',folder)
                self.assertEqual(result.returncode,1,result.stdout)
                self.assertIn(message,result.stderr)
                print(f'Copie altérée refusée : {column} — {result.stderr.strip()}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
