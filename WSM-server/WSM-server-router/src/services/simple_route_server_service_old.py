import zmq, json, base64
from src.logs.logger import Logger
from src.connections.database_manager import DatabaseManager
from src.config import config
from src.serialization.message_processor import MessageProcessor
from src.services.encripted_messages_services import CryptoMessages
from src.ca_services.ca_server import Server 

class FlexibleRouterServerService:
    
    def __init__(self, bind_address="tcp://*:"+config.Z_MQ_PORT):
        self.logger = Logger(log_name='WSM-Router').get_logger()
        self.context = zmq.Context()
        self.bind_address = bind_address
        self.message_processor = MessageProcessor()
        self.dm = DatabaseManager()
        self.cm = CryptoMessages()
        self.ca_srvr = Server()

        # socket ROUTER config
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(self.bind_address)


    def start(self):
        self.logger.info("WSM - simple_route_server_service - Flexible Router server started...")
        #self.logger.info("Flexible Router server started...")
        while True:

            try:    
                # Receive two parts message: [identidade, mensagem]
                identity, message = self.socket.recv_multipart()
                client_id = identity
                message_text = message.decode()
                client_id = client_id.decode()
                self.logger.info(f"WSM - simple_route_server_service - Received from {client_id}: {message_text}")
                
                # process the message
                self.handle_message(client_id, message_text)
            except zmq.ZMQError as e:
                self.logger.error(f"WSM - simple_route_server_service - ZQM error: {e}")
            except UnicodeDecodeError as e:
                self.logger.error(f"WSM - simple_route_server_service - Decoding error: {e}")
            except Exception as e:
                self.logger.error(f"WSM - simple_route_server_service - Unexpected error: {e}")

    def handle_message(self, client_id, message):
        try:
            message_data = json.loads(message)
            self.logger.info(f"WSM - simple_route_server_service - Parsing message : {message_data}")
            # FROM CLIENTS
            if "Client" in message_data: # upsert CLient + need to return client info to client
                response =  self.message_processor.process_client_message(client_id,message_data["Client"])
                self.send_message(client_id,response)
            elif "Session" in message_data: # upsert Session
                response = self.message_processor.process_session_message(client_id,message_data["Session"])
                self.send_message(client_id,response)
            elif "SessionDisconnected" in message_data: # when client send the user was disconnected
                response = self.message_processor.process_user_already_disconnected(message_data)
                self.send_message(client_id,response)
            elif "LockUnlock" in message_data:
                response = self.message_processor.process_lock_or_unlock_user(message_data)
                self.send_message(client_id,response)

            #FROM API
            elif "DisconnectionRequest" in message_data: # when API sent a disconnection to a user
                response = self.message_processor.process_user_disconnection(message_data)
                client_id = response["hostname"]
                self.send_message(client_id,response)
            elif "RoutingClientMessage" in message_data:
                # Here we build the json for the client we get client_id because this message comes from RabbitMQ queue

                if "uid" in message_data["RoutingClientMessage"]: 
                    user = message_data["RoutingClientMessage"]["uid"]
                elif "user" in message_data["RoutingClientMessage"]: #direct message send "user" attr
                    user = message_data["RoutingClientMessage"]["user"]
                sessions = self.dm.get_sessions_by_uid(user)
                for session in sessions:
                    try:
                        if "user" in message_data["RoutingClientMessage"]:
                            client_id, response = self.message_processor.process_direct_message(message_data,session.hostname)
                            self.send_message(client_id,response)
                        else:
                            client_id, response = self.message_processor.process_wsm_agent_updater_message(message_data, session.hostname)
                            self.send_message(client_id,response) 
                    except Exception as e :
                        self.logger.error(f"WSM - simple_route_server_service - Could not send message to client, reason {e}")
                        continue
                return
            elif "Heartbeat" in message_data:
                response =  self.message_processor.process_client_message(client_id,message_data)
                # response = {"status": "beating", "message": "Done"}
                self.send_message(client_id,response)
            elif "LogonRequest" in message_data: # when client sent via 0MQ que user logon, need to return the entire work time
                response = self.message_processor.process_connected_user(message_data)
                self.send_message(client_id,response)
            elif "CARequest" in message_data:
                response = self.ca_srvr.processRequests(message_data, client_id)
                self.send_message(client_id,response)
            else:
                response = self.send_message(client_id,{"status":"error","message":"unknown message type"})
            #self.send_message(client_id,response)       
        except json.JSONDecodeError:
            self.logger.error("WSM - simple_route_server_service - Failed to decode JSON message")
            self.send_message(client_id, {"status": "error", "message": "Invalid JSON format"})
        except Exception as e:
            self.logger.error(f"Cant process the request, reason: {e}")


    #SEND ENCRYPTED MESSAGE TO CLIENT
    def encrypt_message(self,hostname,message):
        public_key = self.cm.load_public_key(hostname)

        aes_key, aes_iv = self.cm.generate_aes_key_iv()
        encrypted_message = self.cm.encrypt_message_aes(message, aes_key, aes_iv)

        encrypted_aes_key = self.cm.encrypt_rsa(aes_key, public_key)
        encrypted_aes_iv = self.cm.encrypt_rsa(aes_iv, public_key)

        # Construct the payload
        payload = {
            "EncryptedAESKey": base64.b64encode(encrypted_aes_key).decode(),
            "EncryptedAESIV": base64.b64encode(encrypted_aes_iv).decode(),
            "EncryptedMessage": base64.b64encode(encrypted_message).decode()
        }
        # message = json.dumps(payload, indent=4)
        message = json.dumps(payload)
        # print(message)
        return message
    
    # PROCESS ENCRYPTD MESSAGE FROM CLIENT
    def process_encrypted_message(self,message):
        # Load private RSA key for decrypting AES key and IV
        private_key = self.cm.load_private_key()
        data = json.loads(message)
        self.logger.info("\nResponse JSON message:\n", json.dumps(data, indent=4))
        encrypted_message = base64.b64decode(data["EncryptedMessage"])
        decrypted_aes_key = self.cm.decrypt_rsa(base64.b64decode(data["EncryptedAESKey"]), private_key)
        decrypted_aes_iv = self.cm.decrypt_rsa(base64.b64decode(data["EncryptedAESIV"]), private_key)
        decrypted_message = self.cm.decrypt_message(encrypted_message, decrypted_aes_key, decrypted_aes_iv)
        return decrypted_message

    def send_message(self, client_id, message):
        """
        Envia uma mensagem arbitrária para um cliente específico.
        """
        """
        message = self.encrypt_message(client_id,message)
        self.socket.send_multipart([client_id.encode(),"".encode(), message.encode()])
        self.logger.info(f" WSM - simple_route_server_service - Sent to {client_id}: {message}")
        """
        json_message = json.dumps(message)
        self.socket.send_multipart([client_id.encode(),"".encode(), json_message.encode()])
        self.logger.info(f" WSM - simple_route_server_service - Sent to {client_id}")

    def stop(self):
        # Fecha o socket e termina o contexto
        self.socket.close()
        self.context.term()
        self.logger.info(" WSM - simple_route_server_service - Flexible Router server stopped.")
