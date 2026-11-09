"""Projection sur liste blanche des résultats pour les journaux et artefacts CI."""
import argparse
import json
import math
import os
from pathlib import Path

GATES = ('tests_offline','atlasshop','ruff','coverage_measured','evaluation_thresholds',
         'evaluation_reproducible','reference_results_consistent','secret_scan','git_diff_check')


def number(value):
    # Les booléens et textes arbitraires ne doivent pas devenir des valeurs publiées.
    return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None


def project(data, outcome):
    indexed = {g['name']:g for g in data.get('gates', []) if isinstance(g, dict) and g.get('name') in GATES}
    statuses = {name:indexed.get(name, {}).get('passed') is True for name in GATES}
    def detail(name):
        value = indexed.get(name, {}).get('detail', {})
        return value if isinstance(value, dict) else {}
    tests = detail('tests_offline')
    coverage = detail('coverage_measured')
    evaluation = detail('evaluation_thresholds')
    measures = evaluation.get('metrics', {})
    def ratio(key):
        value = measures.get(key, {})
        return {part:number(value.get(part)) for part in ('numerator','denominator')}
    direct = evaluation.get('direct', {})
    result = {'outcome':'PASS' if outcome == 'success' and data.get('passed') is True and all(statuses.values()) else 'FAIL',
            'gates':statuses,
            'tests':{key:number(tests.get(key)) for key in ('run','failures','errors','skipped')},
            'coverage':{key:number(coverage.get(key)) for key in ('covered_lines','num_statements','covered_branches','num_branches','percent_covered')},
            'evaluation':{'scenario_successes':ratio('scenario_pass_rate'),
                          'direct_checks':{key:number(direct.get(key)) for key in ('numerator','denominator')},
                          'permission_violation_count':len(measures['permission_violations']) if isinstance(measures.get('permission_violations'),list) else None}}
    fields = list(result['tests'].values()) + list(result['coverage'].values())
    for value in result['evaluation'].values():
        fields.extend(value.values() if isinstance(value,dict) else [value])
    if any(value is None for value in fields):
        result['outcome'] = 'FAIL'
    return result


def load_fresh(report, marker, outcome):
    try:
        if not marker.exists() or report.stat().st_mtime_ns < marker.stat().st_mtime_ns:
            return project({}, outcome)
        return project(json.loads(report.read_text()), outcome)
    except (OSError, ValueError, TypeError, AttributeError, KeyError):
        return project({}, outcome)


def markdown(result):
    lines = ['# CommercePilot · '+result['outcome'], '',
             'Résultats de cette exécution uniquement. Tests hors ligne ; aucun appel réel Groq.', '',
             '| Quality gate | Verdict |','| --- | --- |']
    for name, ok in result['gates'].items():
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL / indisponible'} |")
    tests = result['tests']
    lines += ['',f"Tests : {tests['run']} exécutés ; {tests['failures']} échecs ; {tests['errors']} erreurs ; {tests['skipped']} ignorés."]
    c = result['coverage']
    for label, top, bottom in [('Lignes','covered_lines','num_statements'),('Branches','covered_branches','num_branches')]:
        value = f"{100*c[top]/c[bottom]:.2f} %" if c[top] is not None and c[bottom] else 'indisponible'
        lines.append(f'- {label} : {value}.')
    combined = f"{c['percent_covered']:.2f} %" if c['percent_covered'] is not None else 'indisponible'
    lines.append('- Couverture combinée de src/ : '+combined+'.')
    for name, value in result['evaluation'].items():
        if isinstance(value,dict):
            lines.append(f"- {name} : {value['numerator']}/{value['denominator']}.")
        else:
            lines.append(f'- {name} : {value}.')
    lines += ['', 'Référence : 45 scénarios, au moins 42 réussis, 28/28 contrôles directs, zéro violation.',
              'Les limites connues EV-010, EV-016 et EV-022 restent documentées dans evaluation/agent_report.md.',
              'Un FAIL ou une donnée indisponible impose une revue du step concerné. Reproduire avec python -m quality.check ;',
              'les diagnostics détaillés restent dans work/quality/ en local et ne sont pas téléversés.',
              'Les artefacts ne contiennent ni questions, ni réponses métier, ni traces individuelles, ni erreurs brutes.']
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outcome', default='failure')
    args = parser.parse_args()
    result = load_fresh(Path('evaluation/quality_results.json'),Path('work/ci/started'),args.outcome)
    directory = Path('work/ci');directory.mkdir(parents=True,exist_ok=True)
    text = markdown(result)
    (directory/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (directory/'summary.md').write_text(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as file:
            file.write(text)
    print(text)


if __name__ == '__main__':
    main()
