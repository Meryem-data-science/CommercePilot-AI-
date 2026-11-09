"""Recette Mock et distinction Git entre fast-forward et divergence, sans publication."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from deployment.check_local import main as local_smoke
from deployment.check_sync import inspect


class DeploymentFinalizationTests(unittest.TestCase):
    def prepare(self,folder):
        repo=Path(folder)
        def git(*args):
            return subprocess.check_output(['git',*args],cwd=repo,text=True,stderr=subprocess.STDOUT)
        git('init','-b','main')
        git('config','user.name','Synthetic test')
        git('config','user.email','test@example.invalid')
        (repo/'app.py').write_text('# synthetic fixture\n')
        git('add','app.py');git('commit','-m','base')
        git('branch','deployed')
        return repo,git

    def test_fast_forward_without_production_change(self):
        with tempfile.TemporaryDirectory() as folder:
            repo,git=self.prepare(folder)
            (repo/'notes.md').write_text('synthetic documentation\n')
            git('add','notes.md');git('commit','-m','documentation')
            before=git('rev-parse','deployed')
            result=inspect(repo,'deployed','main')
            self.assertTrue(result['fast_forward_possible'])
            self.assertEqual(result['deployed_only_commits'],0)
            self.assertEqual(result['main_only_commits'],1)
            self.assertEqual(result['production_asset_changes'],[])
            self.assertEqual(git('rev-parse','deployed'),before)

    def test_unique_commit_prevents_fast_forward_even_with_same_design(self):
        with tempfile.TemporaryDirectory() as folder:
            repo,git=self.prepare(folder)
            (repo/'main.md').write_text('synthetic main\n')
            git('add','main.md');git('commit','-m','main change')
            git('switch','deployed')
            (repo/'dev.txt').write_text('synthetic dev configuration\n')
            git('add','dev.txt');git('commit','-m','dev configuration')
            before=git('rev-parse','deployed')
            result=inspect(repo,'deployed','main')
            self.assertFalse(result['fast_forward_possible'])
            self.assertEqual((result['deployed_only_commits'],result['main_only_commits']),(1,1))
            self.assertEqual(result['production_asset_changes'],[])
            self.assertEqual(git('rev-parse','deployed'),before)

    def test_five_mock_paths_without_groq(self):
        with redirect_stdout(io.StringIO()):
            local_smoke()
        result=json.loads(Path('work/deployment/local_smoke.json').read_text())
        self.assertEqual(len(result['scenarios']),5)
        self.assertTrue(all(r['passed'] for r in result['scenarios']))
