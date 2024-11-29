import zmq, json
from src.logs.logger import Logger
from src.connections.database_manager import DatabaseManager
from src.config import config
from src.serialization.message_processor import MessageProcessor

class FlexibleRouterServerService:
    
    def __init__(self, bind_address="tcp://*:5555"):
        self.logger = Logger(log_name=self.__class__.__name__).get_logger()
        self.context = zmq.Context()
        self.bind_address = bind_address
        self.message_processor = MessageProcessor()
        self.dm = DatabaseManager()

        # socket ROUTER config
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(self.bind_address)


    def start(self):
        print("Flexible Router server started...")
        #self.logger.info("Flexible Router server started...")
        while True:
            # Receive two parts message: [identidade, mensagem]
            identity, message = self.socket.recv_multipart()

            ##NÃO POSSO DEIXAR DESSA FORMA
            #client_id = identity.decode()
            client_id = identity
            message_text = message.decode()
            client_id = client_id.decode()
            print(f"Received from {client_id}: {message_text}")
            
            # process the message
            self.handle_message(client_id, message_text)

    def handle_message(self, client_id, message):
        try:
            message_data = json.loads(message)
            print(f"Parsing message : {message_data}")
            if "Client" in message_data: # upsert CLient + need to return client info to client
                response =  self.message_processor.process_client_message(client_id,message_data["Client"])
            elif "Session" in message_data: # upsert Session
                response = self.message_processor.process_session_message(client_id,message_data["Session"])
            elif "DisconnectionRequest" in message_data: # when API sent a disconnection to a user
                response = self.message_processor.process_user_disconnection(message_data)
                client_id = response["hostname"]
            elif "SessionDisconnected" in message_data: # when client send the user was disconnected
                response = self.message_processor.process_user_already_disconnected(message_data)
            elif "RoutingClientMessage" in message_data:
                # Here we build the json for the client we get client_id because this message comes from RabbitMQ queue
                user = message_data["RoutingClientMessage"]["uid"]
                sessions = self.dm.get_sessions_by_uid(user)
                for session in sessions:
                    try:
                        client_id, response = self.message_processor.process_wsm_agent_updater_message(message_data, session.hostname)
                        self.send_message(client_id,response) 
                    except Exception as e :
                        self.logger.error(f"Could not send message to client, reason {e}")
                        continue
                return
            elif "LogonRequest" in message_data: # when client sent via 0MQ que user logon, need to return the entire work time
                response = self.message_processor.process_connected_user(message_data)
            elif "LockUnlock" in message_data:
                response = self.message_processor.process_lock_or_unlock_user(message_data)
            else:
                response = self.send_message(client_id,{"status":"error","message":"unknown message type"})
            self.send_message(client_id,response)       
        except json.JSONDecodeError:
            print("Failed to decode JSON message")
            self.send_message(client_id, {"status": "error", "message": "Invalid JSON format"})
        except Exception as e:
            self.logger.error(f"Cant process the request, reason: {e}")


    def send_message(self, client_id, message):
        """
        Envia uma mensagem arbitrária para um cliente específico.
        """
        json_message = json.dumps(message)
        self.socket.send_multipart([client_id.encode(),"".encode(), json_message.encode()])
        print(f"Sent to {client_id}: {json_message}")

    def stop(self):
        # Fecha o socket e termina o contexto
        self.socket.close()
        self.context.term()
        print("Flexible Router server stopped.")
