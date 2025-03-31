!define ServiceName "WSM-Windows-Service"
!define ServiceExeName "SessionService.exe"
!define ProductName "Workday Session Management Windows Desktop Agent Service"

!include "MUI2.nsh"

!include FileFunc.nsh

!define MUI_ICON "wsm-service-install.ico"
!define MUI_UNICON "wsm-service-uninstall.ico"

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
    File /r "${__FILEDIR__}\..\..\..\WSM-agent-windows\WSM-agent-windows-management_service\publish\*"

    ; Install the service using the 'sc create' command
    nsExec::ExecToLog 'sc create "${ServiceName}" binPath= "$INSTDIR\${ServiceExeName}" start= auto'

    ; Start the service
    nsExec::ExecToLog 'sc start "${ServiceName}"'

    ; Add service description
    nsExec::ExecToLog 'sc description "${ServiceName}" "This service connects to Workday Session Management Router to manage users sessions"'
    
    ; Add service display name
    nsExec::ExecToLog 'sc config "${ServiceName}" DisplayName= "${ProductName}"'

    ; Calculate the size of the installation directory
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2

    ; Write uninstall information with dynamic size
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "EstimatedSize" $0

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Write uninstall registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayName" "Workday Session Management - Windows Service"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayIcon" "$INSTDIR\SessionService.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "Publisher" "eBZ Tecnologia"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayVersion" "1.0.2"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "NoRepair" 1
SectionEnd

Section "Uninstall"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}"

    ; Stop the service
    nsExec::ExecToLog 'sc stop ${ServiceName}'

    Sleep 30000

    ; Delete the service
    nsExec::ExecToLog 'sc delete ${ServiceName}'

    Sleep 5000

    Delete "$INSTDIR\*.*"

    RMDir "$INSTDIR"
    RMDir /r "$INSTDIR\*"

SectionEnd
