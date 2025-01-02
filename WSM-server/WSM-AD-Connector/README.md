
# WSM Router

## Module Definition
**WSM** application responsible for updating client schedules in **Active Directory (AD)**.

---

### Project
- **Name**: Workday Session Management - WSM
- **Document**: Documentation
- **Version**: 1.0
- **Date**: 12/26/2024
- **Author**: Douglas Alves

---

## Introduction
This document presents the proposed design for implementing a Python service responsible for updating client work schedules, using a REST API via a queue in Active Directory. The service facilitates the process of updating and registering schedule extensions.

---

## Business Overview
This component simplifies work schedule management in the WSM application, consuming messages from the RabbitMQ queue sent by the **WSM Agent-Updater-Connector** and retransmitting them to the Active Directory service.

---

## Service Definition

### Forwarding Schedule Update Messages (Input)
The Python service distributes messages received from the ZeroMQ queue, whether they are schedule updates or direct messages for the client.

#### Input Example:

```json
{
  "action": "updateHours",
  "hostname": "WIN-BE7UR9NV6LS",
  "user": "Tester",
  "timezone": "UTC-03:00",
  "allowed_schedule": {
    "sunday": [{"start": 0, "end": 0}],
    "monday": [{"start": 0, "end": 0}],
    "tuesday": [{"start": 540, "end": 1080}],
    "wednesday": [{"start": 540, "end": 1080}],
    "thursday": [{"start": 540, "end": 1080}],
    "friday": [{"start": 540, "end": 1080}],
    "saturday": [{"start": 540, "end": 1080}]
  },
  "timestamp": "2024-11-21T15:30:00Z",
  "message": null,
  "title": null,
  "options": null
}
```

#### Attribute Structure:

| **Attribute**       | **Type** | **Required** | **Description**                                   |
|----------------------|----------|--------------|--------------------------------------------------|
| `action`            | String   | Yes          | Action type to be executed by the service.       |
| `hostname`          | String   | Yes          | Hostname linked to the user session.             |
| `timezone`          | String   | Yes          | Timezone of the current session.                 |
| `allowed_schedule`  | String   | Yes          | User's work schedule update.                     |
| `timestamp`         | String   | Yes          | Timestamp of when the message was sent.          |
| `message`           | String   | No           | Not used.                                        |
| `title`             | String   | No           | Not used.                                        |
| `options`           | String   | No           | Not used.                                        |
| `user`              | String   | Yes          | Login, UID, or user in the system.               |

---

### Forwarding Schedule Update Messages (Output)

After processing, the output will look like the example below:

```json
{
  "action": "updateHours",
  "hostname": "WIN-BE7UR9NV6LS",
  "user": "Tester",
  "timezone": "2024-12-26 10:45:31.767804-03:00",
  "unrestricted": true,
  "enable": true,
  "allowed_schedule": "{"MONDAY": [{"start": 0, "end": 1439}], "TUESDAY": [{"start": 0, "end": 1439}], "WEDNESDAY": [{"start": 0, "end": 1439}], "THURSDAY": [{"start": 0, "end": 1439}], "FRIDAY": [{"start": 0, "end": 1439}], "SATURDAY": [{"start": 0, "end": 1439}], "SUNDAY": [{"start": 0, "end": 1439}]}",
  "timestamp": "2024-12-26 10:45:31.767804-03:00",
  "message": null,
  "title": "Notification",
  "options": "yes_no"
}
```

**Note**: The actual communication between the Router and the Client uses encrypted messages.

---

## Implementation

### Module Installation

#### Steps:
1. Copy the module directory to the project directory:
   ```bash
   cp -r /WSM-AD-Connector <project-directory>
   ```

2. Set up the virtual environment using Python 3.12:
   ```bash
   python3.12 -m venv venv/
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```

4. Install the required libraries from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

5. Start the Python service:
   ```bash
   python3.12 main.py
   ```

If the procedure is successful, the module will start reading the RabbitMQ queue.

---

© 2024 TECNOLOGIA
