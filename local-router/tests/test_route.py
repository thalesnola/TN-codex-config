"""Behavioral routing tests; no task content or external calls."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RouteTests(unittest.TestCase):
    def run_route(self, *args):
        result = subprocess.run([sys.executable, str(ROOT / 'route.py'), *args],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_cloud_specialties(self):
        cases = [('planning', 'astra-planner', 'gpt-6-astra'),
                 ('architecture', 'astra-planner', 'gpt-6-astra'),
                 ('implementation', 'sol-executor', 'gpt-6.1-sol'),
                 ('testing', 'sol-executor', 'gpt-6.1-sol'),
                 ('debug', 'sol-executor', 'gpt-6.1-sol'),
                 ('review', 'sol-reviewer', 'gpt-6.1-sol'),
                 ('triage', 'controller', 'gpt-6-luna'),
                 ('extraction', 'controller', 'gpt-6-luna'),
                 ('visual', 'terra-visual', 'gpt-6.1-terra'),
                 ('writing', 'terra-visual', 'gpt-6.1-terra'),
                 ('computer-use', 'terra-visual', 'gpt-6.1-terra')]
        for task, agent, model in cases:
            with self.subTest(task=task):
                d = self.run_route('--task', task)
                self.assertEqual((d['status'], d['agent'], d['model']),
                                 ('selected', agent, model))
                self.assertFalse(d['dispatched'])

    def test_complex_extraction_requires_sol(self):
        d = self.run_route('--task', 'extraction', '--complexity', 'complex')
        self.assertEqual(d['agent'], 'sol-executor')

    def test_small_cloud_code_stays_with_controller(self):
        d = self.run_route('--task', 'implementation', '--complexity', 'small')
        self.assertEqual((d['agent'], d['model']), ('controller', 'gpt-6-luna'))

    def test_small_local_code_selects_dsh(self):
        d = self.run_route('--task', 'implementation', '--scope', 'local', '--complexity', 'small')
        self.assertEqual((d['agent'], d['model'], d['destination']),
                         ('dsh', 'gpt-oss:20b', 'local'))

    def test_compatibility_flags_do_not_restrict_cloud(self):
        for task, agent in [('planning', 'astra-planner'), ('implementation', 'sol-executor')]:
            d = self.run_route('--task', task, '--restricted', '--scope', 'cloud')
            self.assertEqual(d['agent'], agent)
            self.assertFalse(d['cloud_forbidden'])

    def test_volume_boundaries(self):
        for flag, threshold in [('--total-bytes', 1048576), ('--largest-file-bytes', 524288), ('--files', 5), ('--items', 5)]:
            for n, destination in [(threshold-1, 'cloud'), (threshold, 'local'), (threshold+1, 'local')]:
                with self.subTest(flag=flag, n=n):
                    d = self.run_route('--task', 'extraction', flag, str(n))
                    self.assertEqual(d['destination'], destination)
                    self.assertEqual(d['agent'], 'qwen' if destination == 'local' else 'controller')

    def test_investigation_of_supplied_collection(self):
        d = self.run_route('--task', 'investigation', '--acervo')
        self.assertEqual(d['agent'], 'opencode')

    def test_collection_batch_is_available_to_qwen(self):
        d = self.run_route('--task', 'batch', '--items', '5', '--acervo')
        self.assertEqual(d['agent'], 'qwen')

    def test_planning_volume_still_selects_astra(self):
        d = self.run_route('--task', 'planning', '--total-bytes', '1048576')
        self.assertEqual(d['agent'], 'astra-planner')
        self.assertTrue(d['compact_context_required'])
        self.assertEqual(d['preparation'], 'local_chunking_or_index')
        self.assertEqual(d['cloud_input'], 'compact_summary_only')

    def test_binary_volume_requires_local_preprocessing(self):
        d = self.run_route('--task', 'summarization', '--total-bytes', '1048576', '--input-kind', 'binary')
        self.assertEqual((d['status'], d['model']), ('needs_preprocessing', None))
        self.assertTrue(d['preprocessing_required'])

    def test_explicit_cloud_overrides_volume_preference(self):
        d = self.run_route('--task', 'extraction', '--items', '5', '--scope', 'cloud')
        self.assertEqual(d['agent'], 'controller')
        self.assertTrue(d['compact_context_required'])
        self.assertEqual(d['preparation'], 'local_chunking_or_index')
        self.assertEqual(d['cloud_input'], 'compact_summary_only')

    def test_large_specialist_tasks_keep_cloud_with_local_preparation(self):
        for task, agent in [('review', 'sol-reviewer'), ('visual', 'terra-visual'), ('writing', 'terra-visual'), ('computer-use', 'terra-visual')]:
            d = self.run_route('--task', task, '--total-bytes', '1048576')
            self.assertEqual(d['agent'], agent)
            self.assertEqual(d['preparation'], 'local_chunking_or_index')
            self.assertEqual(d['cloud_input'], 'compact_summary_only')

    def test_unsupported_local_has_no_fallback(self):
        for task in ['architecture', 'visual', 'computer-use', 'review']:
            d = self.run_route('--task', task, '--scope', 'local')
            self.assertEqual((d['status'], d['destination'], d['model']), ('unsupported', 'local', None))
            self.assertTrue(d['cloud_forbidden'])

    def test_complex_local_code_is_unsupported(self):
        d = self.run_route('--task', 'implementation', '--complexity', 'complex', '--scope', 'local')
        self.assertEqual(d['status'], 'unsupported')

    def test_search_and_summary_defaults(self):
        for task in ['search', 'summarization']:
            self.assertEqual(self.run_route('--task', task)['agent'], 'controller')

    def test_rejects_invalid_metadata(self):
        for args in [('--task', 'unknown'), ('--task', 'triage', '--items', '0'),
                     ('--task', 'triage', '--prompt', 'not accepted'), ('--task', 'batch', '--total-bytes', '-1'), ('--task', 'batch', '--files', '-1'), ('--task', 'batch', '--input-kind', 'unknown'), ('--task', 'batch', '--total-bytes', '10', '--largest-file-bytes', '524288')]:
            result = subprocess.run([sys.executable, str(ROOT / 'route.py'), *args], capture_output=True)
            self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main()
