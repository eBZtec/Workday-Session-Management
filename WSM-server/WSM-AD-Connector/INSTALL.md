Creating the AD Connector Service

1 - In the root directory of wsm_ad_connector, include the .env file:

    touch .env

```
ZERO_MQ_URL=
AD_HOSTNAME=
DATABASE_URL=postgresql://<user>:<password>@<host>:<port>/<session_database_name>
```

2 - Create the .service file:

    touch wsm_ad_connector.service

```
[Unit]
Description=WSM AD Updater Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/Workday_Session_Management/WSM-server/WSM-AD-Connector
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

3 - Copy the service file to the system services directory and restart the services:

    systemctl daemon-reload
    systemctl start wsm_ad_connector.service
    systemctl enable wsm_ad_connector.service

4 - To execute:

    ``` python3 zmqServer.py ```
