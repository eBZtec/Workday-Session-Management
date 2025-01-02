
# WSM Router

## Module Definition
**WSM** application responsible for updating the audit database.

---

### Project
- **Name**: Workday Session Management - WSM
- **Document**: Documentation
- **Version**: 1.0
- **Date**: 12/26/2024
- **Author**: Douglas Alves

---

## Introduction
This document presents the proposed design for implementing a Python service responsible for updating the audit database.

---

## Business Overview
This component facilitates the management of work hours in the WSM application by consuming messages from the RabbitMQ queue sent by **WSM Router** and saving them in the audit database.

---

## Service Definition

### Work Hours Update Message Routing (Input)
The Python service saves messages from the Router regarding client sessions that were started and ended.

#### Input Example:

```json
{
   "table": "SessionsAudit",
   "data": {
       "hostname": "WIN-BE7UR9NV6LS",
       "event_type": "logon",
       "login": "Developer2",
       "status": "active",
       "start_time": "2024-12-26T16:28:09.0240139+00:00",
       "end_time": null,
       "os_version": "10.0.20348",
       "os_name": "Microsoft Windows 10.0.20348",
       "ip_address": "10.121.102.15",
       "client_version": "1.2.0.0",
       "agent_info": "Default WSM Service installation"
   }
}
```

#### Attribute Structure:

| **Attribute**       | **Type** | **Required**    | **Description**                                     |
|---------------------|----------|-----------------|---------------------------------------------------|
| `action`           | String   | Yes             | Type of action to be taken by the service.         |
| `hostname`         | String   | Yes             | Hostname linked to the user session.              |
| `event_type`       | String   | Yes             | "logout" if the session event was a logout or "logon" if it was a logon. |
| `login`            | String   | Yes             | UID or username of the user linked to the session. |
| `status`           | String   | Yes             | Session status, can be "active" or "deactivated".  |
| `start_time`       | String   | No              | The time the session started.                     |
| `end_time`         | String   | No              | The time the session ended.                       |
| `os_version`       | String   | No              | The operating system version used.                |
| `ip_address`       | String   | Yes             | IP address linked to the session.                 |
| `client_version`   | String   | Yes             | Client version linked to the session.             |
| `agent_info`       | String   | Yes             | General agent information.                        |

---

## Implementation

### Module Installation

#### Steps:
1. Copy the directory containing the module to the project directory:
   ```bash
   cp -r /WSM-Archive-Processor <project-directory>
   ```

2. Set up the virtualenv using Python 3.12:
   ```bash
   python3.12 -m venv venv/
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Install the libraries from the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the Python service:
   ```bash
   python3.12 main.py
   ```

If the procedure is successful, the module will start reading the RabbitMQ queue.

---

© 2024 TECHNOLOGY
 
