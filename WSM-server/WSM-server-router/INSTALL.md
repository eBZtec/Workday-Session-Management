Creating the Router Service

1 - Define the CA certificate parameters in a .env file located in:

    /opt/wsm/Workday_Session_Management/WSM-server/WSM-server-router/certificates/

```
# CA Certificate Information
CA_COUNTRY_NAME=BR
CA_STATE_OR_PROVINCE_NAME=SP
CA_LOCALITY_NAME=Sao Paulo
CA_ORGANIZATION_NAME=Banco Safra
CA_ORGANIZATIONAL_UNIT_NAME=Workday Session Management Certification Authority
CA_COMMON_NAME=WSM-CA

# CA Certificate Validity (in days)
CA_NOT_VALID_BEFORE=0
CA_NOT_VALID_AFTER=3650

# Password for CA Private Key
CA_PRIVATE_KEY_PASSWORD=<password>
```

2 - Generate the CA certificate:

    python3 scripts/generate-ca/generate-ca.py

3 - Define the client certificate parameters in a .env file located in:

    scripts/generate_client/

4 - Generate the client certificate:

    python3 scripts/generate-client/generate-client.py

5 - Secure sensitive information:

    chmod 600 ca_private_key.pem

6 - Copy the `secret.key` to `/opt/wsm/Workday_Session_Management/WSM-server/WSM-server-router/src/config/`.

7 - Create the Router Service:

```
[Unit]
Description=WSM - Router Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/Workday_Session_Management/WSM-server/WSM-server-router
LimitNOFILE=4096
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

8 - Start and enable the service:

    systemctl daemon-reload
    systemctl start wsm_router.service
    systemctl enable wsm_router.service
