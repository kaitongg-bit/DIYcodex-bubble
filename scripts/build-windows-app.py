"""Build the self-contained Windows application on a Windows runner."""
import argparse
import hashlib
from pathlib import Path
import shutil
import subprocess
import urllib.request
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = (
    ('python', 'https://www.python.org/ftp/python/3.13.16/python-3.13.16-embed-amd64.zip',
     '97dae5274cc54867065e8d5a3226e48c35017ed332a0fdb0e27d5b5821961297'),
    ('node', 'https://nodejs.org/dist/v22.23.3/node-v22.23.3-win-x64.zip',
     '2b0ff57b049cda1bbcea2240eec20467018713c1efe1f7360c2681859b90ed71'),
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', required=True)
    parser.add_argument('--light', action='store_true', help='Resolve or download runtimes at first launch')
    args = parser.parse_args()
    if not args.version or any(c not in '0123456789.-' for c in args.version):
        parser.error('Invalid version')
    stage = ROOT / ('dist/windows-light' if args.light else 'dist/windows-app')
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    for name in ('app', 'presets', 'assets'):
        shutil.copytree(ROOT / name, stage / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    (stage / 'scripts').mkdir()
    shutil.copy2(ROOT / 'scripts/login-start.py', stage / 'scripts/login-start.py')
    shutil.copy2(ROOT / 'LICENSE', stage / 'LICENSE.txt')
    cache = ROOT / 'dist/runtime-cache'
    cache.mkdir(exist_ok=True)
    for name, url, digest in (() if args.light else RUNTIMES):
        archive = cache / url.rsplit('/', 1)[1]
        if not archive.exists():
            urllib.request.urlretrieve(url, archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError(f'{name} download checksum mismatch')
        target = stage / 'runtime' / name
        target.mkdir(parents=True)
        with zipfile.ZipFile(archive) as contents:
            contents.extractall(target)
        if name == 'node':
            inner = target / archive.stem
            # Retain the license; npm and its dependencies are not needed.
            shutil.copy2(inner / 'node.exe', target / 'node.exe')
            shutil.copy2(inner / 'LICENSE', target / 'LICENSE')
            shutil.rmtree(inner)
    if not args.light:
        (stage / 'runtime/python/python313._pth').write_text(
            'python313.zip\n.\n../../app\n../..\n', encoding='utf-8')
    Image.open(stage / 'assets/app-icon.png').save(stage / 'assets/AppIcon.ico',
        sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
    import os
    csc = Path(os.environ['WINDIR']) / 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
    subprocess.run([str(csc), '/nologo', '/target:winexe', '/platform:x64',
        '/reference:System.Windows.Forms.dll', '/reference:System.IO.Compression.dll',
        '/reference:System.IO.Compression.FileSystem.dll', f'/win32icon:{stage / "assets/AppIcon.ico"}',
        f'/out:{stage / "DIY Codex Bubble.exe"}', str(ROOT / 'packaging/windows/Launcher.cs'), str(ROOT / 'packaging/windows/RuntimeBootstrap.cs')], check=True)
    # Portable app is also useful for machines where installation is restricted.
    variant = 'light' if args.light else 'offline'
    with zipfile.ZipFile(ROOT / f'dist/DIYcodex-bubble-v{args.version}-windows-x64-{variant}-portable.zip', 'w', zipfile.ZIP_DEFLATED) as output:
        for path in stage.rglob('*'):
            if path.is_file():
                output.write(path, 'DIY Codex Bubble/' + path.relative_to(stage).as_posix())
    print(stage)


if __name__ == '__main__':
    main()
