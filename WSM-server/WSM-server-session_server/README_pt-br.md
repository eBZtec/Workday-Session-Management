
# API do Servidor de Sessões WSM

## Detalhes do Projeto
- **Nome**: API do Servidor de Sessões WSM
- **Documento**: Documentação
- **Versão**: 1.0
- **Data**: 30/12/2024
- **Autor**: Jean Michel Santos

---

## Introdução
A **API do Servidor de Sessões WSM** é um serviço REST escrito inteiramente em Python versão 3.12, usando o framework FastAPI. É responsável por gerenciar as jornadas de trabalho das contas do WSM.

Este recurso permite gerenciar as jornadas de trabalho das contas, incluindo extensões, bloqueio ou desbloqueio de usuários, e envio de notificações para o usuário nas estações de trabalho em que ele está conectado.

De forma assíncrona, quaisquer alterações feitas utilizando a API do Servidor de Sessões WSM refletem nos serviços pré-configurados da aplicação, como **WSM Agent** e **WSM Connector AD**, onde as jornadas de trabalho são recalculadas com extensões ativas e enviadas para as aplicações.

---
# API

## Contas WSM
As contas do WSM são usadas para calcular a jornada de trabalho de um usuário. Este objeto contém todas as informações necessárias para determinar se um usuário pode trabalhar durante um período específico.

Qualquer alteração na conta é automaticamente sincronizada com todos os serviços gerenciados pelo WSM.

---

### Criação de Conta

Este recurso permite cadastrar uma nova conta no WSM, e configurar a jornada de trabalho baseada nos dados de cadastro. 

Cada nova conta criada, o processo irá automaticamente atualizar o horário em todos os serviços que o usuário possui habilitados no WSM, por exemplo, atualizar o “Logon Hours” no Active Directory, e/ou enviar uma atualização de horários de trabalho para todo(s) o(s) agente(s) WSM da estação que o usuário está autenticado.

#### Requisição
```http
POST /wsm/api/v1/account/
Host: {URL do Ambiente}
Content-Type: application/json

{
 "uid": "<UID do Usuário>",
 "start_time": "08:00",
 "end_time": "17:00",
 "uf": "BR",
 "st": "SP",
 "c": 25,
 "weekdays": "0111110",
 "session_termination_action": "logoff",
 "cn": "<Nome completo do usuário>",
 "l": "Endereço",
 "enable": true,
 "unrestricted": false
}
```

#### Resposta
- **HTTP 200 OK**: Conta cadastrada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos

---

### Esquema de Atributos

| **Atributo**                | **Tipo** | **Obrigatório** | **Descrição**                                                                       |
|-----------------------------|----------|-----------------|-------------------------------------------------------------------------------------|
| `uid`                      | String   | Sim             | Login do usuário                                                                   |
| `start_time`               | String   | Sim             | Horário de início da jornada no formato HH:MM                                      |
| `end_time`                 | String   | Sim             | Horário de fim da jornada no formato HH:MM                                         |
| `uf`                       | String   | Sim             | Unidade Federativa                                                                 |
| `st`                       | String   | Sim             | Estado onde o usuário reside                                                      |
| `c`                        | Integer  | Sim             | Código da cidade                                                                   |
| `weekdays`                 | String   | Sim             | Dias em que o usuário pode trabalhar (0: bloqueado, 1: liberado, começando no domingo) |
| `session_termination_action` | String | Não             | Ação ao autenticar em estação quando não habilitado (padrão: "logoff")             |
| `cn`                       | String   | Sim             | Nome completo do usuário                                                          |
| `l`                        | String   | Sim             | Endereço do usuário                                                               |
| `enable`                   | Boolean  | Não             | Usuário habilitado ou desabilitado (padrão: true)                                  |
| `unrestricted`             | Boolean  | Não             | Habilita jornada irrestrita (padrão: false)                                       |
| `deactivation_date`        | Date     | Não             | Data de desativação no formato YYYY-MM-DDTHH:MM:SS                                 |

---

### Atualização

O recurso para atualizar uma conta recalcula toda a jornada de trabalho de um usuário baseado na alteração feita.

Este recurso pode bloquear/desbloquear uma conta, alterar a jornada de trabalho, alterar os dias da semana da jornada, inserir ou remover data de demissão e/ou transformar a jornada de trabalho para irrestrita.

Em todos esses tipos de atualização, será enviado para os serviços o horário atualizado do usuário já contabilizando feriados, extensões de horários e etc.

#### Requisição
```http
PUT /wsm/api/v1/account/
Host: {URL do Ambiente}
Content-Type: application/json

{
 "uid": "<UID do Usuário>",
 "start_time": "08:00",
 "end_time": "17:00",
 "uf": "BR",
 "st": "SP",
 "c": 25,
 "weekdays": "0111110",
 "session_termination_action": "logoff",
 "cn": "<Nome completo do usuário>",
 "l": "Endereço",
 "enable": true,
 "unrestricted": false
}
```

#### Resposta
- **HTTP 200 OK**: Conta atualizada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos

---

### Desabilitar Conta
Este recurso permite desabilitar um usuário no banco de dados do WSM.

Para isso, a jornada do usuário cadastrada será totalmente ignorada pelo serviço, e em todos os dias da semana o horário do usuário estará bloqueado para acesso.

Os novos valores calculados da jornada serão inseridos no banco de dados, e serão enviados de forma assíncrona para os serviços no Active Directory, e WSM Agent onde o usuário possui sessões ativas.

#### Requisição
```http
POST /wsm/api/v1/account/{uid}/disable
Host: {URL do Ambiente}
Content-Type: application/json
```

- `{uid}`: Login do usuário que será desabilitado.

#### Resposta
- **HTTP 200 OK**: Conta desabilitada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos

---

### Habilitar

Este recurso permite habilitar um usuário no banco de dados do WSM

O jornada será calculada baseada nos dados cadastrados na conta do usuário no WSM, e serão enviados de forma assincrona para para o serviços do Active Directory e WSM Agents onde o usuário possui sessões ativas.

#### Requisição

```http
POST /wsm/api/v1/account/{uid}/enable
HOST {urlAmbiente}
Content-Type: application/json
```
- `{uid}`: Login do usuário que será habilitado.

#### Resposta
- **HTTP 200 OK**: Conta desabilitada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos

---

### Logoff

Permite fazer o logoff de um usuário em uma determinada estação a partir do host. É enviado um comando, de forma assincrona, para o WSM Agent que executa o processo de logoff do usuário na estação.

#### Requisição

```http
POST /wsm/api/v1/account/{uid}/logoff/{host}
HOST {urlAmbiente}
Content-Type: application/json
```
 - `{uid}` : Login do usuário que será desabilitado
 - `{host}` : Host ou IP da estação que deseja fazer o logout do usuário


#### Resposta
- **HTTP 200 OK**: Conta desabilitada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos


### Pesquisa de usuário
Este método retorna os dados cadastrados de um usuário na base dados dos WSM através do uid (login), incluindo as extensões de horários ativas do usuário e o status de atualização dos serviços.

O status de atualização serve para mostrar se os dados do usuário estão atualizados nos serviços, caso o timestamp de atualização do status seja maior ou igual ao timestamp de atualização da conta WSM, significa que o usuário está com todos seus dados sincronizados.

#### Requisição
```http
POST /wsm/api/v1/account/{uid}
HOST {urlAmbiente}
Content-Type: application/json
```

- `{uid}` : Login do usuário que será pesquisado.

#### Resposta
- **HTTP 200 OK**: Conta desabilitada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos




### Extensões de Horário
As extensões de horários são utilizadas para fornecer tempo de trabalho além da jornada de trabalho padrão do usuário.

Neste componente do WSM, pode-se definir novas extensões, alterar extensões, desabilitar extensões e pesquisar extensões ativas por usuário.

O calculo de jornada de trabalho para o usuário, só leva em considerações extensões ativas e que estejam dentro do período de tempo atual, extensões antigas ou desabilitadas são ignoradas. Assim como nas contas do WSM, a cada inserção ou alteração nas extensões de horário, a jornada de trabalho do usuário é recalculada e é enviado automaticamente um sincronismo de informações para o serviços gerenciados pelo WSM.

#### Criação de Extensão

O processo de criação de extensão de extensão de horário insere na base dados uma nova extensão que será utilizada no cálculo da jornada de trabalho do usuário.

#### Requisição
```http
POST /wsm/api/v1/overtime/
Host: {URL do Ambiente}
Content-Type: application/json

{
 "uid": "<UID do Usuário>",
 "extension_start_time": "2024-12-26T20:00:00",
 "extension_end_time": "2024-12-26T21:00:00",
 "extension_active": true
}
```

#### Resposta
- **HTTP 200 OK**: Extensão criada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos

...

### Corpo da requisição

| **Atributo**                | **Tipo** | **Obrigatório** | **Descrição**                                                                       |
|-----------------------------|----------|-----------------|-------------------------------------------------------------------------------------|
| `uid`                       | String   | Sim             | Login do usuário                                                                   |
| `extension_start_time`      | String   | Sim             | Hora de inicio da extensão de horário. É necessário definir a data e hora exata que a extensão irá começar.<br> Formato: YYYY-mm-ddTHH:MM:SS <br> Y – ano <br> m - mês <br> d - dia <br> H - hora <br> M - minuto <br> S - segundo <br> Exemplo: 2024-12-26T20:00:00
| `extension_end_time`        | String   | Sim             | Hora de fim da extensão de horário. É necessário definir a data e hora exata que a extensão irá começar.<br> Formato: YYYY-mm-ddTHH:MM:SS <br> Y – ano <br> m - mês <br> d - dia <br> H - hora <br> M - minuto <br> S - segundo <br> Exemplo: 2024-12-26T20:00:00 <br> Obs.: É possível definir a data final de extensão para o dia seguinte, basta alterar o dia para o dia seguinte                                   |
| `extension_active`          | String   | Sim             | Flag utilizada para determinar se uma extensão está ativa. A extensão será ignorada no cálculo da jornada de trabalho caso seja inativada. <br> Padrão: True (ativa)                                                                 |

---


### Atualização
Este processa atualiza uma extensão de horário já cadastrada no sistema, pode-se alterar o horário, habilitar ou desabilitar a jornada.


#### Requisição
```http
PUT /wsm/api/v1/overtime/
Host: {URL do Ambiente}
Content-Type: application/json

{
 "uid": "<UID do Usuário>",
 "extension_start_time": "2024-12-26T20:00:00",
 "extension_end_time": "2024-12-26T21:00:00",
 "extension_active": true
}
```

#### Resposta
- **HTTP 200 OK**: Atualizado com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos


### Corpo da requisição

| **Atributo**                | **Tipo** | **Obrigatório** | **Descrição**                                                                       |
|-----------------------------|----------|-----------------|-------------------------------------------------------------------------------------|
| `uid`                       | String   | Sim             | Login do usuário                                                                   |
| `extension_start_time`      | String   | Sim             | Hora de inicio da extensão de horário. É necessário definir a data e hora exata que a extensão irá começar.<br> Formato: YYYY-mm-ddTHH:MM:SS <br> Y – ano <br> m - mês <br> d - dia <br> H - hora <br> M - minuto <br> S - segundo <br> Exemplo: 2024-12-26T20:00:00
| `extension_end_time`        | String   | Sim             | Hora de fim da extensão de horário. É necessário definir a data e hora exata que a extensão irá começar.<br> Formato: YYYY-mm-ddTHH:MM:SS <br> Y – ano <br> m - mês <br> d - dia <br> H - hora <br> M - minuto <br> S - segundo <br> Exemplo: 2024-12-26T20:00:00 <br> Obs.: É possível definir a data final de extensão para o dia seguinte, basta alterar o dia para o dia seguinte                                   |
| `extension_active`          | String   | Sim             | Flag utilizada para determinar se uma extensão está ativa. A extensão será ignorada no cálculo da jornada de trabalho caso seja inativada. <br> Padrão: True (ativa)                                                                 |

---

### Pesquisa por extensões ativas de horário por usuário

Este método permite visualizar todas as extensões de horários ativas dos usuários através do login, não serão retornadas as extensões que são antigas, ou seja, seu horário não é válido e extensões inativas.

#### Requisição

```http
GET /wsm/api/v1/overtime/account/{account_id}
HOST {urlAmbiente}
Content-Type: application/json

```

`{account_id}` – Login do usuário que será pesquisado

#### Resposta
- **HTTP 200 OK**: Pesquisa executada criada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos

```
[
  {
    "uid": "string",
    "extension_start_time": "2024-12-30T13:54:01.112Z",
    "extension_end_time": "2024-12-30T13:54:01.112Z",
    "extended_workhours_type": "string",
    "uf": "string",
    "c": 0,
    "week_days_count": "string",
    "extension_active": 0,
    "ou": 0,
    "id": 0
  }
]
```

### Notificações para o Agente WSM

Este é um método que será responsável por abrir um canal direto com agente WSM, notificando o usuário na estação em que está conectado.

A mensagem exibida será enviada na requisição, e aparecerá na tela do usuário em formato de notificação, se o usuário possuir mais de uma sessão ativa, a notificação irá aparecer em todas.


#### Requisição
```http
POST /wsm/api/v1/agent/action
HOST {urlAmbiente}
Content-Type: application/json
```

#### Resposta
- **HTTP 200 OK**: Extensão criada com sucesso
- **HTTP 400 Bad Request**: Atributos inválidos

```


[
  {
    "uid": "string",
    "extension_start_time": "2024-12-30T13:54:01.112Z",
    "extension_end_time": "2024-12-30T13:54:01.112Z",
    "extended_workhours_type": "string",
    "uf": "string",
    "c": 0,
    "week_days_count": "string",
    "extension_active": 0,
    "ou": 0,
    "id": 0
  }
]
```