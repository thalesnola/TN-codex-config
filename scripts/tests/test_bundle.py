"""Synthetic local bundle/install tests. Never reads the user's Codex configuration."""
from pathlib import Path
import hashlib
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('validate_bundle', ROOT / 'scripts/validate_bundle.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
POWERSHELL = shutil.which('powershell.exe')


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()} if root.exists() else {}


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='codex-config-test-')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.source = self.work / 'bundle'
        shutil.copytree(ROOT, self.source, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
        self.destination = self.work / 'destination'

    def mutate(self, relative, transform):
        path = self.source / relative
        path.write_text(transform(path.read_text(encoding='utf-8')), encoding='utf-8')

    def install(self, *args):
        if not POWERSHELL:
            self.skipTest('Windows PowerShell 5.1 is unavailable')
        return subprocess.run([POWERSHELL, '-NoProfile', '-NonInteractive', '-ExecutionPolicy',
                               'Bypass', '-File', str(self.source / 'scripts/Install-CodexConfig.ps1'),
                               '-Destination', str(self.destination), *args], capture_output=True)

    def test_valid_bundle(self):
        validator.validate(self.source)

    def test_missing_policy_rejected_in_every_consumer(self):
        policy = (self.source / 'policy/confidentiality.md').read_text(encoding='utf-8').strip()
        for relative in validator.POLICY_CONSUMERS:
            path = self.source / relative
            original = path.read_text(encoding='utf-8')
            with self.subTest(relative=relative):
                path.write_text(original.replace(policy, ''), encoding='utf-8')
                with self.assertRaisesRegex(ValueError, 'Missing or altered'):
                    validator.validate(self.source)
            path.write_text(original, encoding='utf-8')

    def test_canonical_tampering_rejected(self):
        self.mutate('policy/confidentiality.md', lambda text: text + '\nChanged policy\n')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            validator.validate(self.source)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertFalse(self.destination.exists())

    def test_contradictory_permission_rejected_before_writes(self):
        self.mutate('AGENTS.md', lambda text: text + '\nDados indicados estao disponiveis a qualquer modelo.\n')
        with self.assertRaisesRegex(ValueError, 'Contradictory'):
            validator.validate(self.source)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertFalse(self.destination.exists())

    def test_missing_policy_rejected_before_writes_even_optimized(self):
        self.mutate('AGENTS.md', lambda text: text.replace('Nenhum subagente', 'Qualquer subagente'))
        result = subprocess.run([sys.executable, '-O', str(self.source / 'scripts/validate_bundle.py')], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        for args in [(), ('-WhatIf',)]:
            self.assertNotEqual(self.install(*args).returncode, 0)
            self.assertFalse(self.destination.exists())

    def test_agent_policy_outside_instructions_rejected(self):
        policy = (self.source / 'policy/confidentiality.md').read_text(encoding='utf-8').strip()
        # Keep a complete copy in TOML comments; it must be inside developer_instructions.
        self.mutate('agents/astra-planner.toml', lambda text: text.replace(policy, '') + '\nextra = """\n' + policy + '\n"""\n')
        with self.assertRaisesRegex(ValueError, 'Missing instructions policy'):
            validator.validate(self.source)
        self.assertNotEqual(self.install().returncode, 0)
        self.assertFalse(self.destination.exists())

    def test_whatif_has_no_mutations(self):
        self.assertEqual(self.install('-WhatIf').returncode, 0)
        self.assertFalse(self.destination.exists())

    def test_override_rejected_without_mutating_destination(self):
        self.destination.mkdir()
        (self.destination / 'AGENTS.override.md').write_text('synthetic override', encoding='utf-8')
        (self.destination / 'AGENTS.md').write_text('synthetic instructions', encoding='utf-8')
        before = snapshot(self.destination)
        result = self.install()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b'AGENTS.override.md', result.stderr)
        self.assertEqual(snapshot(self.destination), before)

    def test_install_twice_preserves_config_auth_and_verified_backups(self):
        self.destination.mkdir()
        for name, text in [('config.toml', 'synthetic_config = true\n'),
                           ('auth.json', '{"synthetic": true}\n'),
                           ('AGENTS.md', 'synthetic prior instructions\n')]:
            (self.destination / name).write_text(text, encoding='utf-8')
        before = snapshot(self.destination)
        first = self.install()
        self.assertEqual(first.returncode, 0, first.stderr)
        installed = snapshot(self.destination)
        for name in ('config.toml', 'auth.json'):
            self.assertEqual(installed[name], before[name])
        backups = list((self.destination / 'backups').iterdir())
        self.assertEqual(len(backups), 1)
        self.assertEqual(snapshot(backups[0]), {'AGENTS.md': before['AGENTS.md']})
        second = self.install()
        self.assertEqual(second.returncode, 0, second.stderr)
        after = snapshot(self.destination)
        for name, digest in installed.items():
            self.assertEqual(after[name], digest)
        backups_after = set((self.destination / 'backups').iterdir())
        new_backup = (backups_after - set(backups)).pop()
        expected = {name: digest for name, digest in installed.items()
                    if name not in ('config.toml', 'auth.json') and not name.startswith('backups/')}
        self.assertEqual(snapshot(new_backup), expected)
        self.assertEqual((self.destination / 'AGENTS.md').read_bytes(), (self.source / 'AGENTS.md').read_bytes())


if __name__ == '__main__':
    unittest.main()
