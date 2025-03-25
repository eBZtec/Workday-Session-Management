Name:           wsm
Version:        1.0
Release:        1%{?dist}
Summary:        Workday Session Management Installation Package

License:        GPL-3.0
URL:            https://github.com/Workday_Session_Management
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  git, python3.12, gcc, tar, rsync
Requires:       tar, postgresql, rabbitmq-server, brotli, libbrotli, python3.12, python3.12-pip

%description
Este pacote instala e configura o Workday Session Management (WSM), incluindo módulos de auditoria, conectores e agentes.

%pre
# Criar o diretório /opt/wsm, se não existir
if [ ! -d /opt/wsm ]; then
    mkdir -p /opt/wsm
    chmod 755 /opt/wsm
fi

# Criar o usuário 'wsm' se não existir
getent passwd wsm > /dev/null || useradd -m -d /opt/wsm -s /bin/bash wsm

%prep
echo 'Criar o diretório de build e clonar o repositório'
mkdir -p %{_builddir}/wsm-1.0/Workday_Session_Management/
cd %{_builddir}/wsm-1.0/Workday_Session_Management/
# git clone https://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@github.com/eBZtec/Workday_Session_Management.git tmp_repo
git clone http://gitea.ebz:3000/eBZ/Workday_Session_Management.git tmp_repo

echo 'Mover os arquivos ignorando os diretórios indesejados'
rsync -av --exclude='WSM-connector-ad/' --exclude='WSM-agent-windows/' --exclude='Installers/' tmp_repo/ ./

echo 'Remover o repositório clonado'
rm -rf tmp_repo

# Prepara python packages
# for f in `find %{_builddir}/wsm-1.0/Workday_Session_Management/ -name requirements.txt`; do cat $f | awk -F '==' '{print $1}' | awk -F '~=' '{print $1}' >>  %{_builddir}/wsm-1.0/Workday_Session_Management/requirements.in; done; cat %{_builddir}/wsm-1.0/Workday_Session_Management/requirements.in | sort -u >  %{_builddir}/wsm-1.0/Workday_Session_Management/requirements.txt
# pip download -r %{_builddir}/wsm-1.0/Workday_Session_Management/requirements.txt -d %{_builddir}/wsm-1.0/Workday_Session_Management/python-packages/

echo 'Criar o ambiente virtual Python 3.12 no diretório %{_builddir}/wsm-1.0/wsmenv'
echo "Criando o ambiente virtual Python 3.12 em %{_builddir}/wsm-1.0/Workday_Session_Management/wsmenv..."
python3.12 -m venv %{_builddir}/wsm-1.0/Workday_Session_Management/wsmvenv3.12

echo 'Ativar o ambiente virtual'
source %{_builddir}/wsm-1.0/Workday_Session_Management/wsmvenv3.12/bin/activate

echo 'Atualizar pip e instalar pacotes do requirements.txt'
pip install --upgrade pip
pip install -r %{_builddir}/wsm-1.0/Workday_Session_Management/requirements.txt

echo 'Preparando o tar.gz dos pacotes python'
tar -czf %{_builddir}/wsm-1.0/Workday_Session_Management/wsmvenv3.12.tar.gz -C %{_builddir}/wsm-1.0/Workday_Session_Management/ wsmvenv3.12
#tar -czf /root/rpmbuild/BUILD/wsm-1.0/Workday_Session_Management/wsmvenv3.12.tar.gz -C /root/rpmbuild/BUILD/wsm-1.0/Workday_Session_Management/ wsmvenv3.12
rm -fR %{_builddir}/wsm-1.0/Workday_Session_Management/wsmvenv3.12

echo 'Criar o tar.gz atualizado com os arquivos do Git'
tar -czf %{_sourcedir}/wsm-1.0.tar.gz .

%build
# Nenhuma etapa de compilação necessária para este projeto

%install
echo 'Criar o diretório de instalação'
mkdir -p %{buildroot}/opt/wsm

echo 'Copiar os arquivos do projeto para /opt/wsm'
cp -r %{_builddir}/wsm-1.0/Workday_Session_Management/* %{buildroot}/opt/wsm

echo "Ajustar permissões para o usuário 'wsm'"
chown -R wsm:wsm %{buildroot}/opt/wsm
chmod -R 750 %{buildroot}/opt/wsm

echo "Criar diretório para arquivos de serviço"
mkdir -p %{buildroot}/etc/systemd/system/

echo 'Serviços Systemd:'
echo 'Serviço: WSM Session Updater Connectors'
cat << EOF > %{buildroot}/etc/systemd/system/wsm_session_updater_connectors.service
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

echo 'Serviço: WSM Agent Updater'
cat << EOF > %{buildroot}/etc/systemd/system/wsm_agent_updater.service
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

echo 'Serviço: WSM Archive Processor'
cat << EOF > %{buildroot}/etc/systemd/system/wsm_archive_processor.service
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

echo 'Serviço: WSM Audit Server'
cat << EOF > %{buildroot}/etc/systemd/system/wsm_audit_server.service
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

echo 'Serviço: WSM Router'
cat << EOF > %{buildroot}/etc/systemd/system/wsm_router.service
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

echo 'Serviço: WSM Session Server'
cat << EOF > %{buildroot}/etc/systemd/system/wsm_session_server.service
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

echo 'Serviço: WSM AD-Connector'
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

echo 'Ajustando permissões para os serviços systemd'
chmod 644 %{buildroot}/etc/systemd/system/*.service
chmod +x %{buildroot}/etc/systemd/system/*.service

%post

echo "Extraindo bibliotecas do wsmvenv3.12..tar.gz..."
tar -xzf /opt/wsm/wsmvenv3.12.tar.gz -C /opt/wsm/

# Criar o ambiente virtual Python 3.12 no diretório /opt/wsm/wsmenv
#echo "Criando o ambiente virtual Python 3.12 em /opt/wsm/wsmenv..."
#python3.12 -m venv /opt/wsm/wsmvenv3.12

# Ativar o ambiente virtual
#source /opt/wsm/wsmvenv3.12/bin/activate

# Atualizar pip e instalar pacotes do requirements.txt
#pip install --no-index --find-links=/opt/wsm/python-packages -r /opt/wsm/requirements.txt

echo 'Ajustar proprietário e grupo do ambiente virtual e pacotes instalados'
echo "Ajustando proprietário e grupo do ambiente em /opt/wsm para o usuario wsm"

chown -R wsm:wsm /opt/wsm/

%files
/opt/wsm
/etc/systemd/system/wsm_session_updater_connectors.service
/etc/systemd/system/wsm_agent_updater.service
/etc/systemd/system/wsm_archive_processor.service
/etc/systemd/system/wsm_audit_server.service
/etc/systemd/system/wsm_router.service
/etc/systemd/system/wsm_session_server.service
/etc/systemd/system/wsm-ad-connector.service
