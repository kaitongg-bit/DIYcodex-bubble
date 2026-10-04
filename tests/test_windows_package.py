import importlib.util
import os
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class WindowsPackageTests(unittest.TestCase):
    def test_packaged_restore_uses_external_data_and_bundled_node(self):
        spec = importlib.util.spec_from_file_location('packaged_start', ROOT / 'scripts/login-start.py')
        start = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(start)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'Programs' / 'DIY Codex Bubble'
            node = root / 'runtime/node/node.exe'
            node.parent.mkdir(parents=True)
            node.touch()
            profile = Path(temporary) / 'UserData'
            with patch.object(start, 'ROOT', root), patch.object(start.sys, 'platform', 'win32'), patch.dict(os.environ, {'LOCALAPPDATA':str(profile)}, clear=True), patch.object(start, 'request', side_effect=[{'apiVersion':2,'instance':hashlib.sha256(os.path.normcase(str(root.resolve())).encode()).hexdigest()}, {'results':[]}]) as request:
                start.main()
                self.assertEqual(Path(os.environ['BUBBLE_STUDIO_DATA']), profile / 'DIY Codex Bubble/Data')
                self.assertEqual(Path(os.environ['BUBBLE_STUDIO_NODE']), node)
                self.assertTrue((profile / 'DIY Codex Bubble/Data/login-start.log').exists())
                self.assertFalse((root / '.local').exists())
                request.assert_called_with('/api/launch-active', {})


class ServiceIdentityTests(unittest.TestCase):
    def test_legacy_or_other_workshop_is_not_silently_reused(self):
        spec = importlib.util.spec_from_file_location('identity_start', ROOT / 'scripts/login-start.py')
        start = importlib.util.module_from_spec(spec);spec.loader.exec_module(start)
        for status in ({}, {'apiVersion':1}, {'apiVersion':2,'instance':'other-install'}):
            with self.subTest(status=status), patch.object(start.sys,'platform','win32'), patch.object(start,'request',return_value=status) as request, patch.object(start.subprocess,'Popen') as spawn, patch.object(start.webbrowser,'open') as browser:
                with self.assertRaisesRegex(RuntimeError,'旧工坊'):start.main(open_studio=True)
                request.assert_called_once_with('/api/status')
                spawn.assert_not_called();browser.assert_not_called()


class PackagedStartupTests(unittest.TestCase):
    def test_packaged_startup_uses_bootstrap_and_is_detected(self):
        import sys
        sys.path.insert(0, str(ROOT / 'app'))
        import autostart
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / 'Bubble'
            root.mkdir()
            (root / 'DIY Codex Bubble.exe').touch()
            content = autostart.item_content(platform='win32', root=root).decode('utf-16')
            self.assertIn('DIY Codex Bubble.exe', content)
            self.assertIn('--restore', content)
            self.assertNotIn('login-start.py', content)
            path = autostart.item_path(platform='win32', appdata=temporary)
            path.parent.mkdir(parents=True)
            path.write_bytes(content.encode('utf-16'))
            self.assertTrue(autostart.enabled(platform='win32', appdata=temporary))
            self.assertFalse(autostart.configure(False, platform='win32', appdata=temporary))


if __name__ == '__main__':
    unittest.main()
