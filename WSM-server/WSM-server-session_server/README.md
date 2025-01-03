# WSM Session Server API

## Project Details
- **Name**: WSM Session Server API
- **Document**: Documentation
- **Version**: 1.0
- **Date**: 12/30/2024
- **Author**: Jean Michel Santos

---

## Introduction
The **WSM Session Server API** is a REST service fully written in Python version 3.12, using the FastAPI framework. It manages work schedules for WSM accounts.

This resource allows managing work schedules, including extensions, user lock or unlock, and sending notifications to users on the workstations they are connected to.

Asynchronously, any changes made using the WSM Session Server API reflect in the application's pre-configured services, such as **WSM Agent** and **WSM Connector AD**, where work schedules are recalculated with active extensions and sent to the applications.

---
# API

## WSM Accounts
WSM accounts are used to calculate a user's work schedule. This object contains all the necessary information to determine whether a user can work during a specific period.

Any changes to the account are automatically synchronized with all services managed by WSM.

---

### Account Creation

This resource allows registering a new account in WSM and configuring the work schedule based on the registration data.

For each new account created, the process will automatically update the schedule in all services the user has enabled in WSM, such as updating "Logon Hours" in Active Directory and/or sending an updated work schedule to all WSM agents on the stations where the user is authenticated.

#### Request
```http
POST /wsm/api/v1/account/
Host: {Environment URL}
Content-Type: application/json

{
 "uid": "<User UID>",
 "start_time": "08:00",
 "end_time": "17:00",
 "uf": "BR",
 "st": "SP",
 "c": 25,
 "weekdays": "0111110",
 "session_termination_action": "logoff",
 "cn": "<User's full name>",
 "l": "Address",
 "enable": true,
 "unrestricted": false
}
```

#### Response
- **HTTP 200 OK**: Account successfully registered
- **HTTP 400 Bad Request**: Invalid attributes

---

### Attribute Schema

| **Attribute**                | **Type** | **Required** | **Description**                                                                       |
|------------------------------|----------|--------------|---------------------------------------------------------------------------------------|
| `uid`                       | String   | Yes          | User login                                                                            |
| `start_time`                | String   | Yes          | Start time of the schedule in HH:MM format                                           |
| `end_time`                  | String   | Yes          | End time of the schedule in HH:MM format                                             |
| `uf`                        | String   | Yes          | Federal Unit                                                                         |
| `st`                        | String   | Yes          | State where the user resides                                                         |
| `c`                         | Integer  | Yes          | City code                                                                            |
| `weekdays`                  | String   | Yes          | Days the user can work (0: blocked, 1: allowed, starting on Sunday)                  |
| `session_termination_action` | String | No           | Action when authenticating to a station when not enabled (default: "logoff")         |
| `cn`                        | String   | Yes          | User's full name                                                                     |
| `l`                         | String   | Yes          | User's address                                                                       |
| `enable`                    | Boolean  | No           | Whether the user is enabled or disabled (default: true)                              |
| `unrestricted`              | Boolean  | No           | Enables unrestricted schedule (default: false)                                      |
| `deactivation_date`         | Date     | No           | Deactivation date in the format YYYY-MM-DDTHH:MM:SS                                  |

---

### Update

This resource recalculates a user's work schedule based on changes made.

It can lock/unlock an account, modify the schedule, change workweek days, add or remove a termination date, and/or transform the schedule to unrestricted.

For all these updates, the updated user schedule, accounting for holidays and schedule extensions, is sent to the services.

#### Request
```http
PUT /wsm/api/v1/account/
Host: {Environment URL}
Content-Type: application/json

{
 "uid": "<User UID>",
 "start_time": "08:00",
 "end_time": "17:00",
 "uf": "BR",
 "st": "SP",
 "c": 25,
 "weekdays": "0111110",
 "session_termination_action": "logoff",
 "cn": "<User's full name>",
 "l": "Address",
 "enable": true,
 "unrestricted": false
}
```

#### Response
- **HTTP 200 OK**: Account successfully updated
- **HTTP 400 Bad Request**: Invalid attributes

---

### Disable Account
This resource disables a user in the WSM database.

The registered user's schedule will be entirely ignored by the service, and the user's schedule will be blocked on all days of the week.

The newly calculated schedule values will be inserted into the database and sent asynchronously to services in Active Directory and WSM Agent where the user has active sessions.

#### Request
```http
POST /wsm/api/v1/account/{uid}/disable
Host: {Environment URL}
Content-Type: application/json
```

- `{uid}`: User login to be disabled.

#### Response
- **HTTP 200 OK**: Account successfully disabled
- **HTTP 400 Bad Request**: Invalid attributes

---

### Enable

This resource enables a user in the WSM database.

The schedule will be calculated based on the user's account data in WSM and sent asynchronously to Active Directory services and WSM Agents where the user has active sessions.

#### Request

```http
POST /wsm/api/v1/account/{uid}/enable
HOST {Environment URL}
Content-Type: application/json
```
- `{uid}`: User login to be enabled.

#### Response
- **HTTP 200 OK**: Account successfully enabled
- **HTTP 400 Bad Request**: Invalid attributes

---

### Logoff

Allows logging off a user from a specific station via the host. An asynchronous command is sent to the WSM Agent, which performs the user's logoff on the station.

#### Request

```http
POST /wsm/api/v1/account/{uid}/logoff/{host}
HOST {Environment URL}
Content-Type: application/json
```
 - `{uid}` : User login to be logged off
 - `{host}` : Host or IP of the station where the user will be logged off


#### Response
- **HTTP 200 OK**: Logoff successful
- **HTTP 400 Bad Request**: Invalid attributes

---

### User Search
This method retrieves a user's registered data from the WSM database via the UID (login), including the user's active schedule extensions and service update status.

The update status indicates whether the user's data is updated in the services. If the update status timestamp is greater than or equal to the WSM account update timestamp, the user's data is synchronized.

#### Request
```http
POST /wsm/api/v1/account/{uid}
HOST {Environment URL}
Content-Type: application/json
```

- `{uid}` : User login to be searched.

#### Response
- **HTTP 200 OK**: Search executed successfully
- **HTTP 400 Bad Request**: Invalid attributes

---

### Work Schedule Extensions

Work schedule extensions provide additional working time beyond the user's standard schedule.

In this WSM component, you can define new extensions, modify extensions, disable extensions, and search for active extensions by user.

The work schedule calculation considers only active extensions within the current time period; old or disabled extensions are ignored. Similar to WSM accounts, each insertion or modification of schedule extensions recalculates the user's work schedule and automatically synchronizes the updated information with WSM-managed services.

#### Extension Creation

The process of creating a schedule extension inserts a new extension into the database, which will be used in calculating the user's work schedule.

#### Request
```http
POST /wsm/api/v1/overtime/
Host: {Environment URL}
Content-Type: application/json

{
 "uid": "<User UID>",
 "extension_start_time": "2024-12-26T20:00:00",
 "extension_end_time": "2024-12-26T21:00:00",
 "extension_active": true
}
```

#### Response
- **HTTP 200 OK**: Extension successfully created
- **HTTP 400 Bad Request**: Invalid attributes

### Update
This process updates a schedule extension already registered in the system. It allows modifying the schedule, enabling, or disabling the extension.

#### Request
```http
PUT /wsm/api/v1/overtime/
Host: {Environment URL}
Content-Type: application/json

{
 "uid": "<User UID>",
 "extension_start_time": "2024-12-26T20:00:00",
 "extension_end_time": "2024-12-26T21:00:00",
 "extension_active": true
}
```

#### Response
- **HTTP 200 OK**: Successfully updated
- **HTTP 400 Bad Request**: Invalid attributes

### Request Body

| **Attribute**                | **Type** | **Required** | **Description**                                                                       |
|-----------------------------|----------|--------------|---------------------------------------------------------------------------------------|
| `uid`                       | String   | Yes          | User login                                                                            |
| `extension_start_time`      | String   | Yes          | Start time of the schedule extension. The exact date and time the extension begins must be specified.<br> Format: YYYY-mm-ddTHH:MM:SS <br> Y – year <br> m - month <br> d - day <br> H - hour <br> M - minute <br> S - second <br> Example: 2024-12-26T20:00:00 |
| `extension_end_time`        | String   | Yes          | End time of the schedule extension. The exact date and time the extension ends must be specified.<br> Format: YYYY-mm-ddTHH:MM:SS <br> Y – year <br> m - month <br> d - day <br> H - hour <br> M - minute <br> S - second <br> Example: 2024-12-26T20:00:00 <br> Note: To set the extension end date to the next day, simply change the day to the following day. |
| `extension_active`          | String   | Yes          | Flag used to determine whether an extension is active. The extension will be ignored in the work schedule calculation if deactivated. <br> Default: True (active) |

---

### Search Active Schedule Extensions by User

This method allows viewing all active schedule extensions for a user by login. Old extensions, i.e., those with invalid times or inactive extensions, will not be returned.

#### Request

```http
GET /wsm/api/v1/overtime/account/{account_id}
HOST {Environment URL}
Content-Type: application/json

```

`{account_id}` – User login to be searched.

#### Response
- **HTTP 200 OK**: Search executed successfully
- **HTTP 400 Bad Request**: Invalid attributes

```
[
  {
    "uid": "string",
    "extension_start_time": "2024-12-30T13:54:01.112Z",
    "extension_end_time": "2024-12-30T13:54:01.112Z",
    "extended_workhours_type": "string",
    "uf": "string",
    "c": 0,
    "week_days_count": "string",
    "extension_active": 0,
    "ou": 0,
    "id": 0
  }
]
```

### Notifications for WSM Agent

This method opens a direct channel with the WSM agent, notifying the user on the station they are connected to.

The message displayed will be sent in the request and will appear on the user's screen as a notification. If the user has more than one active session, the notification will appear on all of them.

#### Request
```http
POST /wsm/api/v1/agent/action
HOST {Environment URL}
Content-Type: application/json
```

#### Response
- **HTTP 200 OK**: Notification successfully sent
- **HTTP 400 Bad Request**: Invalid attributes

```
[
  {
    "uid": "string",
    "extension_start_time": "2024-12-30T13:54:01.112Z",
    "extension_end_time": "2024-12-30T13:54:01.112Z",
    "extended_workhours_type": "string",
    "uf": "string",
    "c": 0,
    "week_days_count": "string",
    "extension_active": 0,
    "ou": 0,
    "id": 0
  }
]
```
 
