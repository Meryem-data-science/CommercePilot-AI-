"""Inspection Git locale, sans fetch, merge, commit ou modification des références."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PROTECTED = ['app.py','src/presentation.py','.streamlit','requirements.txt','data']


def inspect(repository=ROOT, deployed='origin/feat/streamlit-interface', target='origin/main'):
    def git(*args):
        return subprocess.check_output(['git',*args],cwd=repository,text=True).strip()
    old=git('rev-parse','--verify','--end-of-options',deployed+'^{commit}')
    new=git('rev-parse','--verify','--end-of-options',target+'^{commit}')
    ahead,behind=map(int,git('rev-list','--left-right','--count',old+'...'+new).split())
    ancestry=subprocess.run(['git','merge-base','--is-ancestor',old,new],cwd=repository,check=False)
    if ancestry.returncode not in (0,1):
        raise RuntimeError('Vérification d’ascendance impossible')
    return {'deployed_commit':old,'main_commit':new,'deployed_only_commits':ahead,
            'main_only_commits':behind,'fast_forward_possible':ancestry.returncode==0,
            'production_asset_changes':git('diff','--name-only',old,new,'--',*PROTECTED).splitlines(),
            'deployed_only_commit_subjects':git('log','--format=%s',new+'..'+old).splitlines()}


if __name__=='__main__':
    print(json.dumps(inspect(),ensure_ascii=False,indent=2))
