import unittest,tempfile,os,sys,json,struct,zlib,threading,urllib.request,urllib.error,base64,shutil
from pathlib import Path
from unittest.mock import patch
TASK_DATA=tempfile.TemporaryDirectory();os.environ['BUBBLE_STUDIO_DATA']=TASK_DATA.name
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'app'))
import server
import autostart

def png(w=198,h=162):
 def chunk(tag,data):return struct.pack('>I',len(data))+tag+data+struct.pack('>I',zlib.crc32(tag+data)&0xffffffff)
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+bytes([253,245,229,255])*w)*h))+chunk(b'IEND',b'')
class StudioTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);server.PORT=cls.http.server_port
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.base=f'http://127.0.0.1:{server.PORT}'
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();TASK_DATA.cleanup()
 def setUp(self):shutil.rmtree(Path(TASK_DATA.name)/'imports',ignore_errors=True);shutil.rmtree(Path(TASK_DATA.name)/'builtins',ignore_errors=True);server.save({**json.loads(json.dumps(server.DEFAULT)),'builtinsInitialized':True});self.folder=Path(TASK_DATA.name)/'art';shutil.rmtree(self.folder,ignore_errors=True);self.folder.mkdir();(self.folder/'one.png').write_bytes(png());(self.folder/'two.png').write_bytes(png(160,120))
 def request(self,path,body=None,origin=True,language="zh"):
  headers={'Content-Type':'application/json','X-Bubble-Studio':'1','Accept-Language':language}
  if origin:headers['Origin']=self.base
  r=urllib.request.Request(self.base+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
  with urllib.request.urlopen(r) as response:return json.load(response)
 def connect(self):self.request('/api/folder',{'path':str(self.folder)});return self.request('/api/library')['items']
 def test_real_folder_and_independent_presets(self):
  items=self.connect();self.assertEqual(len(items),2);a,b=items;original=(self.folder/'one.png').read_bytes();c={**a['config'],'left':60,'right':120}
  self.request('/api/save',{'id':a['id'],'config':c});loaded=self.request('/api/library')['items'];self.assertEqual(loaded[0]['config']['left'],60);self.assertEqual(loaded[1]['config'],b['config']);self.assertEqual((self.folder/'one.png').read_bytes(),original)
 def test_apply_restore_and_export_no_private_path(self):
  a=self.connect()[0]
  with patch.object(server,'bridge',return_value={'connected':True,'matched':6}):
   self.assertEqual(self.request('/api/apply',{'id':a['id'],'config':a['config']})['status']['matched'],6)
   exported=self.request('/api/export');self.assertNotIn(TASK_DATA.name,json.dumps(exported));self.assertEqual(exported['active']['filename'],'one.png')
   self.request('/api/restore',{});self.assertIsNone(server.state()['active'])
 def test_apply_attempts_launch_when_app_is_disconnected(self):
  a=self.connect()[0]
  launch_result={'platform':'codex','state':'quit-required','message':'请先完全退出'}
  with patch.object(server,'bridge',return_value={'connected':False,'matched':0}),patch.object(server,'launch_platform',return_value=launch_result) as launch:
   result=self.request('/api/apply',{'id':a['id'],'config':a['config']})
   self.assertEqual(result['launch'],launch_result)
   self.assertEqual(server.state()['active']['id'],a['id'])
   launch.assert_called_once()
  with patch.object(server,'bridge',return_value={'connected':True,'matched':1}),patch.object(server,'launch_platform') as launch:
   result=self.request('/api/apply',{'id':a['id'],'config':a['config']})
   self.assertIsNone(result['launch'])
   launch.assert_not_called()
 def test_main_navigation_uses_public_gallery_without_owner_review_link(self):
  with urllib.request.urlopen(self.base) as response:page=response.read().decode()
  self.assertIn('https://kaitongg-bit.github.io/DIYcodex-bubble/',page)
  self.assertNotIn('href="/review"',page)
  self.assertIn('data-platform="codex"',page)
  self.assertIn('data-platform="doubao"',page)
  self.assertIn('id="onboarding"',page)
  self.assertIn('id="help"',page)
  self.assertIn('id="appsLauncher"',page)
  self.assertIn('id="autostart"',page)
  self.assertIn('id="revealLauncher"',page)
  self.assertIn('id="revealLauncherGuide"',page)
 def test_reveal_launcher_opens_file_manager_without_launching_apps(self):
  with patch.object(server.sys,'platform','darwin'),patch.object(server.subprocess,'run') as run:
   self.assertTrue(self.request('/api/reveal-launcher',{})['ok'])
   args=run.call_args.args[0]
   self.assertEqual(args[:2],['/usr/bin/open','-R'])
   self.assertTrue(args[2].endswith('Open Bubble Apps.app'))
  with patch.object(server.sys,'platform','win32'),patch.object(server.subprocess,'Popen') as popen:
   self.assertTrue(self.request('/api/reveal-launcher',{})['ok'])
   self.assertEqual(popen.call_args.args[0][0],'explorer.exe')
 def test_login_autostart_registration_is_per_user_and_reversible(self):
  with tempfile.TemporaryDirectory() as home:
   root=Path(home)/'studio';root.mkdir()
   path=autostart.item_path('darwin',home=home)
   self.assertFalse(autostart.enabled('darwin',home=home))
   self.assertTrue(autostart.configure(True,'darwin',home=home,python='/usr/bin/python3',root=root))
   content=path.read_bytes()
   self.assertIn(b'login-start.py',content)
   self.assertIn(b'RunAtLoad',content)
   self.assertFalse(autostart.configure(False,'darwin',home=home))
   self.assertFalse(path.exists())
   appdata=Path(home)/'AppData';path=autostart.item_path('win32',appdata=appdata)
   self.assertTrue(autostart.configure(True,'win32',appdata=appdata,python=Path(home)/'Python'/'python.exe',root=root))
   self.assertIn('login-start.py',path.read_bytes().decode('utf-16'))
   self.assertIn(', 0, False',path.read_bytes().decode('utf-16'))
   self.assertFalse(autostart.configure(False,'win32',appdata=appdata))
 def test_autostart_api_validates_boolean_and_origin(self):
  with patch.object(server,'autostart_enabled',return_value=False),patch.object(server,'configure_autostart',return_value=True) as configure:
   self.assertFalse(self.request('/api/autostart')['enabled'])
   self.assertTrue(self.request('/api/autostart',{'enabled':True})['enabled'])
   configure.assert_called_once_with(True)
   with self.assertRaises(urllib.error.HTTPError):self.request('/api/autostart',{'enabled':'yes'})
   with self.assertRaises(urllib.error.HTTPError):self.request('/api/autostart',{'enabled':False},origin=False)
 def test_fresh_install_selects_alien_cat_once_without_overwriting_user_choice(self):
  s=server.state();s['firstRunPending']=True;s['builtinsInitialized']=False;server.save(s)
  with patch.object(server,'configure_autostart',return_value=True) as enable:
   first=self.request('/api/first-run',{})
   self.assertTrue(first['firstRun']);self.assertTrue(first['autostartEnabled'])
   enable.assert_called_once_with(True)
  active=server.state()['platforms']['codex']['active']
  self.assertEqual(Path(active['path']).name,'alien-cat.png')
  self.assertEqual(active['config']['color'],'#ffffff')
  self.assertEqual(first['activeId'],active['id'])
  self.assertFalse(self.request('/api/first-run',{})['firstRun'])
  self.assertEqual(server.state()['platforms']['codex']['active'],active)
 def test_import_and_bad_png_rollback(self):
  result=self.request('/api/import',{'name':'import.png','data':base64.b64encode(png()).decode()});self.assertTrue(result['id']);before=len(server.library())
  with self.assertRaises(urllib.error.HTTPError):self.request('/api/import',{'name':'bad.png','data':base64.b64encode(b'bad').decode()})
  self.assertEqual(len(server.library()),before)
 def test_crossed_lines_rejected_and_origin_required(self):
  a=self.connect()[0];c={**a['config'],'left':150,'right':80}
  with self.assertRaises(urllib.error.HTTPError) as err:self.request('/api/apply',{'id':a['id'],'config':c})
  self.assertEqual(err.exception.code,400);self.assertIsNone(server.state()['active'])
  with self.assertRaises(urllib.error.HTTPError) as err:self.request('/api/folder',{'path':str(self.folder)},origin=False)
  self.assertEqual(err.exception.code,403)
 def test_large_png_defaults_fit_and_small_scale_radius_save(self):
  self.assertEqual(server.defaults(198,162)['scale'],.6)
  for w,h in [(420,210),(1000,500),(4096,4096)]:
   c=server.defaults(w,h)
   self.assertLessEqual(w*c['scale'],240.1)
   self.assertLessEqual(h*c['scale'],98.1)
  (self.folder/'large.png').write_bytes(png(1000,500))
  a=next(i for i in self.connect() if i['width']==1000)
  c={**a['config'],'scale':.05,'radius':24,'borderWidth':2.5,'borderColor':'#123456'}
  self.request('/api/save',{'id':a['id'],'config':c})
  saved=next(i for i in self.request('/api/library')['items'] if i['id']==a['id'])
  self.assertEqual(saved['config']['scale'],.05)
  self.assertEqual(saved['config']['radius'],24)
  self.assertEqual(saved['config']['borderWidth'],2.5)
  self.assertEqual(saved['config']['borderColor'],'#123456')
  for bad in ({**c,'scale':.001},{**c,'radius':-1},{**c,'radius':201},{**c,'borderWidth':21},{**c,'borderColor':'invalid'}):
   with self.assertRaises(urllib.error.HTTPError):self.request('/api/save',{'id':a['id'],'config':bad})
 def test_delete_undo_preserves_png_preset_and_active_restore(self):
  a=self.connect()[0];path=self.folder/'one.png';original=path.read_bytes()
  c={**a['config'],'radius':16}
  with patch.object(server,'bridge',return_value={'connected':True,'matched':2}) as bridge:
   self.request('/api/apply',{'id':a['id'],'config':c})
   deleted=self.request('/api/delete',{'id':a['id']})
   self.assertTrue(deleted['activeRemoved']);self.assertFalse(path.exists())
   self.assertIsNone(server.state()['active']);bridge.assert_called_with('restore','codex')
   library=self.request('/api/library');self.assertEqual(len(library['items']),1)
   self.assertEqual(library['trashCount'],1);self.assertNotIn(TASK_DATA.name,json.dumps(library['latestTrashId']))
   restored=self.request('/api/undo-delete',{'token':deleted['token']})
   self.assertEqual(restored['id'],a['id']);self.assertEqual(path.read_bytes(),original)
   self.assertEqual(server.state()['presets'][a['id']]['radius'],16)
   self.assertIsNone(server.state()['active']);self.assertEqual(self.request('/api/library')['trashCount'],0)
 def test_undo_delete_refuses_overwriting_and_unknown_id(self):
  a=self.connect()[0];deleted=self.request('/api/delete',{'id':a['id']})
  path=self.folder/'one.png';path.write_bytes(b'new file')
  with self.assertRaises(urllib.error.HTTPError):self.request('/api/undo-delete',{'token':deleted['token']})
  self.assertEqual(path.read_bytes(),b'new file');self.assertEqual(len(server.state()['trash']),1)
  with self.assertRaises(urllib.error.HTTPError):self.request('/api/delete',{'id':'arbitrary-path'})
 def test_native_folder_picker_and_cancel(self):
  from subprocess import CompletedProcess
  with patch.object(server.sys,'platform','darwin'),patch.object(server.subprocess,'run',return_value=CompletedProcess([],0,str(self.folder)+'\n','')) as run:
   self.request('/api/choose-folder',{},language='en')
   self.assertIn('Choose your bubble asset folder',run.call_args.args[0][2])
   self.assertEqual(len(self.request('/api/library')['items']),2)
   self.assertEqual(run.call_args.args[0][0],'/usr/bin/osascript')
  before=server.state()
  with patch.object(server,'choose_folder',return_value=''):
   self.assertTrue(self.request('/api/choose-folder',{})['cancelled'])
  self.assertEqual(server.state(),before)
 def test_windows_folder_picker(self):
  import types
  root=unittest.mock.Mock()
  fake=types.SimpleNamespace(Tk=lambda:root,filedialog=types.SimpleNamespace(askdirectory=lambda **kwargs:str(self.folder)))
  with patch.object(server.sys,'platform','win32'),patch.dict(sys.modules,{'tkinter':fake}):
   self.request('/api/choose-folder',{})
  root.withdraw.assert_called_once();root.destroy.assert_called_once()
  self.assertEqual(len(self.request('/api/library')['items']),2)
 def test_open_trash_and_external_removal(self):
  a=self.connect()[0];self.request('/api/delete',{'id':a['id']})
  entry=server.state()['trash'][0]
  self.assertTrue(Path(entry['stored']).name.endswith('-one.png'))
  with patch.object(server.sys,'platform','darwin'),patch.object(server.subprocess,'run') as run:
   self.request('/api/open-trash',{'path':'/untrusted'})
   self.assertEqual(run.call_args.args[0],['/usr/bin/open',str((server.DATA/'trash').resolve())])
  Path(entry['stored']).unlink()
  result=self.request('/api/library')
  self.assertEqual(result['trashCount'],0);self.assertIsNone(result['latestTrashId'])
 def test_windows_open_recovery_folder(self):
  with patch.object(server.sys,'platform','win32'),patch.object(server.os,'startfile',create=True) as open_folder:
   self.request('/api/open-trash',{})
   open_folder.assert_called_once_with(str((server.DATA/'trash').resolve()))
 def test_builtins_first_run_delete_and_explicit_restore(self):
  server.save(json.loads(json.dumps(server.DEFAULT)))
  items=self.request('/api/library')['items'];self.assertEqual(len(items),3)
  a=next(i for i in items if i['filename']=='alien-cat.png')
  bundled=server.ROOT/'presets/alien-cat.png';original=bundled.read_bytes()
  config={**a['config'],'radius':8}
  self.request('/api/save',{'id':a['id'],'config':config})
  self.request('/api/delete',{'id':a['id']})
  self.assertEqual(len(self.request('/api/library')['items']),2)
  self.assertEqual(bundled.read_bytes(),original)
  self.assertEqual(self.request('/api/restore-builtins',{})['added'],1)
  restored=next(i for i in self.request('/api/library')['items'] if i['id']==a['id'])
  self.assertEqual(restored['config']['radius'],8)
  self.assertEqual(self.request('/api/restore-builtins',{})['added'],0)
 def test_gallery_is_curated_and_download_count_is_real(self):
  self.connect();gallery=self.request('/api/gallery')
  self.assertEqual(len(gallery['items']),3);self.assertEqual(gallery['scope'],'local')
  self.assertNotIn(TASK_DATA.name,json.dumps(gallery));self.assertNotIn('one.png',json.dumps(gallery))
  before=next(i for i in gallery['items'] if i['id']=='love')['downloads']
  result=self.request('/api/gallery-download',{'id':'love'})
  self.assertEqual(result['downloads'],before+1)
  self.assertEqual(base64.b64decode(result['data']),(server.ROOT/'presets/love.png').read_bytes())
  self.assertEqual(next(i for i in self.request('/api/gallery')['items'] if i['id']=='love')['downloads'],before+1)
  with self.assertRaises(urllib.error.HTTPError):self.request('/api/gallery-download',{'id':'../server.py'})
 def test_platform_isolation_switch_restore_and_delete(self):
  a,b=self.connect()
  with patch.object(server,'bridge',return_value={'connected':True,'matched':1}) as bridge:
   self.request('/api/apply',{'id':a['id'],'config':a['config'],'platform':'codex'})
   self.request('/api/platform',{'platform':'doubao'})
   self.assertIsNone(self.request('/api/library')['activeId']);self.assertEqual(server.state()['debugPort'],19326)
   self.request('/api/apply',{'id':b['id'],'config':b['config'],'platform':'doubao'})
   bridge.assert_called_with('apply','doubao')
   with self.assertRaises(urllib.error.HTTPError):self.request('/api/restore',{'platform':'codex'})
   self.request('/api/restore',{'platform':'doubao'});bridge.assert_called_with('restore','doubao')
   self.assertEqual(server.state()['platforms']['codex']['active']['id'],a['id'])
   self.request('/api/apply',{'id':a['id'],'config':a['config'],'platform':'doubao'})
   self.request('/api/delete',{'id':a['id']})
   self.assertIsNone(server.state()['platforms']['codex']['active']);self.assertIsNone(server.state()['platforms']['doubao']['active'])
   self.assertIn(unittest.mock.call('restore','codex'),bridge.call_args_list)
   self.assertIn(unittest.mock.call('restore','doubao'),bridge.call_args_list)
   self.request('/api/platform',{'platform':'codex'});self.assertEqual(server.state()['debugPort'],19327)
 def test_legacy_state_migrates_to_codex_without_losing_settings(self):
  a=self.connect()[0];legacy={**json.loads(json.dumps(server.DEFAULT)),'active':{'id':a['id'],'path':a['path'] if 'path' in a else str(self.folder/'one.png'),'config':a['config'],'version':'legacy'},'presets':{a['id']:a['config']}}
  server.STATE.write_text(json.dumps(legacy));migrated=server.state()
  self.assertEqual(migrated['platforms']['codex']['active']['id'],a['id']);self.assertIsNone(migrated['platforms']['doubao']['active'])
  self.request('/api/platform',{'platform':'doubao'})
  self.assertEqual(server.state()['presets'][a['id']],a['config']);self.assertEqual(server.state()['platforms']['codex']['active']['version'],'legacy')
 def test_launch_uses_selected_platform_and_its_port(self):
  from subprocess import CompletedProcess
  exists=Path.exists
  for key,exe,port in [('doubao','/Applications/Doubao.app/Contents/MacOS/Doubao',19326),('codex','/Applications/ChatGPT.app/Contents/MacOS/ChatGPT',19327)]:
   self.request('/api/platform',{'platform':key})
   with patch.object(server.sys,'platform','darwin'),patch.object(Path,'exists',lambda p:str(p)==exe or exists(p)),patch.object(server.subprocess,'run',return_value=CompletedProcess([],1)) as run,patch.object(server.subprocess,'Popen') as launch:
    self.request('/api/launch',{'platform':key})
    self.assertEqual(launch.call_args.args[0],[exe,'--remote-debugging-address=127.0.0.1',f'--remote-debugging-port={port}'])
    self.assertEqual(run.call_args.args[0][0],'/bin/ps')
 def test_launch_active_starts_both_saved_apps_without_switching_platform(self):
  from subprocess import CompletedProcess
  s=server.state()
  for key in ('codex','doubao'):s['platforms'][key]['active']={'id':key,'path':str(self.folder/'one.png'),'config':server.defaults(198,162),'version':key}
  s['platform']='doubao';s['active']=s['platforms']['doubao']['active'];server.save(s)
  apps={'/Applications/ChatGPT.app/Contents/MacOS/ChatGPT','/Applications/Doubao.app/Contents/MacOS/Doubao'}
  exists=Path.exists
  with patch.object(server.sys,'platform','darwin'),patch.object(Path,'exists',lambda p:str(p) in apps or exists(p)),patch.object(server.subprocess,'run',return_value=CompletedProcess([],1)),patch.object(server.subprocess,'Popen') as launch:
   result=self.request('/api/launch-active',{})
   self.assertEqual([x['state'] for x in result['results']],['starting','starting'])
   self.assertEqual(len(launch.call_args_list),2)
   self.assertEqual({call.args[0][-1] for call in launch.call_args_list},{'--remote-debugging-port=19327','--remote-debugging-port=19326'})
  self.assertEqual(server.state()['platform'],'doubao')
 def test_running_app_without_debug_port_is_not_force_quit(self):
  from subprocess import CompletedProcess
  s=server.state();s['platforms']['doubao']['active']={'id':'doubao','path':str(self.folder/'one.png'),'config':server.defaults(198,162),'version':'test'};server.save(s)
  apps={'/Applications/ChatGPT.app/Contents/MacOS/ChatGPT','/Applications/Doubao.app/Contents/MacOS/Doubao'}
  exists=Path.exists
  with patch.object(server.sys,'platform','darwin'),patch.object(Path,'exists',lambda p:str(p) in apps or exists(p)),patch.object(server.subprocess,'run',return_value=CompletedProcess([],0,'/Applications/Doubao.app/Contents/MacOS/Doubao\n','')),patch.object(server,'bridge',return_value={'connected':False}),patch.object(server.subprocess,'Popen') as launch:
   result=self.request('/api/launch-active',{})
   self.assertEqual(result['results'][0]['state'],'quit-required')
   launch.assert_not_called()
 def test_windows_launch_and_running_app_never_force_quits(self):
  exe=self.folder/'ChatGPT.exe';exe.write_bytes(b'')
  self.request('/api/platform',{'platform':'codex'})
  with patch.object(server.sys,'platform','win32'),patch.dict(os.environ,{'BUBBLE_STUDIO_CODEX_EXE':str(exe)}),patch.object(server,'windows_running_names',return_value=set()),patch.object(server.subprocess,'Popen') as launch:
   self.request('/api/launch',{'platform':'codex'})
   self.assertEqual(launch.call_args.args[0],[str(exe),'--remote-debugging-address=127.0.0.1','--remote-debugging-port=19327'])
   self.assertIn('creationflags',launch.call_args.kwargs)
  with patch.object(server.sys,'platform','win32'),patch.dict(os.environ,{'BUBBLE_STUDIO_CODEX_EXE':str(exe)}),patch.object(server,'windows_running_names',return_value={'chatgpt.exe'}),patch.object(server,'bridge',return_value={'connected':False}),patch.object(server.subprocess,'Popen') as launch:
   result=self.request('/api/launch',{'platform':'codex'})
   self.assertEqual(result['state'],'quit-required')
   self.assertIn('任务栏',result['message'])
   launch.assert_not_called()
 def test_windows_store_discovery_uses_expected_publisher(self):
  from subprocess import CompletedProcess
  exe=self.folder/'Codex.exe';exe.write_bytes(b'')
  with patch.object(server.subprocess,'run',return_value=CompletedProcess([],0,str(exe)+'\n','')) as run:
   self.assertEqual(server.windows_store_apps('codex'),[exe])
   self.assertIn('Publisher',run.call_args.args[0][-1])
 def test_asset_route_cannot_read_arbitrary_path(self):
  with self.assertRaises(urllib.error.HTTPError) as err:self.request('/asset/../../app/server.py')
  self.assertEqual(err.exception.code,404)
if __name__=='__main__':unittest.main()
