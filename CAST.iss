; -- Example2.iss --
; Same as Example1.iss, but creates its icon in the Programs folder of the
; Start Menu instead of in a subfolder, and also creates a desktop icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=CAST
AppPublisher=GeoDa Center
AppPublisherURL=http://spatial.uchicago.edu/
AppSupportURL=http://spatial.uchicago.edu/
AppUpdatesURL=http://spatial.uchicago.edu/
AppSupportPhone=(480)965-7533
AppVersion=0.99(alpha)
DefaultDirName={pf}\GeoDa Software
DefaultGroupName=GeoDa Software
; Since no icons will be created in "{group}", we don't need the wizard
; to ask for a Start Menu folder name:
;DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\CAST.exe
Compression=lzma2
SolidCompression=yes
OutputDir=userdocs:Inno Setup Examples Output

[dirs]
Name:"{app}\examples"

[Files]
Source: "dist\CAST.exe"; DestDir: "{app}"
Source: "Microsoft.VC90.CRT.manifest"; DestDir: "{app}"
Source: "msvcm90.dll"; DestDir: "{app}"
Source: "msvcp90.dll"; DestDir: "{app}"
Source: "msvcr90.dll"; DestDir: "{app}"
;Source: "examples\tempe.shp"; DestDir: "{app}\examples"
;Source: "examples\tempe.dbf"; DestDir: "{app}\examples"
;Source: "examples\tempe.shx"; DestDir: "{app}\examples"
;Source: "examples\beats.shp"; DestDir: "{app}\examples"
;Source: "examples\beats.dbf"; DestDir: "{app}\examples"
;Source: "examples\beats.shx"; DestDir: "{app}\examples"


;Source: "Readme.txt"; DestDir: "{app}"; Flags: isreadme

[Icons]
Name: "{group}\CAST"; Filename: "{app}\CAST.exe"
;Name: "{commonprograms}\GeoDa Software"; Filename: "{app}\CAST.exe"
Name: "{commondesktop}\CAST"; Filename: "{app}\CAST.exe"
