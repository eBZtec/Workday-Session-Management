 
# WSM Agent Updater

## Definition of the Application Module
The WSM application module is responsible for updating the WSM Router.

---

## Project Details
- **Project**: Workday Session Management - WSM
- **Document**: Documentation
- **Version**: 1.0
- **Date**: 12/26/2024
- **Author**: Douglas Alves

---

## Introduction
This document aims to present the proposed design for implementing the Python service responsible for updating the work schedule component of the WSM Router. This service is a Python application that assists in the process of updating and registering schedule extensions.

---

## Business Vision
This component assists in managing work schedules from the perspective of the WSM application. Specifically, it reads from the RabbitMQ queue called "session_agent" populated by the WSM session-updater-connector and retransmits it to the WSM Router via a ZeroMQ queue.

---

## Service Definition

### Forwarding Messages (Input)
This Python service distributes messages from the RabbitMQ queue populated by the WSM session-updater-connector. These messages may be directed to the WSM Router, including direct messages to users or schedule registration/modification messages.

#### Example Input:
```json
b'{"_sa_instance_state": "<sqlalchemy.orm.state.InstanceState object>", "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}", "unrestricted": true, "uf": "BR", "enable": true, "st": "SP", "c": "2", "deactivation_date": null, "uid": "Tester", "weekdays": "0111110", "id": 2, "start_time": "08:00", "session_termination_action": "logoff", "create_timestamp": "2024-12-20 16:58:59.879569-03:00", "cn": "Tester", "update_timestamp": "2024-12-26 10:16:34.390265-03:00", "end_time": "18:00", "l": "enc"}'
```

### Attributes Definition

| **Attribute**               | **Type** | **Required** | **Description**                                                                 |
|-----------------------------|----------|--------------|---------------------------------------------------------------------------------|
| `end_time`                  | String   | Yes          | Time when the user finishes the workday.                                        |
| `start_time`                | String   | Yes          | Time when the user starts the workday.                                          |
| `allowed_work_hours`        | String   | Yes          | JSON string defining the client's work schedule.                                |
| `deactivation_date`         | String   | Yes          | Deactivation date of the user, if applicable.                                   |
| `uf`                        | String   | Yes          | Country abbreviation.                                                           |
| `st`                        | String   | Yes          | Federative unit where the employee operates.                                    |
| `c`                         | String   | Yes          | Municipality code where the employee operates.                                  |
| `weekdays`                  | String   | Yes          | Days of the week for schedule extensions: 0 = blocked, 1 = allowed.             |
| `session_termination_action`| String   | No           | If user logoff is required, this field receives the value "logoff".             |
| `unrestricted`              | String   | Yes          | `True` if the user has no work schedule restrictions.                           |
| `cn`                        | String   | Yes          | Common name of the client, generally the same as `uid`.                         |
| `uid`                       | String   | Yes          | User's UID in the system.                                                       |

---

### Forwarding Messages (Output)
Based on the example input, after processing, the output will be structured as follows:
```json
{"RoutingClientMessage": {"_sa_instance_state": "<sqlalchemy.orm.state.InstanceState object>", "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}", "unrestricted": true, "uf": "BR", "enable": true, "st": "SP", "c": "2", "deactivation_date": null, "uid": "Tester", "weekdays": "0111110", "id": 2, "start_time": "08:00", "session_termination_action": "logoff", "create_timestamp": "2024-12-20 16:58:59.879569-03:00", "cn": "Tester", "update_timestamp": "2024-12-26 10:16:34.390265-03:00", "end_time": "18:00", "l": "enc"}}
```

---

## Implementation

### Module Installation
This step ensures the proper setup of the RabbitMQ queue reader.

1. Copy the module directory to the project directory:
   ```bash
   cp -r /WSM-server-agent_updater <project_directory>
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
