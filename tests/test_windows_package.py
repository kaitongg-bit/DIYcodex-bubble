import importlib.util
import os
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
            with patch.object(start, 'ROOT', root), patch.object(start.sys, 'platform', 'win32'), patch.dict(os.environ, {'LOCALAPPDATA':str(profile)}, clear=True), patch.object(start, 'request', side_effect=[{}, {'results':[]}]) as request:
                start.main()
                self.assertEqual(Path(os.environ['BUBBLE_STUDIO_DATA']), profile / 'DIY Codex Bubble/Data')
                self.assertEqual(Path(os.environ['BUBBLE_STUDIO_NODE']), node)
                self.assertTrue((profile / 'DIY Codex Bubble/Data/login-start.log').exists())
                self.assertFalse((root / '.local').exists())
                request.assert_called_with('/api/launch-active', {})


if __name__ == '__main__':
    unittest.main()
