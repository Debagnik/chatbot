; -- nijika_installer.iss --

[Setup]
AppName=Roleplay Chatbot
AppVersion=0.0.1-Dev-Preview
DefaultDirName={pf}\NijikaChat
DefaultGroupName=NijikaChat
OutputDir=dist
OutputBaseFilename=chatbot_installer_dev
Compression=lzma
SolidCompression=yes
LicenseFile=LICENSE.txt
SetupIconFile=nijika.ico


[Files]
Source: "dist\nijika_chat.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "character.json"; DestDir: "{app}"
Source: ".env"; DestDir: "{app}"


[Icons]
Name: "{group}\Nijika Chat"; Filename: "{app}\nijika_chat.exe"
Name: "{commondesktop}\Nijika Chat"; Filename: "{app}\nijika_chat.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"
