 
# WSM Audit Server

## Definition of the Application Module
The WSM application module is responsible for extracting session reports.

---

## Project Details
- **Project**: Workday Session Management - WSM
- **Document**: Documentation
- **Version**: 1.0
- **Date**: 12/30/2024
- **Author**: Douglas Alves

---

## Introduction
This document aims to present the proposed design for implementing the API responsible for extracting reports related to client sessions.

---

## Business Vision
This component assists in managing work schedules from the WSM application's perspective, specifically by providing query endpoints for users and their sessions, as well as related information.

---

## API Definition
The API uses SQLAlchemy models to map database tables. Example model:

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SessionsAudit(Base):
    __tablename__ = 'session_audit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)
    login = Column(String(100), nullable=False)
    status = Column(String(50))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=True)
    os_version = Column(String(50), nullable=False)
    os_name = Column(String(50))
    ip_address = Column(String(100), nullable=False)
    client_version = Column(String(50), nullable=False)
    agent_info = Column(String(50))
```

---

### Querying Session and Client Information (Input)
This API service enables paginated queries on a database using dynamic filters. Filters are defined in JSON format, allowing flexibility in creating complex queries.

The API is designed to:
- Receive filters in JSON format.
- Translate these filters into SQLAlchemy expressions.
- Return paginated results.

#### Description
Receives filters and pagination parameters and returns paginated results.

##### Input (JSON):
```json
{
  "filters": [
    {"field": "hostname", "operator": "$eq", "value": "WIN-BE7UR9NV6LS"},
    {"field": "start_time", "operator": "$gte", "value": "2024-12-16"},
    {"field": "start_time", "operator": "$lte", "value": "2024-12-16T23:59:59"}
  ],
  "page": 1,
  "page_size": 10
}
```

##### Output (JSON):
```json
{
  "page": 1,
  "page_size": 10,
  "total_records": 2,
  "data": [
    {
      "id": 58,
      "hostname": "WIN-BE7UR9NV6LS",
      "event_type": "logon",
      "login": "Tester",
      "status": "active",
      "start_time": "2024-12-16T09:00:00Z",
      "end_time": null,
      "create_timestamp": "2024-12-16T09:00:00Z",
      "update_timestamp": "2024-12-16T09:00:00Z",
      "os_version": "10.0.20348",
      "os_name": "Microsoft Windows",
      "ip_address": "10.121.102.15",
      "client_version": "1.2.0.0",
      "agent_info": "Default WSM Service installation"
    }
  ]
}
```

---

### Supported Operators
Filters are defined in JSON and support operators such as $eq (equals), $gte (greater than or equal), $lte (less than or equal), $like (partial match), among others. Examples:

| **Operator** | **Description**              | **SQL Equivalent** | **Example**                                      |
|--------------|------------------------------|---------------------|-------------------------------------------------|
| `$eq`        | Equal                        | `=`               | `{ "field": "hostname", "operator": "$eq", "value": "WIN-BE7UR9NV6LS" }` |
| `$ne`        | Not equal                    | `!=`               | `{ "field": "status", "operator": "$ne", "value": "inactive" }`          |
| `$lt`        | Less than                    | `<`                | `{ "field": "start_time", "operator": "$lt", "value": "2024-12-16T00:00:00" }` |
| `$lte`       | Less than or equal to        | `<=`               | `{ "field": "start_time", "operator": "$lte", "value": "2024-12-16T23:59:59" }` |
| `$gt`        | Greater than                 | `>`                | `{ "field": "age", "operator": "$gt", "value": 30 }`                     |
| `$gte`       | Greater than or equal to     | `>=`               | `{ "field": "age", "operator": "$gte", "value": 30 }`                     |
| `$like`      | Partial match                | `LIKE`             | `{ "field": "login", "operator": "$like", "value": "%admin%" }`         |
| `$ilike`     | Case-insensitive match       | `ILIKE` (PostgreSQL)| `{ "field": "login", "operator": "$ilike", "value": "%Admin%" }`        |
| `$in`        | Within a list                | `IN`               | `{ "field": "status", "operator": "$in", "value": ["active", "pending"] }` |

Example of usage:

```json
[
  {"field": "hostname", "operator": "$eq", "value": "WIN-BE7UR9NV6LS"},
  {"logical": "OR", "conditions": [
    {"field": "status", "operator": "$eq", "value": "active"},
    {"field": "status", "operator": "$eq", "value": "disconnected"}
  ]}
]
```

---

## Implementation

### Module Installation
This step defines the functionality for reading the RabbitMQ queue.

1. Copy the module directory to the project directory:
   ```bash
   cp -r /WSM-AD-Connector <project_directory>
   ```

2. Configure the virtual environment using Python 3.12 and install the required libraries from `requirements.txt`:
   ```bash
   python3.12 -m venv venv/
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Start the Python service:
   - For development:
     ```bash
     fastapi dev main.py
     ```
   - For production:
     ```bash
     gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 main:app
     ```

If successful, the module will start the endpoints on the specified port.
