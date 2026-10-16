import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('public_export', Path(__file__).resolve().parents[1] / 'tools/export_public.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(shutil.which('git'), 'Git required to enumerate source files')
class PublicExportTests(unittest.TestCase):
    def _source_with_mixed_endings(self, parent):
        root = parent / 'source'
        root.mkdir()
        subprocess.run(['git', 'init', '-q', str(root)], check=True, capture_output=True)
        contents = {
            'LICENSE': b'Fixture license\r\n',
            'AGENTS.md': '# Agente de prueba\nLínea con ñ\n'.encode('utf-8'),
            'README.md': '# Documento de prueba\r\nLínea con ñ\r\n'.encode('utf-8'),
            'tools/bootstrap.py': b'# fixture\r\n',
            'templates/profile/candidate.md': b'# Generic private-profile skeleton\n',
            '.gitattributes': b'* text=auto eol=lf\n*.cmd text eol=crlf\n*.png binary\n*.gif binary\n',
            'start.cmd': b'@echo off\nrem fixture\r\n',
            'assets/sample.png': b'\x89PNG\r\n\x1a\n\0\r\n',
            # Valid UTF-8 bytes still belong to a declared binary file.
            'assets/sample.gif': b'GIF89a\r\nfixture\n',
        }
        for relative, data in contents.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        return root, contents

    def test_export_normalizes_utf8_text_and_preserves_declared_binary_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root, contents = self._source_with_mixed_endings(parent)
            output = parent / 'public.zip'
            manifest = module.export(root, output)
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.read('README.md'), contents['README.md'].replace(b'\r\n', b'\n'))
                self.assertEqual(archive.read('AGENTS.md'), contents['AGENTS.md'])
                self.assertEqual(archive.read('start.cmd'), b'@echo off\r\nrem fixture\r\n')
                for relative in ('assets/sample.png', 'assets/sample.gif'):
                    self.assertEqual(archive.read(relative), contents[relative])
                for relative, digest in manifest['files'].items():
                    self.assertEqual(hashlib.sha256(archive.read(relative)).hexdigest(), digest)
                self.assertEqual(json.loads(archive.read('PUBLIC-MANIFEST.json')), manifest)
            self.assertEqual(manifest['hash_basis'], 'archive-entry-bytes')
            self.assertEqual(manifest['line_endings'], {'utf8_text': 'LF', 'cmd': 'CRLF', 'binary': 'unchanged'})
            self.assertEqual((root / 'README.md').read_bytes(), contents['README.md'])

    def test_hash_and_archive_use_one_source_read_even_if_a_later_read_would_change(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root, contents = self._source_with_mixed_endings(parent)
            calls = {}
            original = Path.read_bytes

            def changing_read(path):
                calls[path] = calls.get(path, 0) + 1
                if path == root / 'README.md' and calls[path] > 1:
                    return b'changed-after-first-read\n'
                return original(path)

            output = parent / 'public.zip'
            with patch.object(Path, 'read_bytes', new=changing_read):
                manifest = module.export(root, output)
            self.assertEqual(calls, {root / relative: 1 for relative in contents})
            with zipfile.ZipFile(output) as archive:
                self.assertEqual(archive.read('README.md'), contents['README.md'].replace(b'\r\n', b'\n'))
                for relative, digest in manifest['files'].items():
                    self.assertEqual(hashlib.sha256(archive.read(relative)).hexdigest(), digest)

    def test_clean_git_clone_checkout_matches_the_export_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root, _ = self._source_with_mixed_endings(parent)
            output = parent / 'public.zip'
            manifest = module.export(root, output)
            published = parent / 'published'
            with zipfile.ZipFile(output) as archive:
                archive.extractall(published)
            subprocess.run(['git', 'init', '-q', str(published)], check=True, capture_output=True)
            subprocess.run(['git', '-c', 'core.autocrlf=false', 'add', '-A'], cwd=published, check=True, capture_output=True)
            subprocess.run(['git', '-c', 'user.name=Export Test', '-c', 'user.email=export-test@example.invalid',
                            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Export fixture'],
                           cwd=published, check=True, capture_output=True)
            cloned = parent / 'cloned'
            subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--quiet', str(published), str(cloned)],
                           check=True, capture_output=True)
            cloned_manifest = json.loads((cloned / 'PUBLIC-MANIFEST.json').read_text(encoding='utf-8'))
            self.assertEqual(cloned_manifest, manifest)
            for relative, digest in cloned_manifest['files'].items():
                with self.subTest(path=relative):
                    self.assertEqual(hashlib.sha256((cloned / relative).read_bytes()).hexdigest(), digest)

    def test_forced_tracked_private_files_never_leave_the_workspace(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = parent / 'source'
            root.mkdir()
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            public = ['LICENSE', 'AGENTS.md', 'README.md', 'tools/bootstrap.py', 'templates/profile/candidate.md']
            private = ['profile/candidate.md', '.runtime/runtime.local.json', 'documents/linkedin/profile.json',
                       'job_search_tracker.csv', 'cv/main_company_role.json', '.env', 'documents/applications/a/outcome.md',
                       'CLAUDE.md', '.claude/settings.json', 'work/audio-transcript.json', 'PUBLIC-MANIFEST.json']
            for relative in public + private:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('generic source' if relative in public else 'persona-privada@example.test', encoding='utf-8')
            subprocess.run(['git', 'add', '-A'], cwd=root, check=True)
            output = parent / 'public.zip'
            manifest = module.export(root, output)
            self.assertEqual(set(manifest['files']), set(public))
            with zipfile.ZipFile(output) as archive:
                combined = b'\n'.join(archive.read(n) for n in archive.namelist())
                self.assertNotIn(b'persona-privada', combined)
                self.assertFalse(json.loads(archive.read('PUBLIC-MANIFEST.json'))['profile_included'])

    def test_failed_export_preserves_previous_artifact(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            root = parent / 'source'
            root.mkdir()
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            output = parent / 'public.zip'
            output.write_bytes(b'previous-result')
            with self.assertRaises(ValueError):
                module.export(root, output)
            self.assertEqual(output.read_bytes(), b'previous-result')

    def test_path_escape_and_generated_files_are_rejected(self):
        for value in ('../profile.md', '/absolute.py', 'profile/x.md', 'PROFILE/private.md', '.RUNTIME/token.json', '.runtime/token.json', 'reports/demo.pdf', 'cv/main_x.pdf', '.env.prod', '.ENV.PROD', 'documents/cv/a.json'):
            with self.subTest(path=value):
                self.assertFalse(module.public_path(value))
        self.assertTrue(module.public_path('templates/profile/candidate.md'))
        self.assertTrue(module.public_path('.gitattributes'))
        self.assertTrue(module.public_path('.agents/skills/job-application-assistant/SKILL.md'))


if __name__ == '__main__':
    unittest.main()
