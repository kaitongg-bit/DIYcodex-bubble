import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import windows_apps


class DiscoveryTests(unittest.TestCase):
    def test_direct_secondary_drive_executable_is_found(self):
        with tempfile.TemporaryDirectory() as directory:
            drive=Path(directory);exe=drive/'Doubao.exe';exe.touch()
            with patch.dict(os.environ,{},clear=True),patch.object(windows_apps,'local_drives',return_value=[drive]),patch.object(windows_apps,'registered_paths') as registered:
                self.assertEqual(windows_apps.find_candidates('doubao'),[exe])
                registered.assert_not_called()

    def test_versioned_installation_and_newest_version_first(self):
        with tempfile.TemporaryDirectory() as directory:
            drive=Path(directory)
            for version in ('1.9.0','1.10.0'):
                folder=drive/'Doubao/Application'/version;folder.mkdir(parents=True)
                (folder/'Doubao.exe').touch()
            with patch.dict(os.environ,{},clear=True),patch.object(windows_apps,'local_drives',return_value=[drive]):
                found=windows_apps.find_candidates('doubao')
            self.assertEqual(found[0].parent.name,'1.10.0')
            self.assertEqual(len(found),2)

    def test_registered_custom_path_and_installer_excluded(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            exe=folder/'Doubao.exe';exe.touch()
            installer=folder/'DoubaoOnlineInstaller_1.0.exe';installer.touch()
            with patch.dict(os.environ,{},clear=True),patch.object(windows_apps,'local_drives',return_value=[]),patch.object(windows_apps,'registered_paths',return_value=[installer,exe]):
                self.assertEqual(windows_apps.find_candidates('doubao'),[exe])

    def test_saved_location_precedes_discovery(self):
        with tempfile.TemporaryDirectory() as directory:
            exe=Path(directory)/'Doubao.exe';exe.touch()
            with patch.dict(os.environ,{},clear=True),patch.object(windows_apps,'local_drives',return_value=[]),patch.object(windows_apps,'registered_paths') as registered:
                self.assertEqual(windows_apps.find_candidates('doubao',str(exe)),[exe])
                registered.assert_not_called()

    def test_metadata_query_runs_successfully_on_windows(self):
        if os.name!='nt':
            self.skipTest('PowerShell metadata query needs Windows')
        original=subprocess.run
        results=[]
        def record(*args,**kwargs):
            result=original(*args,**kwargs);results.append(result);return result
        with patch.object(windows_apps.subprocess,'run',side_effect=record):
            self.assertEqual(windows_apps.registered_paths('doubao'),[])
        self.assertEqual(results[0].returncode,0,results[0].stderr)


if __name__=='__main__':
    unittest.main()
