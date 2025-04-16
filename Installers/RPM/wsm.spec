Name:           wsm
Version:        1.0
Release:        3%{?dist}
Summary:        Workday Session Management Installation Package

License:        GPL-3.0
URL:            https://github.com/Workday_Session_Management
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  git, python3.12, gcc, tar, rsync
Requires:       tar, postgresql, postgresql-contrib, rabbitmq-server, brotli, libbrotli, python3.12, python3.12-pip

%description
Workday Session Management (WSM) full installation - server, audit, connectors and agents daemons.

%pre
# '/opt/wsm' creation
if [ ! -d /opt/wsm ]; then
    mkdir -p /opt/wsm
    chmod 755 /opt/wsm
fi

# 'wsm' user creation
getent passwd wsm > /dev/null || useradd -m -d /opt/wsm -s /bin/bash wsm

%prep
echo 'git clone for rpmbuild'
mkdir -p %{_builddir}/wsm-main/Workday_Session_Management/
cd %{_builddir}/wsm-main/Workday_Session_Management/
# git clone https://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@github.com/eBZtec/Workday_Session_Management.git tmp_repo
git clone http://gitea.ebz:3000/eBZ/Workday_Session_Management.git tmp_repo

echo 'move and exclude what is not needed'
rsync -a --exclude='WSM-connector-ad/' --exclude='WSM-agent-windows/' --exclude='Installers/' tmp_repo/ ./

echo 'bye bye tmp_repo'
rm -rf tmp_repo

if [ -d WSM-server/WSM-server-router/src/config/encrypted.env ]; then
    rm WSM-server/WSM-server-router/src/config/encrypted.env
fi

echo 'creating the needed tar.gz from git files'
tar -czf %{_sourcedir}/wsm-main.tar.gz .

%build
# no build is needed

%install
echo 'wsm directory is /opt/wsm'
mkdir -p %{buildroot}/opt/wsm

echo 'copying files to /opt/wsm'
cp -r %{_builddir}/wsm-main/Workday_Session_Management/* %{buildroot}/opt/wsm

echo "log dir creation"
mkdir -p %{buildroot}/opt/wsm/WSM-audit-server/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-server-session_server/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-archive-processor/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-server-session_updater_connectors/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-server-session_updater_connectors/src/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-server-agent_updater/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-server-agent_updater/src/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-server-router/logs
mkdir -p %{buildroot}/opt/wsm/WSM-server/WSM-server-router/src/logs

echo "fixing permissions for wsm files"
chown -R wsm:wsm %{buildroot}/opt/wsm
for f in `find %{buildroot}/opt/wsm -type f`; do chmod 640 $f; done
for d in `find %{buildroot}/opt/wsm -type d`; do chmod 750 $d; done


echo "creating systemd buildroot dir."
mkdir -p %{buildroot}/etc/systemd/system/

echo 'creating systemd files...'
echo '  system unit for: WSM Session Updater Connectors'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-session_updater_connectors.service
[Unit]
Description=WSM Session Updater Connectors Service - This service consumes the queue named pooling
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-server-session_updater_connectors
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=always
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-server-session_updater_connectors/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM Agent Updater'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-agent_updater.service
[Unit]
Description=WSM Agent Updater Service - This service consumes the rabbitMQ queue called session_agent and sent to Rouver via 0MQ
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-server-agent_updater
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=always
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-server-agent_updater/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM Archive Processor'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-archive_processor.service
[Unit]
Description=WSM - Archive Processor Service - This service gets entries from rabbitMQ, it was sent from router to session_archive_queue
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-archive-processor
LimitNOFILE=4096
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=on-failure
RestartSec=5s
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-archive-processor/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM Audit Server'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-audit_server.service
[Unit]
Description=WSM - Session Audit Server API Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-audit-server
LimitNOFILE=4096
ExecStart=/opt/wsm/wsmvenv3.12/bin/uvicorn main:app --host 0.0.0.0 --port 8080
RestartSec=5s
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-audit-server/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM Router'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-router.service
[Unit]
Description=WSM - Router Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-server-router
LimitNOFILE=4096
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 main.py
Restart=on-failure
RestartSec=5s
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-server-router/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM Session Server'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-session_server.service
[Unit]
Description=WSM - Session Server API Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-server-session_server
LimitNOFILE=4096
ExecStart=/opt/wsm/wsmvenv3.12/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-server-session_server/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM AD-Connector'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-ad-connector.service
[Unit]
Description=WSM AD Updater Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-AD-Connector
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 zmqServer.py
Restart=always
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-AD-Connector/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM Flex Time Server: Agents Updater'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-flex-time-agents-updater.service
[Unit]
Description=WSM Flex Time Server: Agents Updater Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-server-flex_time
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 agent_updater_server.py
Restart=always
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-server-flex_time/.env

[Install]
WantedBy=multi-user.target
EOF

echo '  system unit for: WSM Flex Time Server: Connectors Updater'
cat << EOF > %{buildroot}/etc/systemd/system/wsm-flex-time-connectors-updater.service
[Unit]
Description=WSM Flex Time Server: Connectors Updater Service
After=network.target

[Service]
User=wsm
WorkingDirectory=/opt/wsm/WSM-server/WSM-server-flex_time
ExecStart=/opt/wsm/wsmvenv3.12/bin/python3.12 connectors_updater_server.py
Restart=always
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/opt/wsm/WSM-server/WSM-server-flex_time/.env

[Install]
WantedBy=multi-user.target
EOF

echo 'setting wsm systemd permissions'
chmod 755 %{buildroot}/etc/systemd/system/wsm-*.service

%post
echo "Setting wsm:wsm owner for /opt/wsm"
chown -R wsm:wsm /opt/wsm/

%files
/opt/wsm
/etc/systemd/system/wsm-session_updater_connectors.service
/etc/systemd/system/wsm-agent_updater.service
/etc/systemd/system/wsm-archive_processor.service
/etc/systemd/system/wsm-audit_server.service
/etc/systemd/system/wsm-router.service
/etc/systemd/system/wsm-session_server.service
/etc/systemd/system/wsm-ad-connector.service
/etc/systemd/system/wsm-flex-time-connectors-updater.service
/etc/systemd/system/wsm-flex-time-agents-updater.service
%ghost /opt/wsm/WSM-audit-server/.env
%ghost /opt/wsm/WSM-server/WSM-server-session_server/.env
%ghost /opt/wsm/WSM-server/WSM-archive-processor/.env
%ghost /opt/wsm/WSM-server/WSM-server-session_updater_connectors/.env
%ghost /opt/wsm/WSM-server/WSM-server-agent_updater/.env
%ghost /opt/wsm/WSM-server/WSM-server-router/.env
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/scripts/generate-client/.env
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/scripts/generate-ca/.env
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/.env
%ghost /opt/wsm/WSM-server/WSM-server-router/src/config/.env
%ghost /opt/wsm/WSM-server/WSM-AD-Connector/.env
%ghost /opt/wsm/WSM-server/WSM-server-router/secret.key
%ghost /opt/wsm/WSM-server/WSM-server-router/src/config/secret.key
%ghost /opt/wsm/WSM-server/WSM-server-router/src/connections/secret.key
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/client_files/WSM-SESSION-SERVER_csr.pem
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/client_files/WSM-SESSION-SERVER_private_key.pem
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/client_files/WSM-SESSION-SERVER_certificate.pem
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/ca_files/ca_certificate.pem
%ghost /opt/wsm/WSM-server/WSM-server-router/certificates/ca_files/ca_private_key.pem
%ghost /opt/wsm/wsmvenv3.12
%ghost /opt/wsm/WSM-server/WSM-server-router/src/config/encrypted.env
%ghost /opt/wsm/WSM-server/WSM-server-router/encrypted.env
%ghost /opt/wsm/WSM-server/WSM-server-flex_time/.env

