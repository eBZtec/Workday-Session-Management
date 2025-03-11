# WSM Agent Updater

## Definição do Módulo de Aplicação
O módulo de aplicação WSM é responsável pela atualização do WSM Router.

---

## Detalhes do Projeto
- **Projeto**: Workday Session Management - WSM
- **Documento**: Documentação
- **Versão**: 1.0
- **Data**: 26/12/2024
- **Autor**: Douglas Alves

---

## Introdução
Este documento tem como objetivo apresentar o desenho proposto para implantação do serviço Python responsável pela atualização do componente de horário de jornada de trabalho do WSM Router. Este serviço é uma aplicação Python que auxilia no processo de atualização e cadastro de extensões de horário.

---

## Visão de Negócio
Este componente auxilia no gerenciamento dos horários de trabalho do ponto de vista da aplicação WSM. Mais especificamente, ele lê da fila RabbitMQ chamada "session_agent" preenchida pelo WSM session-updater-connector e retransmite para o WSM Router através de uma fila ZeroMQ.

---

## Definição do Serviço

### Encaminhamento de Mensagens (Entrada)
Este serviço Python distribui mensagens da fila RabbitMQ preenchidas pelo WSM session-updater-connector. Essas mensagens podem ser direcionadas ao WSM Router, incluindo mensagens diretas aos usuários ou mensagens de cadastro/modificação de horário.

#### Exemplo de Entrada:
```json
b'{"_sa_instance_state": "<sqlalchemy.orm.state.InstanceState object>", "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}", "unrestricted": true, "uf": "BR", "enable": true, "st": "SP", "c": "2", "deactivation_date": null, "uid": "Tester", "weekdays": "0111110", "id": 2, "start_time": "08:00", "session_termination_action": "logoff", "create_timestamp": "2024-12-20 16:58:59.879569-03:00", "cn": "Tester", "update_timestamp": "2024-12-26 10:16:34.390265-03:00", "end_time": "18:00", "l": "enc"}'
```

### Definição dos Atributos

| **Atributo**                | **Tipo** | **Obrigatório** | **Descrição**                                                                      |
|-----------------------------|----------|-----------------|------------------------------------------------------------------------------------|
| `end_time`                  | String   | Sim             | Horário em que o usuário termina o expediente.                                     |
| `start_time`                | String   | Sim             | Horário em que o usuário inicia o expediente.                                      |
| `allowed_work_hours`        | String   | Sim             | String JSON relativa ao horário de trabalho do cliente.                            |
| `deactivation_date`         | String   | Sim             | Data de desativação do usuário, se aplicável.                                      |
| `uf`                        | String   | Sim             | Abreviação do país.                                                                |
| `st`                        | String   | Sim             | Unidade federativa onde o colaborador atua.                                        |
| `c`                         | String   | Sim             | Código do município onde o colaborador atua.                                       |
| `weekdays`                  | String   | Sim             | Dias da semana para extensões de horário: 0 = bloqueado, 1 = liberado.            |
| `session_termination_action`| String   | Não             | Caso seja necessário logoff, este campo recebe o valor "logoff".                  |
| `unrestricted`              | String   | Sim             | `True` caso o usuário não tenha restrição de horário de trabalho.                  |
| `cn`                        | String   | Sim             | Nome comum do cliente, geralmente o mesmo valor de `uid`.                          |
| `uid`                       | String   | Sim             | UID do usuário no sistema.                                                        |

---

### Encaminhamento de Mensagens (Saída)
Com base no exemplo de entrada, após o processamento, a saída será estruturada da seguinte forma:
```json
{"RoutingClientMessage": {"_sa_instance_state": "<sqlalchemy.orm.state.InstanceState object>", "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}", "unrestricted": true, "uf": "BR", "enable": true, "st": "SP", "c": "2", "deactivation_date": null, "uid": "Tester", "weekdays": "0111110", "id": 2, "start_time": "08:00", "session_termination_action": "logoff", "create_timestamp": "2024-12-20 16:58:59.879569-03:00", "cn": "Tester", "update_timestamp": "2024-12-26 10:16:34.390265-03:00", "end_time": "18:00", "l": "enc"}}
```

---

## Implementação

### Instalação do Módulo
Este passo garante a configuração correta do leitor de fila RabbitMQ.

1. Copiar o diretório do módulo para o diretório do projeto:
   ```bash
   cp -r /WSM-server-agent_updater <diretório_do_projeto>
   ```

2. Configurar o ambiente virtual utilizando Python 3.12 e instalar as bibliotecas necessárias:
   ```bash
   python3.12 -m venv venv/
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Iniciar o serviço Python:
   ```bash
   python3.12 main.py
   ```

Se o processo for bem-sucedido, o módulo iniciará a leitura das mensagens da fila RabbitMQ.
 
