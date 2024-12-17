!include "MUI2.nsh"

; Define the icon for the installer
!define MUI_ICON "C:\Users\Developer2\Pictures\installer.ico"

; Require administrative privileges
RequestExecutionLevel admin

; Define installer pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; Set installer name and output
Name "Workday Session Management - Windows Agent"
OutFile "WSM Setup.exe"

; Define installation directory
InstallDir "$PROGRAMFILES32\eBZ Tecnologia\Workday Session Management"

Section "Install Other Setups"
  ; Include the setups in the installer and extract them at runtime
  File /oname=$TEMP\DesktopAgentSetup.exe "C:\Users\Developer2\Desktop\setup build\desktop agent\WSM DesktopAgent Setup.exe"
  File /oname=$TEMP\WSMServiceSetup.exe "C:\Users\Developer2\Desktop\setup build\service\WSM Service Setup.exe"

  ; Run the first setup
  ExecWait '"$TEMP\DesktopAgentSetup.exe" /S' ; Use /S for silent installation if supported
  IfErrors 0 +2
  MessageBox MB_OK "Error installing Desktop Agent."

  ; Run the second setup
  ExecWait '"$TEMP\WSMServiceSetup.exe" /S'
  IfErrors 0 +2
  MessageBox MB_OK "Error installing WSM Service."

  ; Clean up temporary files
  Delete "$TEMP\DesktopAgentSetup.exe"
  Delete "$TEMP\WSMServiceSetup.exe"
SectionEnd
