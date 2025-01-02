# WSM - WORKDAY SESSION MANAGEMENT
## 1. Overview

WSM is a set of python services with focus on manage and calculate daily working hours. This entire project are build keeping in mind integrations with main daily working hours management systems like Microsoft Active Directory, IBM Resource Access Control Facility (RACF).
The entire project are separated in five main aplications:
 1. **Session Server**: API that are built with FASTApi tecnology, this part of project hold the entire endpoints to manage user working hours, add, update and remove data that corresponds to clients working hours and also get direct messages from the user of interface, like HR employees to clients. Thats the main user interface.

 2. **Session Updater Connector**: This component read a rabbitMQ queue called "pooling_contas" that is populated from API and deliver this messages to other queues that the name are the same inserted previously into database in table "targets". Each target represent a new queue and a new resource like AD or RACF resource.

 3. **Session Agent Updater**: The main ideia to this component is a reader from rabbitMQ queue called "session_agent" and rewrite the message to a new ZeroMQ queue with ROUTER-DEALER method, this new queue will be read to a other component. This component only holds a client messages like workhours update/insert and direct messages.

 4. **WSM Router**: This component manage the entire messages with client, redirect API messages to clients or receive/response client criptographed messages. This component works like a Certificate Authority too, doing all the response and receive certificate assign requests etc.

 5. **WSM AD Connector**: This component read basically the same messages that Session Agent Updater read, but redirects into ZeroMQ queue to AD Service, using 0MQ with request response method.

 6. **WSM Archive Processor**: This component manages rabbitMQ messages from WSM Router that refers to users sessions that make logon or logoff events in the client and store into audit database.

 Below we have a entire project structure, the components in red refers to this components that we explain earlier:

![WSM Project Structure]( /fluxo-wsm-session-server.drawio.png "WSM Project Structure")


The database structure are deployed using PosgreSQL, and here we have the structure, keep in mind that structures will be change in the future, when this entire solution will be upgraded.


 ![WSM Session database structure]( /WSM.png "WSM Session Database Structure")


In the last but not the least each project module is discribed into README files inside the module directory.
