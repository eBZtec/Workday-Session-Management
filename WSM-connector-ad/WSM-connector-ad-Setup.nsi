!define ServiceName "WsmConnectorAd"
!define ServiceExeName "wsm-connector-ad.exe"
!define Manufacturer "eBZ Tecnologia"
!define ProductName "Workday Session Management Connector for Active Directory"

!define MUI_ICON "icon.ico"

!include "MUI2.nsh"
!include "nsDialogs.nsh"

RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
Page custom ShowInputPage LeaveInputPage
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"

Name "WsmConnectorAd_Setup"
OutFile "WsmConnectorAd_Setup.exe"

InstallDir "$PROGRAMFILES32\eBZ Tecnologia\Workday Session Management\${ServiceName}"

# Custom icon for the installer
Icon "icon.ico"

Var SESSION_SERVER_HOST
Var ACTIVE_DIRECTORY_HOST

Function ShowInputPage
    nsDialogs::Create 1018
    Pop $0
    ${If} $0 == error
        Abort
    ${EndIf}

    ; SESSION_SERVER_HOST Label
    ${NSD_CreateLabel} 10% 10u 80% 12u "Enter SESSION_SERVER_HOST:"
    Pop $1

    ; SESSION_SERVER_HOST Input
    ${NSD_CreateText} 10% 25u 80% 12u ""
    Pop $SESSION_SERVER_HOST

    ; ACTIVE_DIRECTORY_HOST Label
    ${NSD_CreateLabel} 10% 50u 80% 12u "Enter ACTIVE_DIRECTORY_HOST:"
    Pop $1

    ; ACTIVE_DIRECTORY_HOST Input
    ${NSD_CreateText} 10% 65u 80% 12u ""
    Pop $ACTIVE_DIRECTORY_HOST

    ; Show dialog
    nsDialogs::Show
FunctionEnd

Function LeaveInputPage
    ${NSD_GetText} $SESSION_SERVER_HOST $SESSION_SERVER_HOST
    ${NSD_GetText} $ACTIVE_DIRECTORY_HOST $ACTIVE_DIRECTORY_HOST

    ; Ensure inputs are not empty
    StrCmp $SESSION_SERVER_HOST "" EmptyInput
    StrCmp $ACTIVE_DIRECTORY_HOST "" EmptyInput
    Return

EmptyInput:
    MessageBox MB_OK "Both fields are required. Please enter valid details."
    Abort
FunctionEnd

Section "Install"
    ; Set the install directory
    SetOutPath "$INSTDIR"
    
    ; Copy the service executable and icon
    File /r "bin\Release\net8.0\*"
    File "icon.ico"
    
    ; Save parameters to registry
    SetRegView 64
    WriteRegStr HKLM "Software\${Manufacturer}\${ServiceName}" "SESSION_SERVER_HOST" "$SESSION_SERVER_HOST"
    WriteRegStr HKLM "Software\${Manufacturer}\${ServiceName}" "ACTIVE_DIRECTORY_HOST" "$ACTIVE_DIRECTORY_HOST"

    ; Install the service
    nsExec::ExecToLog 'sc create "${ServiceName}" binPath= "\"$INSTDIR\${ServiceExeName}\" SESSION_SERVER_HOST=$SESSION_SERVER_HOST ACTIVE_DIRECTORY_HOST=$ACTIVE_DIRECTORY_HOST" start= auto'
   
    ; Add service description
    nsExec::ExecToLog 'sc description "${ServiceName}" "This service connects to Workday Session Management for Active Directory integration."'
    
    ; Add service display name
    nsExec::ExecToLog 'sc config "${ServiceName}" DisplayName= "${ProductName}"'

    ; Start the service
    nsExec::ExecToLog 'sc start "${ServiceName}"'
    
    ; Write uninstall registry entries
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayName" "${ProductName}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayIcon" "$INSTDIR\icon.ico"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "Publisher" "${Manufacturer}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "DisplayVersion" "1.0.0.0"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}" "NoRepair" 1
SectionEnd

Section "Uninstall"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ServiceName}"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${ProductName}"
    
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
