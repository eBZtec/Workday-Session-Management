
## Instalação das bibliotecas necessárias para a atualização do WSM-server

1. Baixe os os arquivos wsm-wheels.z01, wsm-wheels.z02, wsm-wheels.z03, wsm-wheels.z04 e wsm-wheels.zip no mesmo diretório no servidor WSM-server e execute:

```bash
su - root
unzip wsm-wheels.zip
chown -R wsm:wsm wsm-wheeels/
mv wsm-wheeels/ /opt/wsm/
su - wsm
source wsmvenv3.12/bin/activate
pip install --no-index --find-links=./wsm-wheels -r requirements.txt
```
Se não houver arquivos para baixar no Github, pule para a pŕoxima seção

## Atualização do WSM Server

1. Baixar o RPM e o .sql com as atualizações no schema do WSM no database
   
update_session_db.sql (salvar no servidor de database PostgreSQL)
wsm-1.0-VERSION.el9.x86_64.rpm (salvar no servidor da aplicação WSM)

2. Instalar as atualizações do database

Acessar o servidor do database, executar:
```
psql -h <host> -U wsm -d wsm_session_db -W -f wsm_session_db.sql
psql -h <host> -U wsm -d wsm_session_db -W -f wsm_session_audit.sql
```

<HOST> host onde se encontra o database Postgresql

3. Atualizar o WSM server com o novo RPM (como root)
```
su - root
rpm -Uvh --force wsm-1.0-<VERSION>.el9.x86_64.rpm
```

4. Reiniciar todos os serviços
```
su - root
cd /etc/systemd/system/
systemctl restart wsm-*
```

##  Logs para coleta
- /opt/wsm/WSM-server/WSM-server-session_server/logs/wsm.log
- /opt/wsm/WSM-server/WSM-server-router/logs/WSM-Router.log
- /opt/wsm/WSM-server/WSM-AD-Connector/zmqServer.log
- /opt/wsm/WSM-server/WSM-server-flex_time/log/WSM-server-flex_time.log
- /opt/wsm/WSM-server/WSM-server-session_updater_connectors/logs/WSM-Server-Agent-Updater.log 
