#!/usr/bin/env python3
"""Local PNG library + nine-slice editor + Codex appearance bridge. No cloud calls."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from pathlib import Path
import json,struct,hashlib,base64,subprocess,shutil,os,threading,time,argparse,uuid,sys
from autostart import enabled as autostart_enabled, configure as configure_autostart
ROOT=Path(__file__).resolve().parent.parent
DATA=Path(os.environ.get('BUBBLE_STUDIO_DATA',str(ROOT/'.local')))
DATA.mkdir(parents=True,exist_ok=True)
STATE=DATA/'state.json'
LOCK=threading.RLock()
STOP=threading.Event()
DEFAULT={'folders':[],'presets':{},'favorites':[],'active':None,'debugPort':19327,'trash':[],'galleryDownloads':{}}
PLATFORMS={'codex':{'name':'Codex','debugPort':19327,'apps':['/Applications/ChatGPT.app/Contents/MacOS/ChatGPT','/Applications/Codex.app/Contents/MacOS/Codex']},'doubao':{'name':'豆包','debugPort':19326,'apps':['/Applications/Doubao.app/Contents/MacOS/Doubao']}}
STATUSES={key:{'connected':False,'matched':0} for key in PLATFORMS}
PORT=19329
NAMES={'cat-big-paw-scruffy':'毛茸茸猫咪 · 大爪子','cat-big-paw-doodle':'涂鸦猫咪 · 大爪子','chef-cat-wok-doodle':'猫咪主厨','onigiri-cat-doodle':'饭团猫咪','guangdong-stool':'广东小板凳','rippled-glass-nine-slice':'水波玻璃','mondrian-painting':'蒙德里安画框','mondrian':'蒙德里安','colorful-happy-doodle':'彩色快乐涂鸦','happy-stickman':'快乐小人','love-square-charcoal':'LOVE 方形炭笔','love-charcoal':'LOVE 炭笔'}
def state():
 try:s={**json.loads(json.dumps(DEFAULT)),**json.loads(STATE.read_text())}
 except (OSError,ValueError):s=json.loads(json.dumps(DEFAULT))
 if s.get('platform') not in PLATFORMS:s['platform']='codex'
 if 'platforms' not in s:
  s['platforms']={'codex':{'active':s.get('active'),'debugPort':s.get('debugPort',19327)}}
 for key,descriptor in PLATFORMS.items():s['platforms'].setdefault(key,{'active':None,'debugPort':descriptor['debugPort']})
 profile=s['platforms'][s['platform']];s['active']=profile.get('active');s['debugPort']=profile.get('debugPort',PLATFORMS[s['platform']]['debugPort'])
 return s
def save(s):
 with LOCK:
  if 'platforms' in s:s['platforms'][s.get('platform','codex')]['active']=s.get('active')
  tmp=DATA/'state.tmp';tmp.write_text(json.dumps(s,ensure_ascii=False,indent=2));tmp.replace(STATE)
def status_for(s):return STATUSES[s['platform']]
def clean_trash(s):
 remaining=[entry for entry in s.get('trash',[]) if Path(entry['stored']).is_file()]
 if remaining!=s.get('trash',[]):s['trash']=remaining;save(s)
 return s
def choose_folder(language="zh"):
 if sys.platform=='win32':
  from tkinter import Tk,filedialog
  root=Tk();root.withdraw();root.attributes('-topmost',True)
  try:return filedialog.askdirectory(parent=root,title='Choose your bubble asset folder' if language.startswith('en') else '选择气泡素材文件夹')
  finally:root.destroy()
 if sys.platform!='darwin':raise ValueError('目前仅支持 macOS 或 Windows 文件夹选择')
 prompt='Choose your bubble asset folder' if language.startswith('en') else '选择气泡素材文件夹'
 script='try\nreturn POSIX path of (choose folder with prompt "'+prompt+'")\non error number -128\nreturn ""\nend try'
 result=subprocess.run(['/usr/bin/osascript','-e',script],capture_output=True,text=True)
 if result.returncode:raise ValueError('无法打开文件夹选择窗口，请重试')
 return result.stdout.strip()
def png_info(path):
 b=path.read_bytes()
 if len(b)<33 or b[:8]!=b'\x89PNG\r\n\x1a\n' or b[12:16]!=b'IHDR':raise ValueError('不是有效的 PNG')
 w,h=struct.unpack('>II',b[16:24])
 if not(2<=w<=4096 and 2<=h<=4096):raise ValueError('图片尺寸需在 2–4096 像素内')
 return w,h,len(b)
def asset_id(path):return hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:20]
def bundled_presets():
 manifest=json.loads((ROOT/'presets/manifest.json').read_text())
 result=[]
 for entry in manifest['items']:
  path=ROOT/'presets'/entry['filename']
  if path.resolve().parent!=(ROOT/'presets').resolve():raise ValueError('无效预设文件')
  w,h,size=png_info(path)
  result.append({**entry,'width':w,'height':h,'bytes':size,'config':validate(entry['config'],w,h),'path':str(path.resolve()),'url':'/preset/'+entry['id']})
 return result
def seed_presets(s,restore=False):
 if s.get('builtinsInitialized') and not restore:return 0
 folder=DATA/'builtins';folder.mkdir(exist_ok=True);added=0
 for item in bundled_presets():
  destination=folder/item['filename']
  if not destination.exists():shutil.copy2(item['path'],destination);added+=1
  key=asset_id(destination);s['presets'].setdefault(key,item['config'])
  if not s.get('preferredId') and item['id']=='alien-cat':s['preferredId']=key
 s['builtinsInitialized']=True;save(s);return added
def first_run_setup(s):
 """Apply the bundled alien cat once on a fresh install, preserving older state."""
 if not s.get('firstRunPending'):return {'firstRun':False,'activeId':s['platforms']['codex'].get('active',{}).get('id') if s['platforms']['codex'].get('active') else None}
 seed_presets(s)
 item=next(x for x in library(s) if x['filename']=='alien-cat.png' and x['builtin'])
 if not s['platforms']['codex'].get('active'):
  s['platforms']['codex']['active']={'id':item['id'],'path':item['path'],'config':item['config'],'version':uuid.uuid4().hex}
  if s['platform']=='codex':s['active']=s['platforms']['codex']['active']
 s['firstRunPending']=False
 save(s)
 return {'firstRun':True,'activeId':s['platforms']['codex']['active']['id']}
def library(s=None):
 s=s or state();items=[];seen=set()
 for folder in s['folders']+[str(DATA/'imports'),str(DATA/'builtins')]:
  p=Path(folder)
  if not p.is_dir():continue
  for f in sorted(p.glob('*.png')):
   if str(f.resolve()) in seen:continue
   try:w,h,size=png_info(f)
   except (ValueError,OSError):continue
   seen.add(str(f.resolve()));key=asset_id(f);name=f.stem.removeprefix('douyin-bubble-').replace('-198x162','')
   for term,label in NAMES.items():
    if name.startswith(term):name=name.replace(term,label);break
   if f.parent==DATA/'builtins':name=next((x['name'] for x in bundled_presets() if x['filename']==f.name),name)
   config={**defaults(w,h),**s['presets'].get(key,{})}
   items.append({'id':key,'name':name,'filename':f.name,'width':w,'height':h,'bytes':size,'douyinSize':w<=198 and h<=162 and size<=2*1024*1024,'favorite':key in s['favorites'],'config':config,'url':'/asset/'+key,'builtin':f.parent==DATA/'builtins','path':str(f.resolve())})
 return items
def defaults(w,h):return {'left':round(w*.35),'right':round(w*.73),'top':round(h*.45),'bottom':round(h*.55),'scale':round(max(.01,min(.6,240/w,98/h)),4),'radius':0,'borderWidth':0,'borderColor':'#d0d0d0','color':'#44362f','padding':[29,37,36,48],'width':w,'height':h}
def validate(c,w,h):
 import re
 c={**defaults(w,h),**c,'width':w,'height':h}
 for k in ('left','right','top','bottom'):c[k]=int(c[k])
 if not(0<c['left']<c['right']<w and 0<c['top']<c['bottom']<h):raise ValueError('拉伸线不能交叉或超出图片')
 c['scale']=float(c['scale'])
 if not .01<=c['scale']<=2:raise ValueError('比例需在 1%–200% 之间')
 c['radius']=float(c['radius'])
 if not 0<=c['radius']<=200:raise ValueError('圆角需在 0–200 像素之间')
 c['borderWidth']=float(c['borderWidth'])
 if not 0<=c['borderWidth']<=20:raise ValueError('边框需在 0–20 像素之间')
 if not re.fullmatch(r'#[0-9a-fA-F]{6}',c['borderColor']):raise ValueError('边框颜色需为六位十六进制颜色')
 if not re.fullmatch(r'#[0-9a-fA-F]{6}',c['color']):raise ValueError('文字颜色需为六位十六进制颜色')
 if len(c['padding'])!=4 or any(not 0<=float(v)<=200 for v in c['padding']):raise ValueError('文字边距需在 0–200 之间')
 c['padding']=[float(v) for v in c['padding']];return c
def node_path():
 n=os.environ.get('BUBBLE_STUDIO_NODE') or shutil.which('node')
 if n:return n
 fallback=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'
 if fallback.exists():return str(fallback)
 if sys.platform=='win32':
  candidate=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'nodejs/node.exe'
  if candidate.exists():return str(candidate)
 raise ValueError('请安装 Node.js 22 或以上版本')
def bridge(action,platform="codex"):
 try:
  result=subprocess.run([node_path(),str(ROOT/'app/bridge.mjs'),str(STATE),action,platform],capture_output=True,text=True,timeout=12)
  return json.loads(result.stdout) if result.returncode==0 else {'connected':False,'matched':0,'message':'应用连接失败'}
 except Exception:return {'connected':False,'matched':0,'message':'应用连接暂不可用'}
def review_cli(*args):
 result=subprocess.run([sys.executable,str(ROOT/'scripts/review-submissions.py'),*args],capture_output=True,text=True,timeout=180)
 if result.returncode:raise ValueError((result.stderr or result.stdout or '审核服务失败').strip())
 return json.loads(result.stdout) if result.stdout.strip() else {}
def review_image(sid):
 import re
 if not re.fullmatch(r'[a-f0-9-]{36}',sid):raise ValueError('Invalid submission ID')
 result=subprocess.run(['gh','api',f'repos/kaitongg-bit/DIYcodex-bubble-submissions/contents/pending/{sid}/bubble.png'],capture_output=True,text=True,timeout=30)
 if result.returncode:raise ValueError('找不到待审图片')
 return base64.b64decode(json.loads(result.stdout)['content'])
def windows_app_candidates(key):
 names={'codex':('ChatGPT.exe','Codex.exe'),'doubao':('Doubao.exe',)}[key]
 override=os.environ.get('BUBBLE_STUDIO_CODEX_EXE' if key=='codex' else 'BUBBLE_STUDIO_DOUBAO_EXE')
 roots=[Path(value) for value in (os.environ.get('LOCALAPPDATA'),os.environ.get('ProgramFiles'),os.environ.get('ProgramFiles(x86)')) if value]
 candidates=[Path(override)] if override else []
 for root in roots:
  for name in names:
   stem=Path(name).stem
   candidates.extend((root/'Programs'/stem/name,root/stem/name,root/'Programs'/stem/'app'/name))
 return [p for p in candidates if p.is_file()]
def windows_store_apps(key):
 # Use only packages from the expected publisher; do not launch similarly named third-party apps.
 filter_script="Get-AppxPackage | Where-Object { $_.Publisher -match 'OpenAI' -and $_.Name -match 'ChatGPT|Codex|OpenAI' }" if key=='codex' else "Get-AppxPackage | Where-Object { $_.Name -match 'Doubao' -and $_.Publisher -match 'ByteDance|Bytedance|Doubao' }"
 script=f"{filter_script} | ForEach-Object {{ $p=$_; [xml]$m=(Get-AppxPackageManifest -Package $p.PackageFullName); foreach($a in $m.Package.Applications.Application) {{ if($a.Executable) {{ Join-Path $p.InstallLocation $a.Executable }} }} }}"
 result=subprocess.run(['powershell.exe','-NoProfile','-Command',script],capture_output=True,text=True,timeout=15)
 if result.returncode:return []
 return [p for line in result.stdout.splitlines() if (p:=Path(line.strip())).is_file()]
def windows_running_names():
 result=subprocess.run(['tasklist.exe','/fo','csv','/nh'],capture_output=True,text=True,check=True,timeout=10)
 import csv,io
 return {row[0].casefold() for row in csv.reader(io.StringIO(result.stdout)) if row}
def launch_platform(key,s):
 if sys.platform not in ('darwin','win32'):raise ValueError('目前仅支持 macOS 和 Windows')
 descriptor=PLATFORMS[key]
 if sys.platform=='darwin':
  apps=[p for p in map(Path,descriptor['apps']) if p.exists()]
  processes=subprocess.run(['/bin/ps','-axo','command='],capture_output=True,text=True,check=True)
  lines=(processes.stdout or '').splitlines()
  running_app=next((app for app in apps if any(line==str(app) or line.startswith(str(app)+' ') for line in lines)),None)
 else:
  apps=windows_app_candidates(key) or windows_store_apps(key)
  names={'codex':{'chatgpt.exe','codex.exe'},'doubao':{'doubao.exe'}}[key]
  running=windows_running_names() if apps else set()
  running_app=next((app for app in apps if app.name.casefold() in running),None)
 if not apps:raise ValueError(f'未找到 {descriptor["name"]} 桌面应用；Windows 可设置 BUBBLE_STUDIO_{"CODEX" if key=="codex" else "DOUBAO"}_EXE 指向应用程序。' if sys.platform=='win32' else '未找到豆包桌面应用，请确认已安装 /Applications/Doubao.app' if key=='doubao' else '未找到 ChatGPT 或 Codex 应用')
 app=running_app or apps[0]
 if running_app:
  if bridge('status',key).get('connected'):return {'platform':key,'state':'connected','message':f'{descriptor["name"]} 已连接，气泡会自动恢复。'}
  shortcut='从任务栏完全退出' if sys.platform=='win32' else '用 ⌘Q 完全退出'
  return {'platform':key,'state':'quit-required','message':f'{descriptor["name"]} 已普通启动。请保存输入并{shortcut}，再点击启动。'}
 with (DATA/'app-start.log').open('a') as log:
  kwargs={'start_new_session':True} if sys.platform=='darwin' else {'creationflags':getattr(subprocess,'CREATE_NEW_PROCESS_GROUP',0)}
  subprocess.Popen([str(app),'--remote-debugging-address=127.0.0.1',f'--remote-debugging-port={s["platforms"][key]["debugPort"]}'],stdout=log,stderr=log,**kwargs)
 return {'platform':key,'state':'starting','message':f'{descriptor["name"]} 正在启动，连接后会自动恢复已选气泡。'}
def watch(platform):
 while not STOP.wait(3):
  s=state();active=s['platforms'][platform].get('active')
  STATUSES[platform]=bridge('apply' if active else 'status',platform)
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def send(self,data,code=200,kind='application/json'):
  body=json.dumps(data,ensure_ascii=False).encode() if kind=='application/json' else data
  self.send_response(code);self.send_header('Content-Type',kind);self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
 def do_GET(self):
  path=self.path.split('?')[0]
  if path=='/api/library':
   with LOCK:s=clean_trash(state());seed_presets(s);items=library(s)
   for item in items:item.pop('path')
   return self.send({'items':items,'folders':s['folders'],'activeId':s['active']['id'] if s['active'] else None,'preferredId':s.get('preferredId'),'trashCount':len(s.get('trash',[])),'latestTrashId':s['trash'][-1]['token'] if s.get('trash') else None,'status':status_for(s),'platform':s['platform']})
  if path=='/api/gallery':
   s=state();items=bundled_presets()
   for item in items:item.pop('path');item['downloads']=s.get('galleryDownloads',{}).get(item['id'],0)
   return self.send({'items':items,'scope':'local','moderationAvailable':False})
  if path.startswith('/preset/'):
   item=next((x for x in bundled_presets() if x['id']==path[8:]),None)
   if not item:return self.send({'error':'素材不存在'},404)
   return self.send(Path(item['path']).read_bytes(),kind='image/png')
  if path=='/api/status':
   s=state();return self.send({**status_for(s),'activeId':s['active']['id'] if s['active'] else None,'platform':s['platform']})
  if path=='/api/autostart':return self.send({'enabled':autostart_enabled()})
  if path.startswith('/asset/'):
   item=next((x for x in library() if x['id']==path[7:]),None)
   if not item:return self.send({'error':'素材不存在'},404)
   return self.send(Path(item['path']).read_bytes(),kind='image/png')
  if path=='/api/design-prompt':return self.send({'prompt':'使用 $douyin-chat-bubble skill 设计一款原创抖音聊天气泡。先确定四边直线锚区和点九拉伸线，保证镜像可读与文字空间；导出到我的素材库，完成尺寸、边距、四边锚点与长短消息预检，再在气泡工坊里选择并应用。'})
  if path=='/api/review/list':return self.send(review_cli('list'))
  if path.startswith('/api/review/image'):
   from urllib.parse import parse_qs,urlparse
   sid=parse_qs(urlparse(self.path).query).get('id',[''])[0]
   return self.send(review_image(sid),kind='image/png')
  if path=='/api/export':
   s=state();return self.send({'version':1,'active':None if not s['active'] else {'filename':Path(s['active']['path']).name,'config':s['active']['config']}})
  files={'/':'index.html','/index.html':'index.html','/app.css':'app.css','/app.js':'app.js','/nine-slice.mjs':'nine-slice.mjs','/editor-core.mjs':'editor-core.mjs','/i18n.mjs':'i18n.mjs','/codex-preview.mjs':'codex-preview.mjs','/codex-preview.css':'codex-preview.css','/gallery':'gallery.html','/gallery.html':'gallery.html','/gallery.js':'gallery.js','/gallery.css':'gallery.css','/review':'review.html','/review.html':'review.html','/review.js':'review.js','/review.css':'review.css','/workshop':'workshop.html','/workshop.html':'workshop.html','/workshop.js':'workshop.js','/workshop.css':'workshop.css'}
  if path not in files:return self.send({'error':'不存在'},404)
  f=ROOT/'app/static'/files[path];kind={'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','mjs':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[f.suffix[1:]];return self.send(f.read_bytes(),kind=kind)
 def do_POST(self):
  if self.headers.get('Origin')!=f'http://127.0.0.1:{PORT}' or self.headers.get('X-Bubble-Studio')!='1':return self.send({'error':'只允许本机工作台操作'},403)
  try:
   length=int(self.headers.get('Content-Length','0'))
   if length>4*1024*1024:raise ValueError('请求过大')
   body=json.loads(self.rfile.read(length))
   if self.path=='/api/choose-folder':
    selected=choose_folder(self.headers.get('Accept-Language','zh'))
    if not selected:return self.send({'ok':True,'cancelled':True})
    body={'path':selected}
   with LOCK:
    s=state()
    if self.path=='/api/platform':
     key=body.get('platform')
     if key not in PLATFORMS:raise ValueError('不支持的平台')
     s['platform']=key;s['active']=s['platforms'][key].get('active');s['debugPort']=s['platforms'][key]['debugPort'];save(s)
     return self.send({'ok':True,'platform':key,'status':status_for(s)})
    if self.path=='/api/autostart':
     if type(body.get('enabled')) is not bool:raise ValueError('请选择开启或关闭')
     return self.send({'ok':True,'enabled':configure_autostart(body['enabled'])})
    if self.path=='/api/reveal-launcher':
     if sys.platform=='darwin':
      launcher=ROOT/'Open Bubble Apps.app'
      if not launcher.is_dir():raise ValueError('找不到气泡启动图标')
      subprocess.run(['/usr/bin/open','-R',str(launcher)],check=True,capture_output=True)
     elif sys.platform=='win32':
      launcher=ROOT/'Open Bubble Apps.vbs'
      if not launcher.is_file():raise ValueError('找不到气泡启动图标')
      subprocess.Popen(['explorer.exe',f'/select,{launcher}'])
     else:raise ValueError('目前仅支持 macOS 和 Windows')
     return self.send({'ok':True})
    if self.path=='/api/first-run':
     result=first_run_setup(s)
     if result['firstRun']:
      try:result['autostartEnabled']=configure_autostart(True)
      except (ValueError,OSError) as error:result['autostartError']=str(error)
     return self.send({'ok':True,**result})
    if self.path=='/api/review/decision':
     sid=str(body.get('id',''));action=body.get('action');reason=str(body.get('reason',''))[:500]
     if action not in ('approve','reject'):raise ValueError('审核动作无效')
     return self.send(review_cli(action,sid,'--reason',reason))
    if self.path=='/api/review/batch':
     ids=body.get('ids',[]);reason=str(body.get('reason',''))[:500]
     if not isinstance(ids,list) or not ids:raise ValueError('请先选择投稿')
     return self.send(review_cli('batch-approve',json.dumps(ids,ensure_ascii=False),'--reason',reason))
    if self.path=='/api/launch-active':
     active=[key for key in PLATFORMS if s['platforms'][key].get('active')]
     if not active:raise ValueError('还没有已应用的气泡；请先在工坊中选择并应用。')
     results=[]
     for key in active:
      try:results.append(launch_platform(key,s))
      except (ValueError,OSError,subprocess.SubprocessError) as error:results.append({'platform':key,'state':'unavailable','message':str(error)})
     return self.send({'ok':True,'results':results,'message':' '.join(result['message'] for result in results)})
    if body.get('platform',s['platform'])!=s['platform']:raise ValueError('平台已切换，请刷新后重试')
    if self.path=='/api/restore-builtins':
     added=seed_presets(s,restore=True);return self.send({'ok':True,'added':added})
    if self.path=='/api/gallery-download':
     item=next((x for x in bundled_presets() if x['id']==body.get('id')),None)
     if not item:raise ValueError('素材不存在')
     data=base64.b64encode(Path(item['path']).read_bytes()).decode()
     counts=s.setdefault('galleryDownloads',{});counts[item['id']]=counts.get(item['id'],0)+1;save(s)
     return self.send({'ok':True,'filename':item['filename'],'data':data,'config':item['config'],'downloads':counts[item['id']]})
    if self.path in ('/api/folder','/api/choose-folder'):
     p=Path(body['path']).expanduser().resolve()
     if not p.is_dir():raise ValueError('文件夹不存在')
     if str(p) not in s['folders']:s['folders'].append(str(p))
     save(s);return self.send({'ok':True})
    if self.path=='/api/open-trash':
     trash=DATA/'trash';trash.mkdir(exist_ok=True)
     if sys.platform=='darwin':subprocess.run(['/usr/bin/open',str(trash.resolve())],check=True,capture_output=True)
     elif sys.platform=='win32':os.startfile(str(trash.resolve()))
     else:raise ValueError('目前仅支持 macOS 和 Windows')
     return self.send({'ok':True})
    if self.path=='/api/import':
     data=base64.b64decode(body['data'],validate=True)
     if len(data)>2*1024*1024:raise ValueError('PNG 不得超过 2 MB')
     folder=DATA/'imports';folder.mkdir(exist_ok=True);name=Path(body['name']).name
     if not name.lower().endswith('.png'):raise ValueError('请选择 PNG')
     p=folder/(uuid.uuid4().hex[:8]+'-'+name);p.write_bytes(data)
     try:png_info(p)
     except Exception:p.unlink();raise
     return self.send({'ok':True,'id':asset_id(p)})
    if self.path=='/api/delete':
     item=next((x for x in library(s) if x['id']==body['id']),None)
     if not item:raise ValueError('素材不存在')
     source=Path(item['path']);token=uuid.uuid4().hex
     trash=DATA/'trash';trash.mkdir(exist_ok=True);destination=trash/(token[:8]+'-'+source.name)
     shutil.move(str(source),str(destination))
     entry={'token':token,'id':item['id'],'original':str(source),'stored':str(destination)}
     s.setdefault('trash',[]).append(entry)
     removed_platforms=[key for key,profile in s['platforms'].items() if profile.get('active') and profile['active']['id']==item['id']]
     removed_active=bool(removed_platforms)
     for key in removed_platforms:s['platforms'][key]['active']=None
     s['active']=s['platforms'][s['platform']].get('active')
     try:save(s)
     except Exception:shutil.move(str(destination),str(source));raise
     for key in removed_platforms:STATUSES[key]=bridge('restore',key)
     return self.send({'ok':True,'token':token,'activeRemoved':removed_active})
    if self.path=='/api/undo-delete':
     entry=next((x for x in s.get('trash',[]) if x['token']==body['token']),None)
     if not entry:raise ValueError('未找到可恢复的素材')
     original=Path(entry['original']);stored=Path(entry['stored'])
     if original.exists() or original.is_symlink():raise ValueError('原位置已有同名文件，恢复未覆盖任何文件')
     original.parent.mkdir(parents=True,exist_ok=True)
     shutil.move(str(stored),str(original));s['trash']=[x for x in s['trash'] if x['token']!=entry['token']]
     try:save(s)
     except Exception:shutil.move(str(original),str(stored));raise
     return self.send({'ok':True,'id':entry['id']})
    if self.path=='/api/favorite':
     key=body['id'];s['favorites']=[x for x in s['favorites'] if x!=key] if key in s['favorites'] else s['favorites']+[key];save(s);return self.send({'ok':True})
    if self.path in ('/api/save','/api/apply'):
     item=next((x for x in library(s) if x['id']==body['id']),None)
     if not item:raise ValueError('素材不存在')
     c=validate(body['config'],item['width'],item['height']);s['presets'][item['id']]=c;s['preferredId']=item['id']
     if self.path=='/api/apply':
      s['active']={'id':item['id'],'path':item['path'],'config':c,'version':uuid.uuid4().hex}
      # Hand off from the old one-bubble monitor before taking ownership.
      old=ROOT.parent/'codex-cat-bubble'
      if s['platform']=='codex' and old.is_dir():(old/'stop-watch').write_text('studio owns appearance')
     save(s)
    elif self.path=='/api/restore':s['active']=None;save(s)
    elif self.path=='/api/launch':
     result=launch_platform(s['platform'],s)
     return self.send({'ok':True,**result})
    else:raise ValueError('未知操作')
   launch=None
   if self.path in ('/api/apply','/api/restore'):
    STATUSES[s['platform']]=bridge('restore' if self.path=='/api/restore' else 'apply',s['platform'])
    if self.path=='/api/apply' and not STATUSES[s['platform']].get('connected'):
     try:launch=launch_platform(s['platform'],s)
     except (ValueError,OSError,subprocess.SubprocessError) as error:launch={'platform':s['platform'],'state':'unavailable','message':str(error)}
   return self.send({'ok':True,'status':status_for(s),'platform':s['platform'],'launch':launch})
  except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError) as e:self.send({'error':str(e)},400)
def main():
 global PORT
 parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=19329);args=parser.parse_args();PORT=args.port
 if not STATE.exists():save({**DEFAULT,'firstRunPending':True})
 for platform in PLATFORMS:threading.Thread(target=watch,args=(platform,),daemon=True).start()
 print(f'气泡工坊 http://127.0.0.1:{PORT}',flush=True)
 try:ThreadingHTTPServer(('127.0.0.1',PORT),Handler).serve_forever()
 finally:STOP.set()
if __name__=='__main__':main()
