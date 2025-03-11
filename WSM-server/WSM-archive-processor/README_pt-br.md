
# WSM Router

## Definição do Módulo
Aplicação **WSM** responsável pela atualização do banco de dados de auditoria.

---

### Projeto
- **Nome**: Workday Session Management - WSM
- **Documento**: Documentação
- **Versão**: 1.0
- **Data**: 26/12/2024
- **Autor**: Douglas Alves

---

## Introdução
Este documento apresenta o desenho proposto para a implantação de um serviço Python responsável pela atualização do banco de dados de auditoria

---

## Visão de Negócio
Este componente facilita o gerenciamento dos horários de trabalho na aplicação WSM, consumindo mensagens da fila RabbitMQ enviadas pelo **WSM Router** salvando no banco de dados de auditoria

---

## Definição do Serviço

### Encaminhamento de Mensagens de Atualização de Horário (Entrada)
O serviço Python salva as mensagens vindas do Router sobre sessões de clientes que foram iniciadas e que foram fechadas.

#### Exemplo de entrada:

```json
{
   'table': 'SessionsAudit',
   'data': {
   'hostname': 'WIN-BE7UR9NV6LS',
    'event_type': 'logon',
     'login': 'Developer2',
      'status': 'active',
       'start_time': '2024-12-26T16:28:09.0240139+00:00',
       'end_time': None, 
       'os_version': '10.0.20348',
       'os_name': 'Microsoft Windows 10.0.20348', 
       'ip_address': '10.121.102.15', 
       'client_version': '1.2.0.0', 
       'agent_info': 'Default WSM Service installation'
      }
}
```

#### Estrutura dos atributos:

| **Atributo**       | **Tipo** | **Obrigatório** | **Descrição**                                      |
|---------------------|----------|-----------------|--------------------------------------------------|
| `action`           | String   | Sim             | Tipo de ação a ser tomada pelo serviço.          |
| `hostname`         | String   | Sim             | Hostname vinculado à sessão do usuário.          |
| `event_type`         | String   | Sim             |“logout” = se o evento que ocorreu na sessão foi um logout ou “logon” = se o evento que ocorreu na sessão foi um logon.                       |
| `login` | String   | Sim             |Uid ou username do usuário vinculado a sessão  |
| `status`        | String   | Sim             | Status da sessão, pode ser active ou deactivated        |
| `start_time`          | String   | Não             | Horário que a sessão foi iniciada.                                   |
| `end_time`            | String   | Não             | Horário que a sessão foi fechada.                                   |
| `os_version`          | String   | Não             | Versão do sistema operacional utilizado.                                   |
| `ip_address`             | String   | Sim             | Endereço de IP vinculado a sessão.               |
| `client_info`   | String | Sim | Versão do cliente vinculada a sessão |
|`agent_info` | String | Sim | Informações gerais sobre o agente | 

---

## Implementação

### Instalação do Módulo

#### Passos:
1. Copie o diretório contendo o módulo para o diretório do projeto:
   ```bash
   cp -r /WSM-Archive-Processor <diretório-do-projeto>
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
