import zmq, json, base64
from src.logs.logger import Logger
from src.connections.database_manager import DatabaseManager
from src.config import config
from src.serialization.message_processor import MessageProcessor
from src.services.encripted_messages_services import CryptoMessages
from src.ca_services.ca_server import Server 

class FlexibleRouterServerService:
    
    def __init__(self, bind_address="tcp://*:"+config.Z_MQ_PORT):
        self.logger = Logger().get_logger()
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
            self.logger.info(f"Parsing message: {message_data}")
            response = self.route_message(client_id,message_data)
            if response:
                self.send_message(client_id,response)
            else:
                self.logger.warning("No response for message")
        except json.JSONDecoderError:
            self.logger.error("Failed to decode JSON message")
            self.send_message(client_id,{"status": "error","message":"Invalid JSON format"})
        except Exception as e:
            self.logger.error(f"Unable to process the request: {e}")
            self.send_message(client_id, {"status": "error", "message": "An unexpected error occurred"})

    def route_message(self, client_id, message_data):
        try:
            message_handlers = {
                "Client": lambda: self.handle_client_message(client_id, message_data["Client"]),
                "Session": lambda: self.handle_session_message(client_id, message_data["Session"]),
                "SessionDisconnected": lambda: self.handle_session_disconnection(message_data),
                "LockUnlock": lambda: self.handle_lock_unlock(message_data),
                "DisconnectionRequest": lambda: self.handle_disconnection_request(message_data),
                "RoutingClientMessage": lambda: self.handle_routing_client_message(message_data),
                "Heartbeat": lambda: self.handle_heartbeat(client_id, message_data),
                "LogonRequest": lambda: self.handle_logon_request(message_data),
                "CARequest": lambda: self.handle_ca_request(message_data["CARequest"]),
            }
            # Find the appropriate handler
            for key, handler in message_handlers.items():
                if key in message_data:
                    return handler()
            # Default case for unknown message types
            self.logger.warning(f"Unknown message type: {message_data}")
            return {"status": "error", "message": "Unknown message type"}
        except KeyError as e:
            self.logger.error(f"Missing expected key in message: {e}")
            return {"status": "error", "message": f"Invalid message structure: {e}"}
        except Exception as e:
            self.logger.error(f"Error routing message: {e}")
            raise
    
        # Individual handlers for each message type
    def handle_client_message(self, client_id, client_data):
        self.logger.info("Processing client message")
        return self.message_processor.process_client_message(client_id, client_data)

    def handle_session_message(self, client_id, session_data):
        self.logger.info("Processing session message")
        return self.message_processor.process_session_message(client_id, session_data)

    def handle_session_disconnection(self, message_data):
        self.logger.info("Processing session disconnection")
        return self.message_processor.process_user_already_disconnected(message_data)

    def handle_lock_unlock(self, message_data):
        self.logger.info("Processing lock/unlock message")
        return self.message_processor.process_lock_or_unlock_user(message_data)

    def handle_disconnection_request(self, message_data):
        self.logger.info("Processing disconnection request")
        response = self.message_processor.process_user_disconnection(message_data)
        client_id = response.get("hostname")
        self.send_message(client_id, response)

    def handle_routing_client_message(self, message_data):
        self.logger.info("Processing routing client message")
        user = message_data["RoutingClientMessage"].get("uid") or message_data["RoutingClientMessage"].get("user")
        sessions = self.dm.get_sessions_by_uid(user)

        for session in sessions:
            try:
                hostname = session.hostname
                if "user" in message_data["RoutingClientMessage"]:
                    client_id, response = self.message_processor.process_direct_message(message_data, hostname)
                else:
                    client_id, response = self.message_processor.process_wsm_agent_updater_message(message_data, hostname)
                self.send_message(client_id, response)
            except Exception as e:
                self.logger.error(f"Could not send message to client: {e}")
                continue

    def handle_heartbeat(self, client_id, message_data):
        self.logger.info("Processing heartbeat")
        return self.message_processor.process_client_message(client_id, message_data)

    def handle_logon_request(self, message_data):
        self.logger.info("Processing logon request")
        return self.message_processor.process_connected_user(message_data)

    def handle_ca_request(self, ca_request):
        self.logger.info("Processing CA request")
        return self.ca_srvr.processRequests(json.loads(ca_request))

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
        self.logger.info(f" WSM - simple_route_server_service - Sent to {client_id}: {json_message}")

    def stop(self):
        # Fecha o socket e termina o contexto
        self.socket.close()
        self.context.term()
        self.logger.info(" WSM - simple_route_server_service - Flexible Router server stopped.")
