 
# WSM Updater Connectors

## Definição do Módulo de Aplicação
O módulo de aplicação WSM é responsável pela atualização de conectores.

---

## Detalhes do Projeto
- **Projeto**: API REST para o Integrador CJT
- **Documento**: Documentação
- **Versão**: 1.0
- **Data**: 26/12/2024
- **Autor**: Douglas Alves

---

## Introdução
Este documento tem como objetivo apresentar o desenho proposto para implantação do serviço Python responsável pela atualização de horário de jornada de trabalho de conectores. Este serviço auxilia no processo de atualização e cadastro de extensões de horário.

---

## Visão de Negócio
Este componente auxilia no gerenciamento dos horários de trabalho do ponto de vista da aplicação WSM. Ele deve ler a fila RabbitMQ chamada "pooling de contas" e, com base nos serviços cadastrados no banco de dados para o usuário, disparar mensagens para a fila com o horário do usuário.

---

## Definição do Serviço

### Roteamento de Mensagens
Este serviço Python distribui mensagens provenientes da API. Essas mensagens podem ser direcionadas ao WSM Router, como mensagens diretas ao usuário, ou mensagens de cadastro/alteração de horário destinadas ao WSM Router através da fila "session_agent" ou a outros serviços, como a fila específica para o Active Directory (AD).

#### Exemplo de Entrada: Mensagem ao Usuário
```json
{"action": "Notify", "user": "Tester", "title": "Notification", "message": "Some message"}
```

### Definição dos Atributos

| **Atributo** | **Tipo** | **Obrigatório** | **Descrição** |
|--------------|----------|-----------------|---------------|
| `action`     | String   | Sim             | Tipo de ação vinculada ao registro na fila. Exemplo: `Notify` para mensagens diretas ao usuário. |
| `user`       | String   | Sim             | Nome do usuário que receberá a mensagem. |
| `title`      | String   | Sim             | Título da mensagem exibido ao usuário. |
| `message`    | String   | Sim             | Corpo da mensagem enviada ao usuário. |

---

#### Exemplo de Entrada: Cadastro/Atualização de Horário de Trabalho
```json
{
 "end_time": "18:00",
 "l": "enc",
 "allowed_work_hours": "{\"MONDAY\": [{\"start\": 0, \"end\": 1439}], \"TUESDAY\": [{\"start\": 0, \"end\": 1439}], \"WEDNESDAY\": [{\"start\": 0, \"end\": 1439}], \"THURSDAY\": [{\"start\": 0, \"end\": 1439}], \"FRIDAY\": [{\"start\": 0, \"end\": 1439}], \"SATURDAY\": [{\"start\": 0, \"end\": 1439}], \"SUNDAY\": [{\"start\": 0, \"end\": 1439}]}\",
 "unrestricted": true,
 "uf": "BR",
 "enable": true,
 "st": "SP",
 "c": "2",
 "deactivation_date": null,
 "uid": "Tester",
 "weekdays": "0111110",
 "start_time": "08:00",
 "session_termination_action": "logoff",
 "create_timestamp": "2024-12-20 16:58:59.879569-03:00",
 "cn": "Tester",
 "update_timestamp": "2024-12-23 13:55:52.240257-03:00"
}
```

### Definição dos Atributos

| **Atributo**                | **Tipo** | **Obrigatório** | **Descrição** |
|-----------------------------|----------|-----------------|---------------|
| `end_time`                  | String   | Sim             | Horário em que o usuário termina o expediente. |
| `start_time`                | String   | Sim             | Horário em que o usuário inicia o expediente. |
| `allowed_work_hours`        | String   | Sim             | JSON contendo o horário de trabalho do cliente. |
| `deactivation_date`         | String   | Sim             | Data de desativação do usuário, se aplicável. |
| `uf`                        | String   | Sim             | Abreviação do país. |
| `st`                        | String   | Sim             | Unidade federativa onde o colaborador atua. |
| `c`                         | String   | Sim             | Código do município onde o colaborador atua. |
| `weekdays`                  | String   | Sim             | Dias da semana aplicados à extensão de horário: 0 = bloqueado, 1 = liberado. |
| `session_termination_action`| String   | Não             | Valor "logoff" caso o usuário precise encerrar a sessão. |
| `unrestricted`              | String   | Sim             | `True` se o usuário não tiver restrição de horário. |
| `cn`                        | String   | Sim             | Nome comum do cliente, geralmente o mesmo valor de `uid`. |
| `uid`                       | String   | Sim             | UID do usuário no sistema. |

---

## Implementação

### Instalação do Módulo
Este passo garante a configuração correta do leitor de fila RabbitMQ.

1. Copiar o diretório do módulo para o diretório do projeto:
   ```bash
   cp -r /WSM-server-session_updater_connectors <diretório_do_projeto>
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