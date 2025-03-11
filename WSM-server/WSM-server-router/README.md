# WSM Router

## Application Module Definition
The WSM application module is responsible for updating client schedules, encryption, and messaging.

---

## Project Details
- **Project**: Workday Session Management - WSM
- **Document**: Documentation
- **Version**: 1.0
- **Date**: 12/26/2024
- **Author**: Douglas Alves

---

## Introduction
This document aims to present the proposed design for implementing the Python service responsible for updating encrypted client work schedules, sending encrypted messages to clients via the REST API and queue, and managing the Certification Authority for communications. This service assists in the process of updating and registering schedule extensions.

---

## Business Vision
This component assists in managing work schedules from the WSM application's perspective. Specifically, it reads from the ZeroMQ queue sent by the WSM agent-updater and retransmits it to clients, also using the ZeroMQ queue.

---

## Service Definition

### Forwarding Schedule Update Messages (Input)
This Python service distributes messages from the ZeroMQ queue populated by the WSM agent-updater. These messages may include a schedule update for the client or direct messages to the client.

#### Example Input:
```json
"RoutingClientMessage": {
    "_sa_instance_state": "<sqlalchemy.orm.state.InstanceState object>",
    "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}",",
    "unrestricted": true,
    "uf": "BR",
    "enable": true,
    "st": "SP",
    "c": "2",
    "deactivation_date": null,
    "uid": "Tester",
    "weekdays": "0111110",
    "id": 2,
    "start_time": "08:00",
    "session_termination_action": "logoff",
    "create_timestamp": "2024-12-20 16:58:59.879569-03:00",
    "cn": "Tester",
    "update_timestamp": "2024-12-26 10:45:31.767804-03:00",
    "end_time": "18:00",
    "l": "enc"
}
```

### Forwarding Schedule Update Messages (Output)
After processing, the output will be:
```json
{
    "action": "updateHours",
    "hostname": "WIN-BE7UR9NV6LS",
    "user": "Tester",
    "timezone": "2024-12-26 10:45:31.767804-03:00",
    "unrestricted": true,
    "enable": true,
    "allowed_schedule": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}",",
    "timestamp": "2024-12-26 10:45:31.767804-03:00",
    "message": null,
    "title": "Notification",
    "options": "yes_no"
}
```
The structure of the output message is just an example, as real communication between the Router and Client is encrypted.

---

### Forwarding Direct Messages (Input)
In addition to schedule updates, the service can send direct messages to clients.

#### Example Input:
```json
{"RoutingClientMessage": {"action": "Notify", "user": "Tester", "title": "Title", "message": "Message"}}
```

### Forwarding Direct Messages (Output)
After processing, the sent message will be structured as follows:
```json
{
    "action": "Notify",
    "hostname": "WIN-BE7UR9NV6LS",
    "user": "Tester",
    "timezone": "UTC",
    "unrestricted": true,
    "enable": true,
    "timestamp": "2024-12-26 10:45:31.767804-03:00",
    "message": "Message",
    "title": "Title",
    "options": "yes_no"
}
```

---

## Receiving Heartbeating Messages (Input)
Clients send messages to the Router to confirm Heartbeating communication and include a new user session.

#### Example Input:
```json
{
    "Heartbeat": {
        "hostname": "WIN-BE7UR9NV6LS",
        "ip_address": "10.121.102.15",
        "client_version": "1.2.0.0",
        "os_name": "Microsoft Windows 10.0.20348",
        "os_version": "10.0.20348",
        "agent_info": "Default WSM Service installation",
        "uptime": 90,
        "timezone": "-03:00:00"
    }
}
```

### Receiving Heartbeating Messages (Output)
As a response, the Router returns the following message:
```json
{"status": "beating", "message": "Done"}
```

---

## Sending Messages to the Audit Queue
The Router also sends messages to the audit queue containing data about sessions opened and closed in the session database.

#### Example Audit Message:
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

---

## Certification and Message Encryption Process
The server has its own Certification Authority (CA) to manage Certificate Signing Requests (CSRs). These CSRs are the first messages exchanged between the Router and clients, allowing for certificate signing and recognition.

- **WSM_SESSION_SERVER**: Router certificate containing the private key to decrypt received messages.
- **WSM_CA**: Self-signed certificate establishing the CA's identity.

The Router stores only clients' public keys in the database and uses these keys to encrypt messages. Communication between the Router and clients is guaranteed to be secure, with messages decrypted only by the intended recipients.

---

## Implementation

### Module Installation
1. Copy the module directory to the project:
   ```bash
   cp -r /WSM-router <project_directory>
   ```

2. Set up the virtual environment with Python 3.12:
   ```bash
   python3.12 -m venv venv/
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the Python service:
   ```bash
   python3.12 main.py
   ```

If successful, the module will start reading the RabbitMQ queue.
 
