import unittest,tempfile,json,hashlib,sys,plistlib
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import updater
class Response:
 def __init__(self,data):self.data=data;self.offset=0
 def __enter__(self):return self
 def __exit__(self,*args):pass
 def read(self,n):value=self.data[self.offset:self.offset+n];self.offset+=len(value);return value
class UpdateTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'app';self.root.mkdir();self.data=Path(self.tmp.name)/'data';self.data.mkdir();self.u=updater.Updater(self.root,self.data)
 def tearDown(self):self.tmp.cleanup()
 def release(self):return {'tag_name':'v0.2.11','assets':[{'name':'DIYcodex-bubble-v0.2.11-windows-x64-light-setup.exe','size':3,'digest':'sha256:'+hashlib.sha256(b'abc').hexdigest(),'browser_download_url':'https://github.com/'+updater.REPO+'/releases/download/v0.2.11/DIYcodex-bubble-v0.2.11-windows-x64-light-setup.exe'}]}
 def test_version_check_and_source_download_fallback(self):
  with patch.object(updater.urllib.request,'urlopen',return_value=Response(json.dumps(self.release()).encode())):
   self.u.work('check')
  self.assertEqual(self.u.status()['state'],'available');self.assertFalse(self.u.status()['supported'])
  with self.assertRaises(ValueError):self.u.start('install')
 def test_invalid_digest_never_runs_installer(self):
  self.u.release=self.release()
  with patch.object(updater.sys,'platform','win32'),patch.object(updater.urllib.request,'urlopen',return_value=Response(b'bad')),patch.object(updater.subprocess,'Popen') as start:
   self.u.work('install');start.assert_not_called()
  self.assertEqual(self.u.status()['state'],'error');self.assertFalse(list((self.data/'updates').glob('*.part')))
 def test_verified_windows_update_runs_same_installation_and_keeps_data(self):
  self.u.release=self.release();(self.data/'state.json').write_text('personal settings')
  with patch.object(updater.sys,'platform','win32'),patch.object(updater.urllib.request,'urlopen',return_value=Response(b'abc')),patch.object(updater.subprocess,'Popen') as start:
   self.u.work('install')
  self.assertEqual(self.u.status()['state'],'installing');self.assertIn('/DIR='+str(self.root),start.call_args.args[0]);self.assertIn('/BUBBLEUPDATE=1',start.call_args.args[0]);self.assertEqual((self.data/'state.json').read_text(),'personal settings')
 def test_macos_swap_and_rollback_keep_personal_data(self):
  app=self.root/'DIY Codex Bubble.app';old=app/'Contents/Resources';old.mkdir(parents=True);(old/'marker').write_text('old')
  image=self.root/'image';source=image/'DIY Codex Bubble.app';(source/'Contents').mkdir(parents=True)
  (source/'Contents/Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier':'cc.kaitongg.diycodexbubble','CFBundleShortVersionString':'0.2.11'}));(source/'marker').write_text('new')
  (self.data/'updates').mkdir();(self.data/'state.json').write_text('settings');package=self.data/'updates/test.dmg';package.write_bytes(b'dmg')
  job={'root':str(old),'data':str(self.data),'package':str(package),'version':'0.2.11','pid':123}
  def run(args,**kwargs):
   if args[0]=='/usr/bin/open' and (app/'marker').exists():raise OSError('launch failed')
  with patch.object(updater.sys,'platform','darwin'),patch.object(updater.tempfile,'mkdtemp',return_value=str(image)),patch.object(updater.subprocess,'run',side_effect=run),patch.object(updater.os,'kill') as kill,patch.object(updater.time,'sleep'):
   updater.install(job);kill.assert_called_once_with(123,15)
  self.assertEqual((old/'marker').read_text(),'old');self.assertEqual((self.data/'state.json').read_text(),'settings');self.assertEqual(json.loads((self.data/'updates/result.json').read_text())['state'],'error')
