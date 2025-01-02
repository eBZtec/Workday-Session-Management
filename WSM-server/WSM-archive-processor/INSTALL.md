 Criação do serviço do wsm_agent_updater

1 - No diretório raiz do wsm_session_updater_connectors inclua o .env

    touch .env
```

AUDIT_DB_URL=postgresql://<user>:<password>@<host>:<port>/<audit_database_name>
QUEUE_NAME=session_archive_queue
QUEUE_HOST=localhost

```

2 - Crie o serviço em /etc/systemd/system/

```
[Unit]
Description=WSM Archive Processor Service - This service consumes the rabbitMQ queue called session_archive_queue and update the audit database.
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/Workday_Session_Management/WSM-server/WSM-archive-processor
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

2 - Inicie os serviços.

    systemctl daemon-reload.

    systemctl start wsm_archive_processor.service.

    systemctl status wsm_archive_processor.service.

    systemctl enable wsm_archive_processor.service.
