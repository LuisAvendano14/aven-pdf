; Instalador profesional de Aven PDF (Inno Setup) — todo en español,
; sin administrador, con elección de carpeta e icono automático.
[Setup]
AppId={{B7A51C2E-3D4F-4E5A-9B6C-1A2B3C4D5E6F}
AppName=Aven PDF
AppVersion=1.15
CloseApplications=yes
RestartApplications=no
AppPublisher=Aven
DefaultDirName={localappdata}\AvenPDF
DefaultGroupName=Aven PDF
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=out
OutputBaseFilename=AvenPDF_Setup
SetupIconFile=app\aven.ico
UninstallDisplayIcon={app}\app\aven.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear un icono en el &escritorio"; GroupDescription: "Iconos adicionales:"; Flags: checkedonce

[Files]
Source: "build\payload\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\Aven PDF"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app\aven_pdf.py"" --ventana"; WorkingDir: "{app}\app"; IconFilename: "{app}\app\aven.ico"; Comment: "Editor de PDF"
Name: "{group}\Desinstalar Aven PDF"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Aven PDF"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app\aven_pdf.py"" --ventana"; WorkingDir: "{app}\app"; IconFilename: "{app}\app\aven.ico"; Comment: "Editor de PDF"; Tasks: desktopicon

[Run]
Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\app\aven_pdf.py"" --ventana"; WorkingDir: "{app}\app"; Description: "Abrir Aven PDF ahora"; Flags: nowait postinstall skipifsilent

[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
  DetectCmd, KillCmd: String;
begin
  Result := '';
  DetectCmd := '-NoProfile -Command "$p = Get-Process pythonw,python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like ''' + ExpandConstant('{app}') + '*'' }; if ($p) { exit 10 } else { exit 0 }"';
  if Exec('powershell.exe', DetectCmd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 10) then
  begin
    if MsgBox('Aven PDF esta abierto en este momento.' + #13#10 + #13#10 +
              'Cierro la ventana anterior y continuo con la instalacion?',
              mbConfirmation, MB_OKCANCEL) = IDOK then
    begin
      KillCmd := '-NoProfile -Command "Get-Process pythonw,python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like ''' + ExpandConstant('{app}') + '*'' } | Stop-Process -Force"';
      Exec('powershell.exe', KillCmd, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
      Sleep(900);
    end
    else
      Result := 'Instalacion cancelada: cierra Aven PDF y vuelve a ejecutar el instalador.';
  end;
end;
