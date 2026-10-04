#ifndef AppVersion
  #define AppVersion "0.2.10"
#endif
#ifndef StageName
  #define StageName "windows-light"
#endif
#ifndef Variant
  #define Variant "light"
#endif
[Setup]
AppId={{C03D2187-EA90-4BBA-B824-379FA9A5FCF7}
AppName=DIY Codex Bubble
AppVersion={#AppVersion}
AppPublisher=kaitongg
AppPublisherURL=https://github.com/kaitongg-bit/DIYcodex-bubble
DefaultDirName={localappdata}\Programs\DIY Codex Bubble
DefaultGroupName=DIY Codex Bubble
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
OutputDir=..\..\dist
OutputBaseFilename=DIYcodex-bubble-v{#AppVersion}-windows-x64-{#Variant}-setup
SetupIconFile=..\..\dist\{#StageName}\assets\AppIcon.ico
UninstallDisplayIcon={app}\DIY Codex Bubble.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\..\dist\{#StageName}\DIY Codex Bubble.exe"; DestName: "Bubble Upgrade Helper.exe"; Flags: dontcopy
Source: "..\..\dist\{#StageName}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DIY Codex Bubble"; Filename: "{app}\DIY Codex Bubble.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\DIY Codex Bubble"; Filename: "{app}\DIY Codex Bubble.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\DIY Codex Bubble.exe"; Description: "Open DIY Codex Bubble / 打开气泡工坊"; Flags: nowait postinstall skipifsilent; Check: not IsBubbleUpdate

Filename: "{app}\DIY Codex Bubble.exe"; Flags: nowait; Check: IsBubbleUpdate

[UninstallRun]
Filename: "{app}\DIY Codex Bubble.exe"; Parameters: "--uninstall-startup"; Flags: runhidden; RunOnceId: "RemoveOwnedStartup"

[InstallDelete]
; Remove obsolete bundled runtimes when upgrading to the online build.
Type: filesandordirs; Name: "{app}\runtime"

[Code]
function IsBubbleUpdate: Boolean;
begin
  Result := ExpandConstant('{param:BUBBLEUPDATE|0}') = '1';
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ExitCode: Integer;
begin
  Result := '';
  ExtractTemporaryFile('Bubble Upgrade Helper.exe');
  if not Exec(ExpandConstant('{tmp}\Bubble Upgrade Helper.exe'),
    '--stop-owned-service "' + ExpandConstant('{app}') + '"', '', SW_HIDE,
    ewWaitUntilTerminated, ExitCode) or (ExitCode <> 0) then
    Result := 'Cannot stop the workshop background service. Restart Windows and try again. / 无法关闭工坊后台服务，请重启 Windows 后再安装。';
end;
