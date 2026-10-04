"""Silent login entry point: start local service, then restore saved apps."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
URL = 'http://127.0.0.1:19329'


def request(path, body=None):
 headers={'Origin':URL,'X-Bubble-Studio':'1','Content-Type':'application/json'}
 data=None if body is None else json.dumps(body).encode()
 with urllib.request.urlopen(urllib.request.Request(URL+path,data=data,headers=headers),timeout=5) as response:
  return json.load(response)


def main(open_studio=False):
 if sys.platform not in ('darwin','win32'):return
 os.environ['PATH']=os.pathsep.join(['/opt/homebrew/bin','/usr/local/bin',os.environ.get('PATH','')])
 local=ROOT/'.local';local.mkdir(exist_ok=True)
 try:request('/api/status')
 except Exception:
  with (local/'studio.log').open('a',encoding='utf-8') as log:
   kwargs={'start_new_session':True} if sys.platform=='darwin' else {'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS}
   subprocess.Popen([sys.executable,str(ROOT/'app/server.py')],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=log,**kwargs)
  for _ in range(50):
   time.sleep(.2)
   try:request('/api/status');break
   except Exception:pass
  else:raise RuntimeError('Bubble Studio local service did not start')
 if open_studio:
  setup=request('/api/first-run',{})
  if setup.get('firstRun'):
   try:request('/api/launch-active',{})
   except Exception:pass
  if sys.platform=='darwin':
   subprocess.run(['/usr/bin/open',URL],check=True)
  else:
   webbrowser.open(URL)
  return
 # /api/launch-active only launches platforms with a saved active bubble.
 result=request('/api/launch-active',{})
 with (local/'login-start.log').open('a',encoding='utf-8') as log:
  log.write(json.dumps(result,ensure_ascii=False)+'\n')
 # A normal app launch cannot accept the debugging port. Surface that state in
 # the studio instead of silently exiting with no visible feedback.
 if any(item.get('state')=='quit-required' for item in result.get('results',[])):
  if sys.platform=='darwin':
   subprocess.run(['/usr/bin/open',URL],check=True)
  else:
   webbrowser.open(URL)


if __name__=='__main__':
 try:main(open_studio='--studio' in sys.argv[1:])
 except Exception as error:
  local=ROOT/'.local';local.mkdir(exist_ok=True)
  with (local/'login-start.log').open('a',encoding='utf-8') as log:log.write(f'error: {error}\n')
