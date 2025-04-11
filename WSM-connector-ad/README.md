# WSM Connector AD

## Full documentaion
[Check full documentation](WSM-Connector-AD-v1.0.0.pdf)

## Overview
The **WSM Connector AD** is a .NET-based project designed to manage and update user permissions and schedules in an Active Directory (AD) environment. It provides capabilities to interact with Active Directory and update logon hours for users.

## Features
- **Active Directory Integration**:
  - Authenticate and interact with Active Directory.
  - Search for users by their username.
  - Update user logon hours based on a schedule provided in JSON format.

- **Custom Schedule Management**:
  - Define allowed working hours using a flexible JSON structure.
  - Automatically convert time zones and ensure schedules are properly applied.

- **Logging and Error Handling**:
  - Log activities and errors to the Windows Event Viewer for easy monitoring.
  - Detailed logging of operations, including schedule application and AD interactions.

- **Windows Service**:
  - Runs as a Windows Service for continuous background operations.

## Prerequisites
- **Operating System**: Windows with Active Directory configured.
- **Framework**: [.NET 8.0 or higher](https://dotnet.microsoft.com/en-us/download).
- **NSIS**: [Nullsoft Scriptable Install System](https://nsis.sourceforge.io/Download), to create the installer.
- **Firewall**: The Windows service listens on **TCP port 44901** for incoming requests.
  - Make sure **port 44901** is **open in the Windows Firewall**.
  - Allow inbound connections to this port on any machine running the service.

## Project Structure

### Key Components
- **`Controller/Program.cs`**:
  - Entry point of the application. Sets up the Windows Service and initializes the worker.

- **`ActiveDirectory/AdManager.cs`**:
  - Handles Active Directory interactions, such as updating logon hours and searching for users.

- **`Utils`**:
  - Contains utility classes for cryptography, logging, and other supporting operations.

### Build and Run
1. Clone the repository:
```bash
git clone <repository-url>
```
2. Open the solution (`WSM-connector-ad.sln`) in Visual Studio.
3. Restore NuGet packages:
```bash
dotnet restore
```
4. Build the solution:
```bash
dotnet build
```
5. Publish the application:
```bash
dotnet publish -c Release
```

### Instalation

The installation is done using **NSIS**. To generate a new installer, you need to have NSIS installed and run the `.nsi` script file provided (`WsmConnectorAdInstallerScript.nsi`).
    
If you do not want to create a new installer, you can directly run the `.exe` file generated in the project.

#### Parameters

1. `ACTIVE_DIRECTORY_HOST`: ensure value is set correctly. The application uses this value to connect to the AD domain.

2. `SESSION_SERVER_HOST`: ensure value is set correctly. The format is `<session_server_host>:<port>`.


## Configuring Domain User for "Log on as a service"

To run the Windows service under a **domain user account**, the account must be granted the **“Log on as a service”** right and have specific **Active Directory permissions**.

### Step 1: Grant “Log on as a service” Right

#### Using Local Security Policy:

1. Open `secpol.msc` on the machine hosting the service
2. Navigate to:
   ```
   Local Policies → User Rights Assignment → Log on as a service
   ```
3. Add your **domain user account** (e.g., `CORP\ad-service-user`)
4. Click **Apply** and **OK**

> If managed by Group Policy (GPO), update it in Group Policy Management (`gpmc.msc`).

---

### Step 2: Restart the Service

After assigning the logon right, **restart the Windows service** for the change to take effect.

```powershell
Restart-Service -Name "YourServiceName"
```

---

## Required Active Directory Permissions

The domain user running the service must have permission to manage user accounts.

### Minimum required permissions:

| Operation                | Required AD Permission                      |
|--------------------------|---------------------------------------------|
| **Update logon hours**   | Write to the `logonHours` attribute         |
| **Enable/Disable account** | Write to the `userAccountControl` attribute |
| **Unlock account**       | Reset `lockoutTime` attribute or use unlock control |

> Delegate permissions via AD Users and Computers:
>
> 1. Right-click the **OU** → **Delegate Control**
> 2. Select the user/service account
> 3. Choose **“Create a custom task to delegate”**
> 4. Choose **User objects**
> 5. Assign the necessary permissions

---

## Verify Effective Permissions

To verify permissions:

1. Open **AD Users and Computers**
2. Right-click a target user → **Properties**
3. Go to the **Security** tab → **Advanced**
4. Open **Effective Access** → Select the service account → **View effective access**


## Usage

```json
{
  "uid": "jdoe",
  "allowed_work_hours": {
    "MONDAY": [{ "start": 480, "end": 1020 }],
    "TUESDAY": [{ "start": 480, "end": 1020 }]
  },
  "enable": true,
  "unlock": true
}
```
  
## Parameter Descriptions

| Parameter             | Type     | Description |
|-----------------------|----------|-------------|
| `uid`                 | `string` | The **username** (SAM account name) of the Active Directory user. Example: `"jdoe"` |
| `allowed_work_hours`  | `object` | A dictionary defining **logon time windows per day of the week**. Keys are day names in uppercase (e.g., `"MONDAY"`). Values are arrays of time ranges in minutes since midnight. |
| `start`               | `int`    | Start time in minutes after midnight. Example: `480` = `08:00 AM` |
| `end`                 | `int`    | End time in minutes after midnight. Example: `1020` = `05:00 PM` |
| `enable`              | `bool`   | Enables or disables the account. `true` enables the account, `false` disables it. |
| `unlock`              | `bool`   | If `true`, the account will be unlocked if it is currently locked out due to failed login attempts. |


## Error Handling
- Errors and warnings are logged to the Windows Event Viewer.
- Examples include issues with AD authentication, user not found, or invalid schedules.
