; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

[Setup]
AppName=Gertrude
AppVerName=Gertrude 0.54
DefaultDirName={pf}\Gertrude
DefaultGroupName=Gertrude
OutputBaseFilename=setup
Compression=lzma
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Files]
Source: "dist\*"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\bitmaps\*"; DestDir: "{app}\bitmaps"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\templates\*"; DestDir: "{app}\templates"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\Gertrude"; Filename: "{app}\gertrude.exe"; WorkingDir: "{app}"
Name: "{userdesktop}\Gertrude"; Filename: "{app}\gertrude.exe"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\gertrude.exe"; Description: "{cm:LaunchProgram,Gertrude}"; Flags: nowait postinstall skipifsilent

