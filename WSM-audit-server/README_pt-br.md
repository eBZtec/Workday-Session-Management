# WSM Audit Server

## Definição do Módulo de Aplicação
O módulo de aplicação WSM é responsável pela extração de relatórios de sessão.

---

## Detalhes do Projeto
- **Projeto**: Workday Session Management - WSM
- **Documento**: Documentação
- **Versão**: 1.0
- **Data**: 30/12/2024
- **Autor**: Douglas Alves

---

## Introdução
Este documento tem como objetivo apresentar o desenho proposto para a implementação da API responsável pela extração de relatórios referentes às sessões de clientes.

---

## Visão de Negócio
Este componente auxilia no gerenciamento dos horários de trabalho do ponto de vista da aplicação WSM, especificamente fornecendo endpoints de consulta para usuários e suas sessões, bem como informações relacionadas.

---

## Definição da API
A API utiliza modelos do SQLAlchemy para mapear tabelas do banco de dados. Exemplo de modelo:

```python
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class SessionsAudit(Base):
    __tablename__ = 'session_audit'

    id = Column(Integer, primary_key=True, autoincrement=True)
    hostname = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)
    login = Column(String(100), nullable=False)
    status = Column(String(50))
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    create_timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    update_timestamp = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=True)
    os_version = Column(String(50), nullable=False)
    os_name = Column(String(50))
    ip_address = Column(String(100), nullable=False)
    client_version = Column(String(50), nullable=False)
    agent_info = Column(String(50))
```

---

### Consultas a Informações de Sessões e Clientes (Entrada)
Este serviço de API permite a consulta paginada em um banco de dados utilizando filtros dinâmicos. Os filtros são definidos no formato JSON, permitindo flexibilidade na criação de consultas complexas.

A API foi projetada para:
- Receber filtros em formato JSON.
- Traduzir esses filtros em expressões SQLAlchemy.
- Retornar resultados paginados.

#### Descrição
Recebe filtros e parâmetros de paginação e retorna os resultados paginados.

##### Entrada (JSON):
```json
{
  "filters": [
    {"field": "hostname", "operator": "$eq", "value": "WIN-BE7UR9NV6LS"},
    {"field": "start_time", "operator": "$gte", "value": "2024-12-16"},
    {"field": "start_time", "operator": "$lte", "value": "2024-12-16T23:59:59"}
  ],
  "page": 1,
  "page_size": 10
}
```

##### Saída (JSON):
```json
{
  "page": 1,
  "page_size": 10,
  "total_records": 2,
  "data": [
    {
      "id": 58,
      "hostname": "WIN-BE7UR9NV6LS",
      "event_type": "logon",
      "login": "Tester",
      "status": "active",
      "start_time": "2024-12-16T09:00:00Z",
      "end_time": null,
      "create_timestamp": "2024-12-16T09:00:00Z",
      "update_timestamp": "2024-12-16T09:00:00Z",
      "os_version": "10.0.20348",
      "os_name": "Microsoft Windows",
      "ip_address": "10.121.102.15",
      "client_version": "1.2.0.0",
      "agent_info": "Default WSM Service installation"
    }
  ]
}
```

---

### Operadores Suportados
Os filtros são definidos em JSON e suportam operadores como $eq (igual), $gte (maior ou igual), $lte (menor ou igual), $like (correspondência parcial), entre outros. Exemplos:

| **Operador** | **Descrição**                  | **Equivalente SQL** | **Exemplo**                                       |
|--------------|--------------------------------|----------------------|--------------------------------------------------|
| `$eq`        | Igual                          | `=`                | `{ "field": "hostname", "operator": "$eq", "value": "WIN-BE7UR9NV6LS" }` |
| `$ne`        | Diferente                      | `!=`                | `{ "field": "status", "operator": "$ne", "value": "inactive" }`          |
| `$lt`        | Menor que                      | `<`                 | `{ "field": "start_time", "operator": "$lt", "value": "2024-12-16T00:00:00" }` |
| `$lte`       | Menor ou igual a               | `<=`                | `{ "field": "start_time", "operator": "$lte", "value": "2024-12-16T23:59:59" }` |
| `$gt`        | Maior que                      | `>`                 | `{ "field": "age", "operator": "$gt", "value": 30 }`                     |
| `$gte`       | Maior ou igual a               | `>=`                | `{ "field": "age", "operator": "$gte", "value": 30 }`                     |
| `$like`      | Correspondência parcial        | `LIKE`              | `{ "field": "login", "operator": "$like", "value": "%admin%" }`         |
| `$ilike`     | Correspondência parcial case-insensitive | `ILIKE` (PostgreSQL)| `{ "field": "login", "operator": "$ilike", "value": "%Admin%" }`        |
| `$in`        | Dentro de uma lista            | `IN`                | `{ "field": "status", "operator": "$in", "value": ["active", "pending"] }` |

Exemplo de uso:

```json
[
  {"field": "hostname", "operator": "$eq", "value": "WIN-BE7UR9NV6LS"},
  {"logical": "OR", "conditions": [
    {"field": "status", "operator": "$eq", "value": "active"},
    {"field": "status", "operator": "$eq", "value": "disconnected"}
  ]}
]
```

---

## Implementação

### Instalação do Módulo
Este passo define a funcionalidade para leitura da fila RabbitMQ.

1. Copiar o diretório do módulo para o diretório do projeto:
   ```bash
   cp -r /WSM-AD-Connector <diretório_do_projeto>
   ```

2. Configurar o ambiente virtual utilizando Python 3.12 e instalar as bibliotecas do `requirements.txt`:
   ```bash
   python3.12 -m venv venv/
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Iniciar o serviço Python:
   - Para desenvolvimento:
     ```bash
     fastapi dev main.py
     ```
   - Para produção:
     ```bash
     gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 main:app
     ```

Se o procedimento for bem-sucedido, o módulo iniciará os endpoints na porta especificada.
