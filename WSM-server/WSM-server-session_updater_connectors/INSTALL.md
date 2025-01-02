Creating the wsm_session_updater_connectors Service

1 - In the root directory of wsm_session_updater_connectors, include the .env file:

    touch .env

```
DB_URI=postgresql://<user>:<password>@host:<port>/<session_database_name>
RABBITMQ_HOST=localhost
RABBITMQ_QUEUE_IN=pooling
RABBITMQ_SESSION_AGENT_QUEUE_NAME=session_agent
```

2 - As root, create the .service file and insert the following content:

    touch wsm_session_updater_connector.service

```
[Unit]
Description=WSM Session Updater Connectors Service - This service consumes the queue named pooling
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/Workday_Session_Management/WSM-server/WSM-server-session_updater_connectors
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

3 - Copy the service file to the system services directory and restart the services:

    systemctl daemon-reload
    systemctl start wsm_session_updater_connector.service
    systemctl enable wsm_session_updater_connector.service
