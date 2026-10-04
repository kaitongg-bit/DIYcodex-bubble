#ifndef AppVersion
  #define AppVersion "0.2.4"
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
OutputBaseFilename=DIYcodex-bubble-v{#AppVersion}-windows-x64-setup
SetupIconFile=..\..\dist\windows-app\assets\AppIcon.ico
UninstallDisplayIcon={app}\DIY Codex Bubble.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\..\dist\windows-app\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\DIY Codex Bubble"; Filename: "{app}\DIY Codex Bubble.exe"; WorkingDir: "{app}"
Name: "{autodesktop}\DIY Codex Bubble"; Filename: "{app}\DIY Codex Bubble.exe"; WorkingDir: "{app}"

[Run]
Filename: "{app}\DIY Codex Bubble.exe"; Description: "Open DIY Codex Bubble / 打开气泡工坊"; Flags: nowait postinstall skipifsilent

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var FileName, Content: String;
begin
  if CurUninstallStep = usUninstall then begin
    FileName := ExpandConstant('{userstartup}\DIY Codex Bubble Restore.vbs');
    if LoadStringFromFile(FileName, Content) and (Pos(ExpandConstant('{app}'), Content) > 0) then
      DeleteFile(FileName);
  end;
end;
