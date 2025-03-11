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
- **Framework**: .NET 8.0 or higher.
- **Dependencies**:
  - [Newtonsoft.Json](https://www.nuget.org/packages/Newtonsoft.Json/)
  - [BouncyCastle.Cryptography](https://www.nuget.org/packages/BouncyCastle.Cryptography/)
  - [System.DirectoryServices](https://learn.microsoft.com/en-us/dotnet/api/system.directoryservices)
  - [Microsoft.Extensions.Hosting.WindowsServices](https://www.nuget.org/packages/Microsoft.Extensions.Hosting.WindowsServices/)

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
6. Install and run the Windows Service:
  - The installation is done using **NSIS** (Nullsoft Scriptable Install System). To generate a new installer, you need to have NSIS installed and run the `.nsi` script file provided (`WsmConnectorAdInstallerScript.nsi`).
  - If you do not want to create a new installer, you can directly run the `.exe` file generated in the project.


- **Active Directory Host**:
  Ensure the `ACTIVE_DIRECTORY_HOST` registry value is set correctly. The application uses this value to connect to the AD domain.

## Usage
- Define user schedules as JSON:
  ```json
  {
    "uid": "jdoe",
    "allowed_work_hours": {
      "MONDAY": [{ "start": 480, "end": 1020 }],
      "TUESDAY": [{ "start": 480, "end": 1020 }]
    }
  }
  ```
- Use the `AdManager` class to apply schedules to AD users.

## Error Handling
- Errors and warnings are logged to the Windows Event Viewer.
- Examples include issues with AD authentication, user not found, or invalid schedules.