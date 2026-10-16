import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('codex_runner', Path(__file__).resolve().parents[1] / 'tools/run.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def test_query_is_one_argument_and_filters_are_explicit(self):
        query = 'React "frontend"; $(dangerous) & literal'
        args = runner.search_args(query, 'remote', 5)
        self.assertEqual(args[args.index('--query') + 1], query)
        self.assertEqual(args[args.index('--country') + 1], 'AR')
        self.assertEqual(args[args.index('--remote') + 1], 'remote')
        self.assertEqual(args[args.index('--jobage') + 1], '14')

    def test_bad_config_path_falls_back_to_path(self):
        with patch.object(runner.shutil, 'which', return_value='/valid/codex'):
            self.assertEqual(runner.executable('codex', {'codex': '/no/such/codex'}), '/valid/codex')

    def test_no_bun_does_not_fake_search_success(self):
        with patch.object(runner, 'executable', return_value=None), patch.object(runner.subprocess, 'run') as call:
            self.assertEqual(runner.main(['search', '--query', 'backend']), 2)
            call.assert_not_called()

    def test_disabled_portal_stops_before_network_process(self):
        with patch.object(runner, 'executable', return_value='/bin/bun'), patch.object(runner, 'portal_enabled', return_value=False), patch.object(runner.subprocess, 'run') as call:
            self.assertEqual(runner.main(['search', '--query', 'backend']), 2)
            call.assert_not_called()

    def test_enabled_metadata_is_read_as_yaml(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = root / '.agents/skills/example/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text('---\nname: example\ndescription: test\nmetadata:\n  enabled: false\n---\n', encoding='utf-8')
            self.assertFalse(runner.portal_enabled('example', root))
            skill.write_text('---\nname: example\ndescription: test\nmetadata:\n  enabled: unknown\n---\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                runner.portal_enabled('example', root)

    def test_runtime_is_parsed_as_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.runtime').mkdir()
            (root / '.runtime/runtime.local.json').write_text('{"python":"literal;not-a-command"}', encoding='utf-8')
            self.assertEqual(runner.runtime(root)['python'], 'literal;not-a-command')

    def test_start_uses_argv_and_workspace(self):
        with patch.object(runner, 'executable', side_effect=lambda name, config, root=runner.ROOT: '/bin/' + name), patch.object(runner.subprocess, 'run') as call:
            call.return_value.returncode = 0
            self.assertEqual(runner.main(['start', '--prompt', 'mi pedido; literal']), 0)
            self.assertEqual(call.call_args.args[0][-1], 'mi pedido; literal')
            self.assertIn('--cd', call.call_args.args[0])
            self.assertNotIn('shell', call.call_args.kwargs)


if __name__ == '__main__':
    unittest.main()
