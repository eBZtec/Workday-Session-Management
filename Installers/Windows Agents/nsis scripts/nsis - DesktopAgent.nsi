# Define the application name, version, and target directory
!define APP_NAME "WSM Desktop Agent"
!define APP_VERSION "1.0.1"
!define INSTALL_DIR "$PROGRAMFILES32\eBZ Tecnologia\Workday Session Management\${APP_NAME}"

# Include necessary NSIS plugins and scripts
!include "MUI2.nsh"

!include FileFunc.nsh

!define MUI_ICON "wsm-agent-install.ico"
!define MUI_UNICON "wsm-agent-uninstall.ico"

# Installer details
Name "${APP_NAME}"

# Output installer file
OutFile "WSM Desktop Agent Setup.exe"

# Target installation directory
InstallDir "${INSTALL_DIR}"

# Request administrative privileges
RequestExecutionLevel admin

# Define pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

# Define the sections
Section "Install"

    # Create installation directory
    SetOutPath "$INSTDIR"

    # Copy files
    File /r "${__FILEDIR__}\..\..\..\WSM-agent-windows\WSM-agent-windows-desktop_agent\publish\*.*"

    # Create a startup shortcut
    CreateShortCut "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\${APP_NAME}.lnk" "$INSTDIR\DesktopAgent.exe" ""


    ; Calculate the size of the installation directory
    ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2

    ; Write uninstall information with dynamic size
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "EstimatedSize" $0

    # Add an uninstaller
    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Write uninstall registry entries
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "Workday Session Management - Windows Desktop Agent"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\DesktopAgent.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "eBZ Tecnologia"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "1.0.1"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "InstallLocation" "$INSTDIR"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1

SectionEnd

Section "Uninstall"

    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    # Delete files
    Delete "$INSTDIR\*.*"
    
    # Remove shortcuts
    Delete "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup\${APP_NAME}.lnk"

    # Remove installation directory
    RMDir "$INSTDIR"
    RMDir /r "$INSTDIR\*"

SectionEnd

