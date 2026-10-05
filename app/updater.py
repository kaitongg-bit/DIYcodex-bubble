"""Explicit updates from this project's GitHub Releases; user data stays outside the app."""
from pathlib import Path
import hashlib,json,os,plistlib,re,shutil,subprocess,sys,tempfile,threading,time,urllib.request
VERSION='0.2.12'
REPO='kaitongg-bit/DIYcodex-bubble'
API='https://api.github.com/repos/'+REPO+'/releases/latest'
class Updater:
 def __init__(self,root,data):
  self.root=Path(root);self.data=Path(data);self.lock=threading.Lock();self.job=None
  self.info={'state':'idle','current':VERSION};self.release=None
 def status(self):
  with self.lock:
   result=dict(self.info)
  marker=self.data/'updates/result.json'
  if result['state']=='installing' and marker.exists():
   try:result.update(json.loads(marker.read_text()))
   except (OSError,ValueError):pass
  return result
 def installed(self):
  if sys.platform=='win32':return (self.root/'unins000.exe').is_file()
  return sys.platform=='darwin' and self.root.name=='Resources' and self.root.parent.name=='Contents' and self.root.parent.parent.suffix=='.app' and os.access(self.root.parent.parent.parent,os.W_OK)
 def start(self,action):
  with self.lock:
   if self.info['state'] in ('checking','downloading','installing') or (self.job and self.job.is_alive()):raise ValueError('正在检查或更新，请稍候')
   if action=='install' and (self.info['state']!='available' or not self.installed()):raise ValueError('请先检查更新；自动更新仅支持已安装的应用')
   self.info={'state':'checking' if action=='check' else 'downloading','current':VERSION}
   self.job=threading.Thread(target=self.work,args=(action,),daemon=True);self.job.start()
  return self.status()
 def set(self,**values):
  with self.lock:self.info.update(values)
 def work(self,action):
  try:
   if action=='check':
    # Only our own cached update packages are removed; never touch user assets.
    folder=self.data/'updates'
    for pattern in ('DIYcodex-bubble-*.exe','DIYcodex-bubble-*.dmg','DIYcodex-bubble-*.part'):
     for old in folder.glob(pattern):
      try:old.unlink()
      except OSError:pass
    request=urllib.request.Request(API,headers={'Accept':'application/vnd.github+json','User-Agent':'DIY-Codex-Bubble-Updater'})
    with urllib.request.urlopen(request,timeout=20) as response:
     raw=response.read(1024*1024+1)
    if len(raw)>1024*1024:raise ValueError('更新信息过大')
    release=json.loads(raw);tag=release['tag_name'];match=re.fullmatch(r'v(\d+)\.(\d+)\.(\d+)',tag)
    if not match or release.get('prerelease') or release.get('draft'):raise ValueError('更新版本信息无效')
    self.release=release;newer=tuple(map(int,match.groups()))>tuple(map(int,VERSION.split('.')))
    self.set(state='available' if newer else 'latest',latest=tag[1:],supported=self.installed(),url='https://github.com/'+REPO+'/releases/latest')
    return
   release=self.release;tag=release['tag_name']
   name='DIYcodex-bubble-macos.dmg' if sys.platform=='darwin' else 'DIYcodex-bubble-'+tag+'-windows-x64-light-setup.exe'
   asset=next((a for a in release['assets'] if a['name']==name),None)
   if not asset:raise ValueError('此版本尚无适用的安装包')
   digest=asset.get('digest','')
   if not re.fullmatch(r'sha256:[0-9a-f]{64}',digest):raise ValueError('安装包缺少 SHA-256 校验信息，请到发布页下载')
   url=asset['browser_download_url'];prefix='https://github.com/'+REPO+'/releases/download/'+tag+'/'
   if url!=prefix+name:raise ValueError('安装包地址无效')
   if not 0<asset['size']<200*1024*1024:raise ValueError('安装包大小无效')
   folder=self.data/'updates';folder.mkdir(exist_ok=True)
   package=folder/name;temporary=folder/(name+'.part');total=0;checksum=hashlib.sha256()
   try:
    with urllib.request.urlopen(url,timeout=30) as response,temporary.open('wb') as target:
     while True:
      block=response.read(256*1024)
      if not block:break
      total+=len(block)
      if total>asset['size']:raise ValueError('安装包大小不匹配')
      checksum.update(block);target.write(block);self.set(progress=round(total/asset['size']*100))
    if total!=asset['size'] or checksum.hexdigest()!=digest[7:]:raise ValueError('安装包校验失败，未进行安装')
    temporary.replace(package)
   finally:temporary.unlink(missing_ok=True)
   if sys.platform=='win32':
    self.set(state='installing',progress=100)
    subprocess.Popen([str(package),'/SILENT','/NORESTART','/BUBBLEUPDATE=1','/DIR='+str(self.root)])
    return
   helper=Path(tempfile.mkdtemp(prefix='bubble-update-'))/'helper.py';shutil.copy2(__file__,helper)
   job={'root':str(self.root),'data':str(self.data),'package':str(package),'version':tag[1:],'pid':os.getpid()}
   jobfile=helper.with_suffix('.json');jobfile.write_text(json.dumps(job),encoding='utf-8')
   (folder/'result.json').unlink(missing_ok=True)
   self.set(state='installing',progress=100)
   options={'creationflags':0x08000000} if sys.platform=='win32' else {'start_new_session':True}
   subprocess.Popen([sys.executable,str(helper),str(jobfile)],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,**options)
  except Exception as error:self.set(state='error',error=str(error))
def install(job):
 root=Path(job['root']);data=Path(job['data']);package=Path(job['package']);result=data/'updates/result.json'
 backup=None;mount=None;stage=None;app=None;swapped=False
 try:
  if sys.platform=='win32':
   subprocess.run([str(package),'/SILENT','/NORESTART','/DIR='+str(root)],check=True)
   result.write_text(json.dumps({'state':'completed','latest':job['version']}))
   subprocess.Popen([str(root/'DIY Codex Bubble.exe')])
  else:
   app=root.parent.parent
   mount=Path(tempfile.mkdtemp(prefix='bubble-dmg-'))
   subprocess.run(['hdiutil','attach','-nobrowse','-readonly','-mountpoint',str(mount),str(package)],check=True,capture_output=True)
   source=mount/'DIY Codex Bubble.app'
   with (source/'Contents/Info.plist').open('rb') as file:metadata=plistlib.load(file)
   if metadata.get('CFBundleIdentifier')!='cc.kaitongg.diycodexbubble' or metadata.get('CFBundleShortVersionString')!=job['version']:raise ValueError('应用版本不匹配')
   stage=app.parent/('.bubble-update-'+str(os.getpid())+'.app');shutil.copytree(source,stage)
   # Only the server which initiated this update is stopped, not Codex or Doubao.
   os.kill(job['pid'],15);time.sleep(.5)
   backup=app.with_name('.bubble-previous-'+str(os.getpid())+'.app');app.rename(backup);stage.rename(app);swapped=True
   subprocess.run(['/usr/bin/open',str(app)],check=True)
   result.write_text(json.dumps({'state':'completed','latest':job['version']}))
   try:shutil.rmtree(backup);backup=None
   except OSError:pass
  try:package.unlink(missing_ok=True)
  except OSError:pass
 except Exception as error:
  if backup and backup.exists():
   if swapped and app.exists():shutil.rmtree(app)
   backup.rename(app)
   subprocess.run(['/usr/bin/open',str(app)],capture_output=True)
  result.write_text(json.dumps({'state':'error','error':str(error)}))
 finally:
  if stage and stage.exists():shutil.rmtree(stage)
  if mount:
   subprocess.run(['hdiutil','detach',str(mount)],capture_output=True)
   try:mount.rmdir()
   except OSError:pass
if __name__=='__main__':install(json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')))
