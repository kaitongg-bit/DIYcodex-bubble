"""Discover known desktop executables without scanning an entire drive."""
import base64
import ctypes
import json
import os
from pathlib import Path
import re
import subprocess

NAMES = {'codex': ('ChatGPT.exe', 'Codex.exe'), 'doubao': ('Doubao.exe',)}


def local_drives():
    if os.name != 'nt':
        return []
    kernel = ctypes.windll.kernel32
    mask = kernel.GetLogicalDrives()
    return [Path(f'{chr(65+i)}:/') for i in range(26)
            if mask & (1 << i) and kernel.GetDriveTypeW(f'{chr(65+i)}:\\') == 3]


def executable_paths(folder, names):
    """Only inspect known app folders and their direct version subfolders."""
    folder = Path(folder)
    candidates = []
    for base in (folder, folder / 'Application', folder / 'app', folder / 'current'):
        candidates.extend(base / name for name in names)
        if base.is_dir():
            # Newest numeric version first; never recursively walk a whole drive.
            try:
                versions = [p for p in base.iterdir() if p.is_dir() and re.fullmatch(r'(?:app-)?\d+(?:\.\d+)*(?:[-\w.]*)', p.name)]
            except OSError:
                continue
            versions.sort(key=lambda p: tuple(int(n) for n in re.findall(r'\d+', p.name)), reverse=True)
            candidates.extend(version / name for version in versions[:30] for name in names)
    return candidates


def registered_paths(key):
    """Read process paths, App Paths, uninstall metadata and named shortcuts."""
    names = NAMES[key]
    label = 'Doubao|豆包' if key == 'doubao' else 'Codex|ChatGPT'
    array = ','.join("'" + n + "'" for n in names)
    script = r"""[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$names = @(__NAMES__)
$paths = [System.Collections.Generic.List[string]]::new()
$filter = ($names | ForEach-Object { "Name = '$_'" }) -join ' OR '
Get-CimInstance Win32_Process -Filter $filter -ErrorAction SilentlyContinue | ForEach-Object {
  if ($_.ExecutablePath) { $paths.Add($_.ExecutablePath) }
}
foreach ($base in @('HKCU:\Software\Microsoft\Windows\CurrentVersion\App Paths','HKLM:\Software\Microsoft\Windows\CurrentVersion\App Paths','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths')) {
  foreach ($name in $names) {
    $item = Get-Item -LiteralPath "$base\$name" -ErrorAction SilentlyContinue
    if ($item) { $value = $item.GetValue(''); if ($value) { $paths.Add($value.Trim('"')) } }
  }
}
foreach ($base in @('HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall')) {
  Get-ItemProperty "$base\*" -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match '^(__LABEL__)(?:\s|$)' } | ForEach-Object {
    if ($_.InstallLocation) { $paths.Add($_.InstallLocation.Trim('"')) }
    if ($_.DisplayIcon) { $paths.Add(($_.DisplayIcon -replace ',\s*-?\d+$','').Trim('"')) }
    if ($_.UninstallString -match '^\s*"([^"]+\.exe)"|^\s*(.+?\.exe)(?:\s|$)') {
      $exe = if ($matches[1]) { $matches[1] } else { $matches[2] }
      $paths.Add((Split-Path -Parent $exe))
    }
  }
}
$shell = New-Object -ComObject WScript.Shell
foreach ($base in @([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('CommonDesktopDirectory'),[Environment]::GetFolderPath('StartMenu'),[Environment]::GetFolderPath('CommonStartMenu'))) {
  if ($base) {
    Get-ChildItem -LiteralPath $base -Filter '*.lnk' -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.BaseName -match '^(__LABEL__)(?:\s|$)' } | ForEach-Object {
      $target = $shell.CreateShortcut($_.FullName).TargetPath
      if ($target) { $paths.Add($target) }
    }
  }
}
ConvertTo-Json -Compress -InputObject @($paths | Select-Object -Unique)
""".replace('__NAMES__', array).replace('__LABEL__', label)
    encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
    try:
        result = subprocess.run(['powershell.exe','-NoProfile','-EncodedCommand',encoded],
            capture_output=True,text=True,encoding='utf-8',timeout=20,
            creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        if result.returncode:
            return []
        paths = json.loads(result.stdout.strip().lstrip('\ufeff'))
        return [Path(p) for p in paths if isinstance(p,str)] if isinstance(paths,list) else []
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return []


def find_candidates(key, saved=None):
    names = NAMES[key]
    override = os.environ.get('BUBBLE_STUDIO_CODEX_EXE' if key == 'codex' else 'BUBBLE_STUDIO_DOUBAO_EXE')
    candidates = [Path(p) for p in (override, saved) if p]
    roots = [Path(p) for p in (os.environ.get('LOCALAPPDATA'),os.environ.get('ProgramFiles'),os.environ.get('ProgramFiles(x86)')) if p]
    drives = local_drives()
    # A direct D:\Doubao.exe is checked without enumerating D:\.
    candidates.extend(drive / name for drive in drives for name in names)
    for root in roots + drives:
        for name in names:
            stem = Path(name).stem
            for folder in (root/stem, root/'Programs'/stem, root/'ByteDance'/stem, root/'Programs/ByteDance'/stem):
                candidates.extend(executable_paths(folder,names))
        if key == 'doubao':
            candidates.extend(executable_paths(root/'豆包',names))
    existing = list(dict.fromkeys(p for p in candidates if p.is_file() and p.name.casefold() in {n.casefold() for n in names}))
    if existing:
        return existing
    for path in registered_paths(key):
        if path.is_dir():
            candidates.extend(executable_paths(path,names))
        elif path.name.casefold() in {n.casefold() for n in names}:
            candidates.append(path)
    return list(dict.fromkeys(p for p in candidates if p.is_file() and p.name.casefold() in {n.casefold() for n in names}))


def choose_executable(key):
    array = ','.join("'" + n + "'" for n in NAMES[key])
    script = "[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); Add-Type -AssemblyName System.Windows.Forms; $dialog=New-Object System.Windows.Forms.OpenFileDialog; $dialog.Title='Select " + ('Doubao.exe' if key=='doubao' else 'Codex.exe / ChatGPT.exe') + "'; $dialog.Filter='Application (*.exe)|*.exe'; try { if($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { if(@("+array+") -notcontains [IO.Path]::GetFileName($dialog.FileName)) { throw 'Select the app executable, not its installer.' }; ConvertTo-Json -Compress -InputObject $dialog.FileName } else { ConvertTo-Json -Compress -InputObject '' } } finally { $dialog.Dispose() }"
    result = subprocess.run(['powershell.exe','-NoProfile','-STA','-EncodedCommand',base64.b64encode(script.encode('utf-16le')).decode('ascii')],
        capture_output=True,text=True,encoding='utf-8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    if result.returncode:
        raise ValueError('请选择应用本身的 .exe 文件，不是下载的安装包')
    return json.loads(result.stdout.strip().lstrip('\ufeff'))
