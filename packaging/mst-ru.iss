; Inno Setup script — wraps the PyInstaller one-folder payload (dist\mst-ru\)
; into a single, self-contained mst-ru-setup.exe.
;
; No Python, no .NET, no libraries are required on the target Windows 10/11 machine.
; Per-user install (no administrator rights, no UAC prompt). The patcher builds the
; translation from the player's OWN copy of the game; no game assets are shipped.
;
; Build (from the repository root, after `pyinstaller packaging\mst-ru.spec`):
;   iscc packaging\mst-ru.iss                 -> dist\mst-ru-setup.exe
;   iscc /DMyAppVersion=1.0.4 packaging\mst-ru.iss

#ifndef MyAppVersion
  #define MyAppVersion "1.0.4"
#endif
#ifndef MyBuildDate
  #define MyBuildDate "dev"
#endif
#define MyAppName "Metal Slug Tactics — Russian translation"
#define MyExeName "mst-ru.exe"

[Setup]
AppId={{8B9E7C4A-1F2D-4E6B-9A3C-7D5E1F0A2B3C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} (build {#MyBuildDate})
VersionInfoTextVersion={#MyAppVersion} (build {#MyBuildDate})
AppPublisher=superheher
AppPublisherURL=https://github.com/superheher/metal-slug-tactics-ru
AppSupportURL=https://github.com/superheher/metal-slug-tactics-ru
DefaultDirName={localappdata}\Programs\MST-RU
DefaultGroupName=Metal Slug Tactics RU
DisableProgramGroupPage=yes
DisableDirPage=auto
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
OutputDir=..\dist
OutputBaseFilename=mst-ru-setup
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
WizardImageFile=art\wizard-image.bmp
WizardImageStretch=yes
SetupIconFile=art\mst-ru.ico
UninstallDisplayName={#MyAppName}
UninstallDisplayIcon={app}\{#MyExeName}

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"

[Messages]
WelcomeLabel2=This will install the Russian translation for Metal Slug Tactics on your computer.%n%nIt finds your copy of the game and rebuilds the text and fonts from it — nothing is downloaded and no game assets are shipped. Please close the game before continuing.
FinishedLabel=Setup is complete. Leave the checkbox below ticked and click Finish — a console window will find your game and apply the Russian translation.
FinishedLabelNoIcons=Setup is complete. Leave the checkbox below ticked and click Finish — a console window will find your game and apply the Russian translation.

[Files]
Source: "..\dist\mst-ru\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Install / update the Russian translation"; Filename: "{app}\{#MyExeName}"
Name: "{group}\Revert to English"; Filename: "{app}\{#MyExeName}"; Parameters: "--revert"
Name: "{group}\Uninstall"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\{#MyExeName}"; Description: "Translate Metal Slug Tactics into Russian now"; Flags: postinstall skipifsilent
