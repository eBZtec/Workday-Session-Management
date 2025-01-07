
# WSM Router

## Definição do Módulo
Aplicação **WSM** responsável pela atualização de horário de clientes no **Active Directory (AD)**.

---

### Projeto
- **Nome**: Workday Session Management - WSM
- **Documento**: Documentação
- **Versão**: 1.0
- **Data**: 26/12/2024
- **Autor**: Douglas Alves

---

## Introdução
Este documento apresenta o desenho proposto para a implantação de um serviço Python responsável pela atualização de horários de jornada de trabalho dos clientes, utilizando uma API REST via fila no Active Directory. O serviço auxilia no processo de atualização e cadastro de extensões de horário.

---

## Visão de Negócio
Este componente facilita o gerenciamento dos horários de trabalho na aplicação WSM, consumindo mensagens da fila RabbitMQ enviadas pelo **WSM Agent-Updater-Connector** e retransmitindo-as para o serviço do Active Directory.

---

## Definição do Serviço

### Encaminhamento de Mensagens de Atualização de Horário (Entrada)
O serviço Python distribui mensagens vindas da fila ZeroMQ, sejam de atualização de horário ou mensagens diretas para o cliente.

#### Exemplo de entrada:

```json
{
  "action": "updateHours",
  "hostname": "WIN-BE7UR9NV6LS",
  "user": "Tester",
  "timezone": "UTC-03:00",
  "allowed_schedule": {
    "sunday": [{"start": 0, "end": 0}],
    "monday": [{"start": 0, "end": 0}],
    "tuesday": [{"start": 540, "end": 1080}],
    "wednesday": [{"start": 540, "end": 1080}],
    "thursday": [{"start": 540, "end": 1080}],
    "friday": [{"start": 540, "end": 1080}],
    "saturday": [{"start": 540, "end": 1080}]
  },
  "timestamp": "2024-11-21T15:30:00Z",
  "message": null,
  "title": null,
  "options": null
}
```

#### Estrutura dos atributos:

| **Atributo**       | **Tipo** | **Obrigatório** | **Descrição**                                      |
|---------------------|----------|-----------------|--------------------------------------------------|
| `action`           | String   | Sim             | Tipo de ação a ser tomada pelo serviço.          |
| `hostname`         | String   | Sim             | Hostname vinculado à sessão do usuário.          |
| `timezone`         | String   | Sim             | Timezone da sessão atual.                        |
| `allowed_schedule` | String   | Sim             | Atualização do horário de trabalho do usuário.   |
| `timestamp`        | String   | Sim             | Horário em que a mensagem foi disparada.         |
| `message`          | String   | Não             | Não utilizado.                                   |
| `title`            | String   | Não             | Não utilizado.                                   |
| `options`          | String   | Não             | Não utilizado.                                   |
| `user`             | String   | Sim             | Login, UID ou usuário no sistema.               |

---

### Encaminhamento de Mensagens de Atualização de Horário (Saída)

Após o processamento, a saída será como o exemplo abaixo:

```json
{
  "action": "updateHours",
  "hostname": "WIN-BE7UR9NV6LS",
  "user": "Tester",
  "timezone": "2024-12-26 10:45:31.767804-03:00",
  "unrestricted": true,
  "enable": true,
  "allowed_schedule": "{"MONDAY": [{"start": 0, "end": 1439}], "TUESDAY": [{"start": 0, "end": 1439}], "WEDNESDAY": [{"start": 0, "end": 1439}], "THURSDAY": [{"start": 0, "end": 1439}], "FRIDAY": [{"start": 0, "end": 1439}], "SATURDAY": [{"start": 0, "end": 1439}], "SUNDAY": [{"start": 0, "end": 1439}]}",
  "timestamp": "2024-12-26 10:45:31.767804-03:00",
  "message": null,
  "title": "Notification",
  "options": "yes_no"
}
```

**Nota**: A comunicação real entre o Router e o Client utiliza mensagens criptografadas.

---

## Implementação

### Instalação do Módulo
Antes de iniciar a instalação o arquivo "private_key.pem" já deve estar gerado na instalação do WSM Router e deve estar neste diretório para que a criptografia funcione corretamente ou o apontamento para esse diretório na função load_key no zmqServer.py para o caminho do arquivo, para que seja feita a leitura.
#### Passos:
1. Copie o diretório contendo o módulo para o diretório do projeto:
   ```bash
   cp -r /WSM-AD-Connector <diretório-do-projeto>
   ```

2. Configure o virtualenv utilizando o Python 3.12:
   ```bash
   python3.12 -m venv venv/
   ```

3. Ative o ambiente virtual:
   ```bash
   source venv/bin/activate
   ```

4. Instale as bibliotecas do arquivo `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

5. Inicie o serviço Python:
   ```bash
   python3.12 main.py
   ```

Se o procedimento for bem-sucedido, o módulo iniciará a leitura da fila RabbitMQ.

---

© 2024 TECNOLOGIA
