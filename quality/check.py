"""Quality gates locaux : code de sortie non nul si un contrôle échoue."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from evaluation.agent_evaluation import load_cases, metrics, run

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / 'quality/baseline.json'


def evaluation_verdict(report, baseline):
    rows = report['scenarios']
    direct = report['deterministic_tool_validation']
    old = set(baseline['previously_passed'])
    passed = {r['id'] for r in rows if r['passed']}
    problems = []
    if len(rows) != baseline['minimum_scenarios'] or len({r['id'] for r in rows}) != 45:
        problems.append('scenario_count')
    if len(passed) < baseline['minimum_passed']:
        problems.append('minimum_successes')
    if old - passed:
        problems.append('previous_success_regressed')
    if direct['numerator'] != baseline['required_direct_passed'] or direct['denominator'] != 28:
        problems.append('direct_tools')
    if report['metrics'] != metrics(rows):
        problems.append('metric_mismatch')
    if report['metrics']['permission_violations'] or any(not r['checks']['permissions'] for r in rows):
        problems.append('permission_violation')
    return problems


def secret_issues(paths):
    """Détection limitée ; ne jamais retourner le contenu correspondant."""
    issues = []
    values = [v for k, v in os.environ.items() if len(v) > 12 and any(
        marker in k.upper() for marker in ('API_KEY', 'TOKEN', 'PASSWORD', 'SECRET'))]
    pattern = re.compile(r'(?:gsk_|ghp_|github_pat_)[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')
    for path in paths:
        path = Path(path)
        if not path.is_file():
            continue
        if (path.name == '.env' or path.name.startswith('.env.') and path.name != '.env.example'
                or path.name == 'secrets.toml' or path.suffix in ('.pem', '.key', '.p12', '.pfx')):
            issues.append({'file':path.name, 'reason':'sensitive_file'})
        # Pas de sortie de lignes ou valeurs, même sur erreur.
        data = path.read_bytes()
        if pattern.search(data.decode('utf-8', errors='replace')) or any(v.encode() in data for v in values):
            issues.append({'file':path.name, 'reason':'credential_pattern_or_environment_value'})
    return issues


def command(args, log):
    with log.open('w') as file:
        result = subprocess.run(args, cwd=ROOT, stdout=file, stderr=subprocess.STDOUT, check=False)
    return result.returncode == 0


def main():
    os.chdir(ROOT)
    work = ROOT / 'work/quality'
    work.mkdir(parents=True, exist_ok=True)
    baseline = json.loads(BASELINE.read_text())
    gates = []

    def add(name, ok, detail):
        gates.append({'name':name, 'passed':bool(ok), 'detail':detail})

    # Seuils figés dans baseline.json avant cette exécution ; pas d'ajustement automatique.
    tests_ok = command([sys.executable, '-m', 'coverage', 'run', '-m', 'quality.test_suite'], work/'tests.txt')
    test_file = work/'test_results.json'
    tests = json.loads(test_file.read_text()) if test_file.exists() else {}
    add('tests_offline', tests_ok and tests.get('run', 0) >= baseline['minimum_tests']
        and not tests.get('skipped', 0) and not tests.get('expected_failures', 0), tests)
    add('atlasshop', command([sys.executable, 'data/validate_data.py'], work/'data.txt'), 'Validateur officiel, données inchangées')
    add('ruff', command([sys.executable, '-m', 'ruff', 'check', '.'], work/'ruff.txt'),
        'Ruff 0.14.4 : E4, E9, F et règles de sécurité ciblées du pyproject.toml')
    coverage_ok = command([sys.executable, '-m', 'coverage', 'json', '-o', str(work/'coverage.json')], work/'coverage.txt')
    coverage = json.loads((work/'coverage.json').read_text()) if coverage_ok else {}
    add('coverage_measured', coverage_ok and coverage.get('totals', {}).get('num_statements', 0) > 0,
        coverage.get('totals', {}))
    try:
        load_cases()
        digest = hashlib.sha256((ROOT/'evaluation/scenarios.json').read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as folder:
            evaluation = run(folder)
            repeated = run(folder)
        anomalies = evaluation_verdict(evaluation, baseline)
        add('evaluation_thresholds', not anomalies and digest == baseline['scenario_sha256'],
            {'problems':anomalies, 'metrics':evaluation['metrics'], 'direct':evaluation['deterministic_tool_validation']})
        add('evaluation_reproducible', evaluation == repeated, 'Deux exécutions sans réseau, comparaison exacte')
        stored = json.loads((ROOT/'evaluation/agent_results.json').read_text())
        add('reference_results_consistent', stored == evaluation, 'Résultats versionnés non réécrits')
    except Exception:
        add('evaluation_thresholds', False, 'Évaluation invalide ; diagnostiquer localement sans exposer de contenu sensible')
    files = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).split(b'\0'))
    files |= set(subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '-z'], cwd=ROOT).split(b'\0'))
    issues = secret_issues([ROOT / os.fsdecode(f) for f in files if f])
    add('secret_scan', not issues, {'files_checked':len([f for f in files if f]), 'issues':issues})
    add('git_diff_check', command(['git', 'diff', '--check'], work/'diff.txt')
        and command(['git', 'diff', '--cached', '--check'], work/'diff-staged.txt'), 'Diff non indexé et indexé')
    result = {'scope':'local offline quality gates; not production or real Groq metrics',
              'versions':{'ruff':'0.14.4','coverage':'7.11.3'},
              'passed':all(g['passed'] for g in gates), 'gates':gates,
              'known_evaluation_failures':baseline['known_failures'],
              'coverage_by_module':{name:info['summary'] for name,info in coverage.get('files', {}).items()},
              'coverage_scope':'src uniquement ; couverture de branches incluse, sans seuil de pourcentage imposé'}
    dest = ROOT/'evaluation/quality_results.json'
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    text = '# Rapport qualité — tâche 8\n\nContrôles locaux, aucun appel Groq réel.\n\n'
    text += '| Quality gate | Verdict |\n| --- | --- |\n'
    for gate in gates:
        text += f"| {gate['name']} | {'RÉUSSI' if gate['passed'] else 'ÉCHEC'} |\n"
    text += '\n## Tests et couverture\n\n'+json.dumps(tests, ensure_ascii=False)+'\n\n'
    text += 'Couverture de `src/`, mesurée avec branches (hors app.py, scripts, tests et dépendances) :\n\n'
    text += '```json\n'+json.dumps(coverage.get('totals', {}), indent=2)+'\n```\n'
    text += '\n| Module | Couverture lignes + branches (%) |\n| --- | --- |\n'
    for name, info in coverage.get('files', {}).items():
        text += f"| {name} | {info['summary']['percent_covered']:.2f} |\n"
    text += '''
## Référence d'évaluation

Seuils fixés dans `quality/baseline.json` avant exécution : 45 scénarios, au moins 42 réussis,
28/28 contrôles directs, zéro violation. Chaque scénario précédemment réussi doit le rester.
L'empreinte du jeu interdit une modification silencieuse des annotations. Les résultats versionnés
et leurs métriques doivent correspondre à la nouvelle exécution, sans être réécrits par le gate.
EV-010 (recherche FAQ lexicale), EV-016 et EV-022 (complétude de paraphrases) restent les trois
échecs connus documentés. Les pannes attendues et correctement gérées sont des scénarios réussis.
Aucun score ne mesure le choix spontané de Groq ni le taux de panne en production.

## Anomalies et corrections

Ruff a initialement détecté six imports inutilisés dans quatre fichiers de tests.
Seuls ces imports ont été retirés ; aucun code métier n'a été corrigé ou reformaté.
Un premier essai des nouveaux tests a échoué sur une assertion du test de gate : une
violation hors du sous-ensemble sensible ne change pas nécessairement son agrégat,
mais doit toujours être bloquée globalement. L'assertion a été corrigée pour tester
ce cas précis ; aucun seuil ni comportement métier n'a été modifié.
Le style historique à points-virgules n'est pas soumis à un reformatage global.
Les limites fonctionnelles connues du benchmark ne sont pas corrigées dans cette tâche.

## Outils, reproductibilité et limites

Ruff 0.14.4 et coverage.py 7.11.3 sont fixés dans requirements-dev.txt. Les règles de lint et
sécurité ciblées figurent dans pyproject.toml ; ce n'est pas un audit de sécurité complet.
Les tests et l'évaluation bloquent les connexions socket ; les réponses SDK utilisent des transports
HTTP simulés. Les preuves détaillées sont dans work/quality/ (ignoré par Git), dont la couverture
par module et les sorties des commandes. Les résultats agrégés sont dans quality_results.json.
Le scanner examine les fichiers versionnés et non ignorés, sans imprimer les valeurs suspectes.
Il détecte des formats de clés, des fichiers sensibles et les secrets présents dans l'environnement,
mais ne garantit pas la détection de toute information confidentielle, clé encodée ou secret absent
de l'environnement. Les fichiers ignorés non publiés ne sont pas couverts.
La couverture est une mesure, sans seuil arbitraire ajouté après son calcul ; elle ne prouve pas
la qualité des assertions ni une sécurité exhaustive. Les erreurs de fournisseur et de journalisation
sont simulées, pas représentatives des incidents de production. Aucun CI distant, service payant,
Docker, GitHub Actions, commit ou push n'est ajouté. Tâche 9 non commencée.

Reproduction : `.venv/bin/python -m quality.check` après installation de requirements.txt et
requirements-dev.txt. Le code de sortie vaut 1 si un gate échoue, 0 sinon. Les preuves sont régénérées,
les artefacts de tâche 7 restent inchangés.
'''
    (ROOT/'evaluation/quality_report.md').write_text(text)
    for gate in gates:
        print(('PASS' if gate['passed'] else 'FAIL')+' '+gate['name'])
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
