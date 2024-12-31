Creating the wsm_agent_updater Service

1 - In the root directory of wsm_session_updater_connectors, include the .env file:

    touch .env

```
DEV_DATABASE_URL=postgresql://wsm:password@localhost:5432/wsm_session_db
DEV_MQ_ADDRESS_HOST=localhost
DEV_MQ_HOST_PORT=5672
DEV_WORK_HOURS_QUEUE=work_hours_queue
DEV_ZEROMQ_URL=tcp://localhost:51555
Z_MQ_PORT=5555
RABBITMQ_HOST=localhost
RABBITMQ_QUEUE=session_agent
```

2 - Create the .service file:

    touch wsm_agent_updater.service

```
[Unit]
Description=WSM Agent Updater Connectors Service - Consumes the RabbitMQ queue session_agent and sends via 0MQ
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/Workday_Session_Management/WSM-server/WSM-server-agent_updater
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

3 - Copy the service file to the system services directory and restart the services:

    systemctl daemon-reload
    systemctl start wsm_agent_updater.service
    systemctl enable wsm_agent_updater.service
