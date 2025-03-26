# WSM Updater Connectors

## Definition of the Application Module
The WSM application module is responsible for updating connectors.

---

## Project Details
- **Project**: REST API for CJT Integrator
- **Document**: Documentation
- **Version**: 1.0
- **Date**: 12/26/2024
- **Author**: Douglas Alves

---

## Introduction
This document aims to present the proposed design for implementing the Python service responsible for updating work schedules of connectors. This service assists in the process of updating and registering schedule extensions.

---

## Business Vision
This component assists in managing work schedules from the perspective of the WSM application. It reads from the RabbitMQ queue named "account pooling" and, based on the services registered in the database for the user, sends messages to the queue with the user's schedule.

---

## Service Definition

### Message Routing
This Python service distributes messages originating from the API. These messages may be directed to the WSM Router, such as direct messages to users, or work schedule registration/modification messages destined for the WSM Router via the "session_agent" queue or other services, such as the specific queue for Active Directory (AD).

#### Example Input: Message to the User
```json
{"action": "Notify", "user": "Tester", "title": "Notification", "message": "Some message"}
```

### Attribute Definitions

| **Attribute** | **Type** | **Required** | **Description** |
|--------------|----------|--------------|------------------|
| `action`     | String   | Yes          | Type of action linked to the record in the queue. Example: `Notify` for direct user messages. |
| `user`       | String   | Yes          | Name of the user who will receive the message. |
| `title`      | String   | Yes          | Title of the message displayed to the user. |
| `message`    | String   | Yes          | Body of the message sent to the user. |

---

#### Example Input: Work Schedule Registration/Update
```json
{
 "end_time": "18:00",
 "l": "enc",
 "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}\",
 "unrestricted": true,
 "uf": "BR",
 "enable": true,
 "st": "SP",
 "c": "2",
 "deactivation_date": null,
 "uid": "Tester",
 "weekdays": "0111110",
 "start_time": "08:00",
 "session_termination_action": "logoff",
 "create_timestamp": "2024-12-20 16:58:59.879569-03:00",
 "cn": "Tester",
 "update_timestamp": "2024-12-23 13:55:52.240257-03:00"
}
```

### Attribute Definitions

| **Attribute**                | **Type** | **Required** | **Description** |
|-----------------------------|----------|--------------|------------------|
| `end_time`                  | String   | Yes          | Time when the user ends the workday. |
| `start_time`                | String   | Yes          | Time when the user starts the workday. |
| `allowed_work_hours`        | String   | Yes          | JSON string containing the client's work schedule. |
| `deactivation_date`         | String   | Yes          | Deactivation date of the user, if applicable. |
| `uf`                        | String   | Yes          | Country abbreviation. |
| `st`                        | String   | Yes          | Federative unit where the employee operates. |
| `c`                         | String   | Yes          | Municipality code where the employee operates. |
| `weekdays`                  | String   | Yes          | Days of the week applied to schedule extensions: 0 = blocked, 1 = allowed. |
| `session_termination_action`| String   | No           | Value "logoff" if the user needs to terminate the session. |
| `unrestricted`              | String   | Yes          | `True` if the user has no schedule restrictions. |
| `cn`                        | String   | Yes          | Common name of the client, usually the same as `uid`. |
| `uid`                       | String   | Yes          | UID of the user in the system. |

---

## Implementation

### Module Installation
This step ensures proper configuration of the RabbitMQ queue reader.

1. Copy the module directory to the project directory:
   ```bash
   cp -r /WSM-server-session_updater_connectors <project_directory>
   ```

2. Configure the virtual environment using Python 3.12 and install the required libraries:
   ```bash
   python3.12 -m venv venv/
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the Python service:
   ```bash
   python3.12 main.py
   ```

If successful, the module will start reading messages from the RabbitMQ queue.
 
