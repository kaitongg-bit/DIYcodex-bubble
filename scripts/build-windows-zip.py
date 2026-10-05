"""Package the Windows workshop without private state or macOS launchers."""
import argparse
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    if not args.version or any(c not in '0123456789.-' for c in args.version):
        parser.error('Version must contain only digits, dots and hyphens')
    output = ROOT / 'dist' / f'DIYcodex-bubble-v{args.version}-windows.zip'
    output.parent.mkdir(exist_ok=True)
    files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
    scripts = {'scripts/windows-launch.py', 'scripts/login-start.py'}
    documents = {'README.md', 'README.en.md', 'LICENSE', 'RESPONSIBILITY.md', 'RESPONSIBILITY.en.md'}
    prefix = 'DIY Codex Bubble/'
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in files:
            if not name:
                continue
            path = Path(name)
            if path.parts[0] in {'app', 'presets', 'assets'} or name in scripts | documents or (path.parts[:2] == ('scripts', 'launchers') and path.suffix in {'.cmd', '.vbs'} and not path.name.startswith('START HERE')):
                archive.write(ROOT / name, prefix + name)
        archive.writestr(prefix + 'WINDOWS-START.txt',
            'Windows 使用说明 / Quick start\r\n\r\n'
            '1. 先解压整个 ZIP，请勿直接在压缩包里运行。\r\n'
            '2. 安装 Python 3.9+（安装时勾选 Add Python to PATH）和 Node.js LTS。\r\n'
            '3. 双击 scripts\\launchers\\Start Bubble Studio.cmd，不需要管理员权限。\r\n'
            '4. 浏览器会打开本机工坊；选好气泡后点击应用。若提示已普通启动，请完全退出 Codex/豆包，再点工坊里的重新启动。\r\n'
            '5. 以后打开工坊仍双击 scripts\\launchers\\Start Bubble Studio.cmd；设置保存在本机 .local 文件夹。\r\n\r\n'
            'Extract the entire ZIP first. Install Python 3.9+ with Add Python to PATH and Node.js LTS.\r\n'
            'Double-click scripts\\launchers\\Start Bubble Studio.cmd (administrator rights are not required).\r\n'
            'If the target app is already running normally, fully quit it and use Restart in the workshop.\r\n'
            'Windows support is beta; this ZIP does not bundle Python or Node.js.\r\n')
    print(output)


if __name__ == '__main__':
    main()
