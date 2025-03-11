Creating the wsm_session_server Service

    vim wsm_session_server.service

```
[Unit]
Description=WSM - Session Server API Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/Workday_Session_Management/WSM-server/WSM-server-session_server
LimitNOFILE=4096
ExecStart=/opt/wsm/wsmvenv3.12/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

7 - Enable SELinux:

    sudo semanage fcontext -a -t bin_t "/opt/wsm/wsmvenv3.12/bin(/.*)?"

    sudo restorecon -Rv /opt/wsm/wsmvenv3.12/bin

8 - Copy the service:

    cp wsm_session_server.service /etc/systemd/system/

9 - Restart the daemon

    systemctl daemon-reload

10 - Insert the connection information into .env located at: /opt/wsm/Workday_Session_Management/WSM-server/WSM-server-session_server

```
DATABASE_URL=postgresql://<user>:<password>@host:<port>/<session_database_name>
MQ_ADDRESS_HOST=localhost
MQ_HOST_PORT=5672
MQ_USER=guest
MQ_PASSWORD=guest1
WORK_HOURS_QUEUE=pooling
SQLALCHEMY_ECHO=false
WSM_LOG_PATH=/opt/wsm/Workday_Session_Management/WSM-server/WSM-server-session_server/logs/wsm.log
WSM_AGENT_NOTIFICATION_QUEUE=pooling
OAUTH_VALID_SECRET_KEY=<API-KEY>
```

11 - Start and enable the Session service:

    systemctl start wsm_session_server.service
    systemctl enable wsm_session_server.service
