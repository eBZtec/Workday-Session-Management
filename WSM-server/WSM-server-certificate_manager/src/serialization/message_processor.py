from src.models.models import Sessions, Client, Events
from src.connections.database_manager import DatabaseManager
from src.logs.logger import Logger
from src.config import config
from sqlalchemy.inspection import inspect

class MessageProcessor:

    def __init__(self):
        self.logger = Logger(log_name=self.__class__.__name__).get_logger()


    def process_client_message(self, ZMQ_client_id, client_data):
        try:
            client = Client(
                hostname = client_data.get("hostname"),
                ip_address = client_data.get("ip_address"),
                client_version = client_data.get("client_version"),
                os_name = client_data.get("os_name"),
                os_version = client_data.get("os_version"),
                agent_info = client_data.get("agent_info"),
                create_timestamp = client_data.get("create_timestamp"),
                update_timestamp = client_data.get("update_timestamp")
                )
            dm = DatabaseManager()
            existing_client = dm.get_by_hostname(Client,client_data.get("hostname"))          
            if existing_client:
                #SqlAlchemy obj to dict()
                client = {c.key: getattr(client, c.key) for c in inspect(client).mapper.column_attrs}
                client.update({"id":existing_client.id})
                client.update({"create_timestamp": existing_client.create_timestamp})
                dm.update_entry(Client,existing_client.id,client)
            else:
                dm.add_entry(client)     
            self.logger.info(f"Processing Client: Hostname={client_data.get("hostname")}, IP={client_data.get("ip_address")},"
              f"Version={client_data.get("client_version")}, OS={client_data.get("os_name")} {client_data.get("os_version")}, Agent={client_data.get("agent_info")}")
            # return confirmation
            message = {"status": "success", "message": "Client information processed"}
            self.logger.info(message)
            return message
        except KeyError as e:
            # return this error when the key in the json is not found
            message = {"status": "error", "message": f"Missing key in client data: {str(e)}"}
            self.logger.error(message)
            return message
        except Exception as e:
            # capture other errors
            message = {"status": "error", "message": f"An error occurred while processing client data: {str(e)}"}
            self.logger.error(message)
            return message

        
    def process_session_message(self, ZMQ_client_id, session_data):
        """
            Processa mensagens do tipo "Session".
        """
        try:
            dm = DatabaseManager()
            session = Sessions(
                client_id=dm.get_id_by_hostname(Client, session_data.get("hostname"))[0],
                hostname = session_data.get("hostname"),
                event_type=session_data.get("event_type"),
                start_time=session_data.get("start_time"), 
                end_time=session_data.get("end_time"), 
                user=session_data.get("user"),
                status=session_data.get("status")
            )
            # Verifica se a sessão já existe
            existing_session = dm.get_by_hostname(Sessions, session_data.get("hostname"))
            if existing_session:
                # Converte o objeto de sessão para um dicionário e atualiza com dados existentes
                session_dict = {c.key: getattr(session, c.key) for c in inspect(session).mapper.column_attrs}
                session_dict.update({
                    "id": existing_session.id,
                    "create_timestamp": existing_session.create_timestamp
                })
                try:
                    dm.update_entry(Sessions, existing_session.id, session_dict)
                    message = (f"Processing Session: ID={session_dict['client_id']}, User={session_dict['user']}, "
                        f"Start={session_dict['start_time']}, End={session_dict['end_time']}, Status={session_dict['status']}")
                    self.logger.info(message)
                    return message
                except Exception as e:
                    self.logger.error(f"Error updating session: {e}")
            else:
                # Adiciona uma nova entrada se não houver uma sessão existente
                try:
                    dm.add_entry(session)
                    message = (f"Processing New Session: ID={session.client_id}, User={session.user}, "
                        f"Start={session.start_time}, End={session.end_time}, Status={session.status}")
                    self.logger.info(message)
                    return message
                except Exception as e:
                    self.logger.error(f"Error adding new session: {e}")
        except Exception as e:
            self.logger.error(f"Error processing session message: {e}")
        
    
    # Keep there but maybe this is not usable, because the events will be preinserted into db, that wont come from client
    def process_event_message(self,ZMQ_client_id, event_data):
        """
        Processa mensagens do tipo "Event".
        """
        try:
            dm = DatabaseManager()
            event = Events(
                event_type = event_data.get('event_type'),
                description = event_data.get('description')
            )
            existing_event = dm.get_event_by_event_type(Events,event_data.get('event_type'))
            if existing_event:
                event = {c.key: getattr(event, c.key) for c in inspect(event).mapper.column_attrs}
                event.update({"id":existing_event.id})
                event.update({"create_timestamp": existing_event.create_timestamp})
                dm.update_entry(Events,existing_event.id,event)
            else:
                dm.add_entry(event)
            # Retorna uma confirmação
            message = {"status": "success", "message": "Event information processed"}
            print(message)
            # self.logger.info(message)
            return message
        except KeyError as e:
            message = {"status": "error", "message": f"Missing key in event data: {str(e)}"}
            print(message)
            # self.logger.error(message)
            return message
        except Exception as e:
            # capture other errors
            message = {"status": "error", "message": f"An error occurred while processing event data: {str(e)}"}
            print(message)
            # self.logger.error(message)
            return message