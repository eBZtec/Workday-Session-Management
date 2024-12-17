!define ServiceName "WSM-Windows-Service"
!define ServiceExeName "SessionService.exe"

!include "MUI2.nsh"

!define MUI_ICON "C:\Users\Developer2\Pictures\installer.ico"

RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Name "WSM Service Setup"
OutFile "WSM Service Setup.exe"

InstallDir "$PROGRAMFILES32\eBZ Tecnologia\Workday Session Management\${ServiceName}"

Section "Install"
    ; Set the install directory
    SetOutPath "$INSTDIR"
    
    ; Copy the service executable
    File /r "E:\Repositories\Gabriel\Workday_Session_Management\WSM-agent-windows\WSM-agent-windows-management_service\bin\Release\*"
    
    ; Install the service using the 'sc create' command
    nsExec::ExecToLog 'sc create "${ServiceName}" binPath= "$INSTDIR\${ServiceExeName}" start= auto'

    ; Start the service
    nsExec::ExecToLog 'sc start "${ServiceName}"'

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Write uninstall registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayName" "Workday Session Management - Windows Service"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayIcon" "$INSTDIR\SessionService.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "Publisher" "eBZ Tecnologia"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayVersion" "1.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "NoRepair" 1
SectionEnd

Section "Uninstall"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}"

    ; Stop the service
    nsExec::ExecToLog 'sc stop ${ServiceName}'

    Sleep 25000

    ; Delete the service
    nsExec::ExecToLog 'sc delete ${ServiceName}'

    Sleep 5000

    Delete "$INSTDIR\*.*"

    RMDir "$INSTDIR"
    RMDir /r "$INSTDIR\*"

SectionEnd