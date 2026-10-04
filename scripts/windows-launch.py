"""Windows double-click entry point for the local studio and saved app bubbles."""
from pathlib import Path
import json,subprocess,sys,time,urllib.request,webbrowser

ROOT=Path(__file__).resolve().parents[1]
URL='http://127.0.0.1:19329'

def request(path,body=None):
 headers={'Origin':URL,'X-Bubble-Studio':'1','Content-Type':'application/json'}
 data=None if body is None else json.dumps(body).encode()
 with urllib.request.urlopen(urllib.request.Request(URL+path,data=data,headers=headers),timeout=3) as response:
  return json.load(response)

def main():
 if sys.platform!='win32':raise RuntimeError('This launcher is for Windows.')
 if sys.version_info<(3,9):raise RuntimeError('Python 3.9 or newer is required.')
 try:request('/api/library')
 except Exception:
  local=ROOT/'.local';local.mkdir(exist_ok=True)
  with (local/'studio.log').open('a',encoding='utf-8') as log:
   subprocess.Popen([sys.executable,str(ROOT/'app/server.py')],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS)
  for _ in range(40):
   time.sleep(.25)
   try:request('/api/library');break
   except Exception:pass
  else:raise RuntimeError('Bubble Studio did not start. Check .local/studio.log.')
 if len(sys.argv)>1 and sys.argv[1]=='apps':
  result=request('/api/launch-active',{})
  print(result.get('message') or result.get('error') or '')
 webbrowser.open(URL)

if __name__=='__main__':
 try:main()
 except Exception as error:
  print(error,file=sys.stderr);sys.exit(1)
