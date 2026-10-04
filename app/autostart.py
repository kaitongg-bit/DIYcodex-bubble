"""Per-user login startup for previously applied bubbles. No administrator access."""
from pathlib import Path
import os
import plistlib
import sys

ROOT = Path(__file__).resolve().parent.parent
MAC_LABEL = 'cc.kaitongg.diycodexbubble.restore'
WIN_NAME = 'DIY Codex Bubble Restore.vbs'


def item_path(platform=None, home=None, appdata=None):
 platform = platform or sys.platform
 if platform == 'darwin':
  return Path(home or Path.home())/'Library'/'LaunchAgents'/(MAC_LABEL+'.plist')
 if platform == 'win32':
  base = appdata or os.environ.get('APPDATA')
  if not base:raise ValueError('找不到 Windows 用户启动文件夹')
  return Path(base)/'Microsoft'/'Windows'/'Start Menu'/'Programs'/'Startup'/WIN_NAME
 raise ValueError('登录自动恢复仅支持 macOS 和 Windows')


def item_content(platform=None, python=None, root=None):
 platform = platform or sys.platform
 python = Path(python or sys.executable).resolve()
 root = Path(root or ROOT).resolve()
 script = root/'scripts'/'login-start.py'
 if platform == 'darwin':
  return plistlib.dumps({'Label':MAC_LABEL,'ProgramArguments':[str(python),str(script)],
   'WorkingDirectory':str(root),'RunAtLoad':True,
   'EnvironmentVariables':{'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin'}})
 if platform == 'win32':
  pythonw = python.with_name('pythonw.exe')
  executable = pythonw if pythonw.is_file() else python
  launcher = root/'DIY Codex Bubble.exe'
  command = f'"{launcher}" --restore' if launcher.is_file() else f'"{executable}" -X utf8 "{script}"'
  if any(char in command for char in '\r\n'):raise ValueError('启动路径不能包含换行')
  # VBScript doubles quotes in string literals. Window style 0 hides a console.
  return ('Set shell = CreateObject("WScript.Shell")\r\n'
          f'shell.Run "{command.replace(chr(34), chr(34)*2)}", 0, False\r\n').encode('utf-16')
 raise ValueError('登录自动恢复仅支持 macOS 和 Windows')


def enabled(platform=None, home=None, appdata=None):
 path = item_path(platform,home,appdata)
 if not path.is_file():return False
 try:
  content = path.read_bytes()
  if (platform or sys.platform) == 'darwin':return plistlib.loads(content).get('Label') == MAC_LABEL
  script = content.decode('utf-16')
  return ('login-start.py' in script or 'DIY Codex Bubble.exe' in script) and 'WScript.Shell' in script
 except (OSError,ValueError,UnicodeError):return False


def configure(turn_on, platform=None, home=None, appdata=None, python=None, root=None):
 path = item_path(platform,home,appdata)
 if turn_on:
  path.parent.mkdir(parents=True,exist_ok=True)
  if path.exists() and not enabled(platform,home,appdata):raise ValueError('登录启动项已被其他内容占用，请手动检查')
  temp = path.with_suffix(path.suffix+'.tmp')
  temp.write_bytes(item_content(platform,python,root));temp.replace(path)
 elif path.exists():
  if not enabled(platform,home,appdata):raise ValueError('登录启动项不是本工具创建的，未删除')
  path.unlink()
 return enabled(platform,home,appdata)
