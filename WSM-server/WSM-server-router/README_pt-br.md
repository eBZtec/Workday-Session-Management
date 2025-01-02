# WSM Router

## Definição do Módulo de Aplicação
O módulo de aplicação WSM é responsável pela atualização de horários dos clientes, criptografia e mensageria.

---

## Detalhes do Projeto
- **Projeto**: Workday Session Management - WSM
- **Documento**: Documentação
- **Versão**: 1.0
- **Data**: 26/12/2024
- **Autor**: Douglas Alves

---

## Introdução
Este documento tem como objetivo apresentar o desenho proposto para implantação do serviço Python responsável pela atualização de horários de jornada de trabalho dos clientes (criptografadas), envio de mensagens para os clientes (criptografadas) vindas da API REST via fila e a Autoridade Certificadora das comunicações. Este serviço auxilia no processo de atualização e cadastro de extensões de horário.

---

## Visão de Negócio
Este componente auxilia no gerenciamento dos horários de trabalho do ponto de vista da aplicação WSM. Mais especificamente, ele lê da fila ZeroMQ enviada pelo WSM agent-updater e retransmite para os clientes também por fila ZeroMQ.

---

## Definição do Serviço

### Encaminhamento de Mensagens de Atualização de Horário (Entrada)
Este serviço Python distribui mensagens da fila ZeroMQ preenchidas pelo WSM agent-updater. Essas mensagens podem ser uma atualização de horário para o cliente ou mensagens diretas para o cliente.

#### Exemplo de Entrada:
```json
"RoutingClientMessage": {
    "_sa_instance_state": "<sqlalchemy.orm.state.InstanceState object>",
    "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}\",",
    "unrestricted": true,
    "uf": "BR",
    "enable": true,
    "st": "SP",
    "c": "2",
    "deactivation_date": null,
    "uid": "Tester",
    "weekdays": "0111110",
    "id": 2,
    "start_time": "08:00",
    "session_termination_action": "logoff",
    "create_timestamp": "2024-12-20 16:58:59.879569-03:00",
    "cn": "Tester",
    "update_timestamp": "2024-12-26 10:45:31.767804-03:00",
    "end_time": "18:00",
    "l": "enc"
}
```

### Encaminhamento de Mensagens de Atualização de Horário (Saída)
A saída após o processamento será:
```json
{
    "action": "updateHours",
    "hostname": "WIN-BE7UR9NV6LS",
    "user": "Tester",
    "timezone": "2024-12-26 10:45:31.767804-03:00",
    "unrestricted": true,
    "enable": true,
    "allowed_schedule": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}\",",
    "timestamp": "2024-12-26 10:45:31.767804-03:00",
    "message": null,
    "title": "Notification",
    "options": "yes_no"
}
```
A estrutura da mensagem de saída é um exemplo, pois a comunicação real entre Router e Client é criptografada.

---

### Encaminhamento de Mensagens Diretas (Entrada)
Além de atualizações de horário, o serviço também pode enviar mensagens diretas para os clientes.

#### Exemplo de Entrada:
```json
{"RoutingClientMessage": {"action": "Notify", "user": "Tester", "title": "Título", "message": "Message"}}
```

### Encaminhamento de Mensagens Diretas (Saída)
Após o processamento, a mensagem enviada será estruturada da seguinte forma:
```json
{
    "action": "Notify",
    "hostname": "WIN-BE7UR9NV6LS",
    "user": "Tester",
    "timezone": "UTC",
    "unrestricted": true,
    "enable": true,
    "timestamp": "2024-12-26 10:45:31.767804-03:00",
    "message": "Message",
    "title": "Título",
    "options": "yes_no"
}
```

---

## Recebimento de Mensagens de Heartbeating (Entrada)
Os clientes enviam mensagens para o Router para confirmar a comunicação Heartbeating e incluir a sessão de um novo usuário.

#### Exemplo de Entrada:
```json
{
    "Heartbeat": {
        "hostname": "WIN-BE7UR9NV6LS",
        "ip_address": "10.121.102.15",
        "client_version": "1.2.0.0",
        "os_name": "Microsoft Windows 10.0.20348",
        "os_version": "10.0.20348",
        "agent_info": "Default WSM Service installation",
        "uptime": 90,
        "timezone": "-03:00:00"
    }
}
```

### Recebimento de Mensagens de Heartbeating (Saída)
Como resposta, o Router retorna a seguinte mensagem:
```json
{"status": "beating", "message": "Done"}
```

---

## Envio de Mensagens para a Fila de Auditoria
O Router também envia mensagens para a fila de auditoria contendo dados de sessões abertas e fechadas no banco de sessões.

#### Exemplo de Mensagem de Auditoria:
```json
{
    "table": "SessionsAudit",
    "data": {
        "hostname": "WIN-BE7UR9NV6LS",
        "event_type": "logon",
        "login": "Developer2",
        "status": "active",
        "start_time": "2024-12-26T16:28:09.0240139+00:00",
        "end_time": null,
        "os_version": "10.0.20348",
        "os_name": "Microsoft Windows 10.0.20348",
        "ip_address": "10.121.102.15",
        "client_version": "1.2.0.0",
        "agent_info": "Default WSM Service installation"
    }
}
```

---

## Processo de Certificação e Criptografia de Mensagens
O servidor possui uma Autoridade Certificadora (CA) própria para gerenciar Certificate Signing Requests (CSRs). Esses CSRs são a primeira mensagem trocada entre o Router e os clientes, permitindo a assinatura e reconhecimento dos certificados.

- **WSM_SESSION_SERVER**: Certificado do Router que contém a chave privada para decriptar mensagens recebidas.
- **WSM_CA**: Certificado autoassinado que estabelece a identidade da CA.

O Router armazena apenas as chaves públicas dos clientes no banco de dados e utiliza essas chaves para criptografar mensagens. A comunicação entre Router e clientes é garantida como segura, com as mensagens sendo decriptadas apenas pelos destinatários.

---

## Implementação

### Instalação do Módulo
1. Copiar o diretório do módulo para o projeto:
   ```bash
   cp -r /WSM-router <diretório do projeto>
   ```

2. Configurar o ambiente virtual com Python 3.12:
   ```bash
   python3.12 -m venv venv/
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Iniciar o serviço Python:
   ```bash
   python3.12 main.py
   ```

Se o processo for bem-sucedido, o módulo iniciará a leitura da fila RabbitMQ.
