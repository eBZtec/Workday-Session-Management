import zmq, json, base64, re, threading, time, datetime, pytz
from src.logs.logger import logger
from src.connections.database_manager import DatabaseManager
from src.connections.database_manager_audit import DatabaseManagerAudit
from src.config import config
from src.serialization.message_processor import MessageProcessor
from src.services.encripted_messages_services import CryptoMessages
from src.ca_services.ca_server import Server 
from src.services.zmq_client import ZMQClient
from src.models.models import Client, Sessions


class FlexibleRouterServerService:
    
    def __init__(self, bind_address="tcp://*:"+config.Z_MQ_PORT):
        
        self.logger = logger
        self.context = zmq.Context()
        self.bind_address = bind_address
        self.message_processor = MessageProcessor()
        self.dm = DatabaseManager()
        self.dma = DatabaseManagerAudit()
        self.cm = CryptoMessages()
        self.ca_srvr = Server()
        # socket ROUTER config
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.setsockopt(zmq.ROUTER_HANDOVER, 1)  ## This configuration can't allow to replace a new connection dealer with same id, this keep the same connection
        self.socket.bind(self.bind_address)


    """
    SESSION CLEANING 
    """

    def start_cleanup_thread(self):
        def periodic_cleanup_loop():
            self.logger.info(f"[CLEANUP THREAD] Starting Cleanup Thread")
            try:
                cln_interval = int(config.CLEANUP_INTERVAL_MINUTES)
            except ValueError:
                self.logger.error(f"[CLEANUP THREAD] Invalid CLEANUP_INTERVAL_MINUTES, using default 40 minutes")
                cln_interval = 40  #Default 40 minutes AFTER ROUTER WAS INITIALIZED, NOT after last cleanup

            while True:
                try:
                    self.cleanup_inactive_sessions(int(config.CLEANUP_THRESHOLD_MINUTES))
                except Exception as e:
                    self.logger.error(f"[CLEANUP THREAD] Error during session cleaning: {e}")
                time.sleep(cln_interval * 60)

        def initial_cleanup_once():
            try:
                self.logger.info("[CLEANUP THREAD] Executando limpeza inicial...")
                self.cleanup_inactive_sessions(int(config.CLEANUP_THRESHOLD_MINUTES))
                self.logger.info("[CLEANUP THREAD] Limpeza inicial concluída.")
            except Exception as e:
                self.logger.error(f"[CLEANUP THREAD] Erro durante a limpeza inicial: {e}")

        # Executa a limpeza inicial em uma thread separada
        threading.Thread(target=initial_cleanup_once, daemon=True).start()

        # Executa a limpeza periódica
        threading.Thread(target=periodic_cleanup_loop, daemon=True).start()

    def cleanup_inactive_sessions(self, threshold_minutes):
        now = datetime.datetime.now(pytz.UTC)
        threshold_minutes = int(threshold_minutes)
        cutoff = now - datetime.timedelta(minutes=threshold_minutes)

        try:
            # Search all sessions with dada associated to clients

            joined_sessions = self.dm.get_sessions_joined_with_client(hostname=None)

            for session_data in joined_sessions:
                hostname = session_data.hostname
                user = session_data.user
                last_contact = session_data.client_update_timestamp

                if last_contact and last_contact < cutoff:
                    self.logger.warning(f"[CLEANUP] Inactive Host: {hostname} (Last Contact : {last_contact})")

                    # Mounting dict with audit_table format

                    session_dict = {
                        "hostname": hostname,
                        "event_type": "logout",
                        "login": user,
                        "status": "disconnected",
                        "start_time": session_data.start_time,
                        "end_time": now,
                        "create_timestamp": session_data.session_create_timestamp,
                        "update_timestamp": now,
                        "os_version": session_data.os_version,
                        "os_name": session_data.os_name,
                        "ip_address": session_data.ip_address,
                        "client_version": session_data.client_version,
                        "agent_info": session_data.agent_info
                    }

                    try:
                        self.dma.insert_cleaned_session(**session_dict)
                        self.logger.info(f"[CLEANUP] Audited session to: '{hostname}/{user}'")
                    except Exception as e:
                        self.logger.error(f"[CLEANUP] Error to audit session: {hostname}{user}: {e}")
                    

                    try:
                        self.dm.delete_user_disconnected(Sessions,session_dict['hostname'], session_dict['login'])
                        self.logger.info (f"[CLEANUP] Session of {hostname}{user} successfully removed.")
                    except Exception as e :
                        self.logger.error(f"[CLEANUP] Error when trying to remove database session of {hostname}{user}: {e}")
        except Exception as e:
            self.logger.error(f"[CLEANUP] Search for sessions/clients failed: {e} ")

    """
        END SESSION CLEANING
    """

    def start(self):
        self.logger.info("WSM - simple_route_server_service - Flexible Router server started...")
        self.start_cleanup_thread()
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        self.logger.debug("WSM - simple_route_server_service - Waiting for messages...")
        while True:
            try:    
                socks = dict(poller.poll(timeout=100))
                if self.socket in socks and socks[self.socket]== zmq.POLLIN:
                    # Receive two parts message: [identidade, mensagem]
                    multipart_msg = self.socket.recv_multipart()
                    self.logger.info(f"Message received:{multipart_msg}")
                    waiting_logged = False  # Reset flag
                    if len(multipart_msg) >=2:
                        identity, message = multipart_msg
                        client_id = identity
                        message_text = message.decode()
                        client_id = client_id.decode()
                        #self.logger.info(f"WSM - simple_route_server_service - Received from {client_id}: {message_text}")
                        self.logger.info(f"WSM - simple_route_server_service - Received from {client_id}:")
                        # process the message
                        self.handle_message(client_id, message_text)
                    else:
                        self.logger.warning(f"WSM - simple_route_server_service - Malformed message: {multipart_msg}")
            except zmq.ContextTerminated:
                self.logger.info("WSM - simple_route_server_service -  ZMQ context terminated, terminate server.")
            except zmq.Again:
                self.logger.debug("WSM - simple_route_server_service - No message received")
            except zmq.ZMQError as e:
                self.logger.error(f"WSM - simple_route_server_service - ZQM error: {e}")
            except UnicodeDecodeError as e:
                self.logger.error(f"WSM - simple_route_server_service - Decoding error: {e}")
            except Exception as e:
                self.logger.error(f"WSM - simple_route_server_service - Unexpected error: {e}")

    def message_is_encrypted(self, data):
        try:
            #data = json.loads(message)
            required_keys = {"EncryptedMessage", "EncryptedAESKey", "EncryptedAESIV" }
            if required_keys.issubset(data.keys()):
                return True
            else:
                self.logger.info("JSON is not encrypted - CA request")
                return False
        except Exception as e:
            self.logger.error("Failed to check if message is encrypted or not")
            return False
            
    def decrypt_json_message(self, message):
        try:
            private_key = self.cm.load_private_key()
            encrypted_message = base64.b64decode(message["EncryptedMessage"])
            decrypted_aes_key = self.cm.decrypt_rsa(base64.b64decode(message["EncryptedAESKey"]), private_key)
            decrypted_aes_iv = self.cm.decrypt_rsa(base64.b64decode(message["EncryptedAESIV"]), private_key)
            decrypted_message = self.cm.decrypt_message(encrypted_message, decrypted_aes_key, decrypted_aes_iv)
            
            #self.logger.info(f"\n\nDecrypted_message: {decrypted_message}")
            
            # Remove caracteres não imprimíveis usando regex
            cleaned_data = re.sub(r'[\x00-\x1F\x7F]+$', '', decrypted_message)
            cleaned_data = json.loads(cleaned_data)
            return cleaned_data
        
        except Exception as e:
            self.logger.error(f"Error while decrypting the following message: {message}")

        
    def handle_message(self, client_id, message):
        try:
            message_data = json.loads(message)

            if "EncryptedAESKey" not in message_data:

                self.logger.info(f"Parsing message: {message_data}")

            if self.message_is_encrypted(message_data) == False:
                response = self.route_message(client_id,message_data)
            else:
                decrypted_message = self.decrypt_json_message(message_data)
                response = self.route_message(client_id,decrypted_message)
    
            if response and ('CARequest') in message_data:
                self.send_message(client_id,response, False)
            elif response and ('CARequest') not in message_data:
                self.send_message(client_id,response, True)
            else:
                self.logger.warning("No response for message")
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON message")
            self.send_message(client_id,{"status": "error","message":"Invalid JSON format"}, False)
        except Exception as e:
            self.logger.error(f"Unable to process the request: {e}")
            self.send_message(client_id, {"status": "error", "message": "An unexpected error occurred"}, False)

    def route_message(self, client_id, message_data):
        try:
            message_handlers = {
                "Client": lambda: self.handle_client_message(client_id, message_data["Client"]),
                "Session": lambda: self.handle_session_message(client_id, message_data["Session"]),
                "SessionDisconnected": lambda: self.handle_session_disconnection(message_data), # Client send user disconnection
                "LockUnlock": lambda: self.handle_lock_unlock(message_data),
                "DisconnectionRequest": lambda: self.handle_disconnection_request(message_data), # when API sent a disconnection to a user
                "RoutingClientMessage": lambda: self.handle_routing_client_message(message_data), # API Comunication to client, to update workhours or sent direct message
                "Heartbeat": lambda: self.handle_heartbeat(client_id, message_data), #Cli sent heartbeatin and creation/update into client table
                "LogonRequest": lambda: self.handle_logon_request(message_data), # Client sent a request to check if is allowed to login (check workhours )
                "CARequest": lambda: self.handle_ca_request(message_data,client_id), #Requests from cli or AD to certificates.
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

    def handle_session_disconnection(self, message_data): # Client send user disconnection
        self.logger.info("Processing session disconnection")
        return self.message_processor.process_user_already_disconnected(message_data)

    def handle_lock_unlock(self, message_data):
        self.logger.info("Processing lock/unlock message")
        return self.message_processor.process_lock_or_unlock_user(message_data)

    def handle_disconnection_request(self, message_data): # when API sent a disconnection to a user
        self.logger.info("Processing disconnection request")
        response = self.message_processor.process_user_disconnection(message_data)
        client_id = response.get("hostname")
        self.send_message(client_id, response, True)

    def handle_routing_client_message(self, message_data):
        self.logger.info("Processing routing client message")

        if message_data["RoutingClientMessage"].get("journey") == "FLEX_TIME": # if the user get flex_time, it will call 0MQ server to get workhours
            if "user" in message_data["RoutingClientMessage"]:
                message_data = self.get_response_flex_time(message_data["RoutingClientMessage"]["user"])

        user = message_data["RoutingClientMessage"].get("uid") or message_data["RoutingClientMessage"].get("user")
        sessions = self.dm.get_sessions_by_uid(user)

        for session in sessions:
            try:
                hostname = session.hostname
                if "user" in message_data["RoutingClientMessage"]:
                    client_id, response = self.message_processor.process_direct_message(message_data, hostname) # Send direct message to session/client
                else:    
                    client_id, response = self.message_processor.process_wsm_agent_updater_message(message_data, hostname) #Update session/client workhours
                self.send_message(client_id, response, True)
            except Exception as e:
                self.logger.error(f"Could not send message to client: {e}")
                continue

    def get_response_flex_time(self, user):
        cli = ZMQClient("tcp://localhost:52555") 
        try:
            response = cli.send_message(user)
            return response
        finally:
            cli.close()

    def handle_heartbeat(self, client_id, message_data):
        self.logger.info("Processing heartbeat")
        return self.message_processor.process_client_message(client_id, message_data)

    def handle_logon_request(self, message_data):
        self.logger.info("Processing logon request")
        return self.message_processor.process_connected_user(message_data)

    def handle_ca_request(self, message_data, client_id):
        self.logger.info("Processing CA request")
        var = self.ca_srvr.processRequests(message_data,client_id)
        #print("var: ", var)
        return var

    #SEND ENCRYPTED MESSAGE TO CLIENT
    def encrypt_message(self,hostname,message):        
        print("Message without encryption: ", message)
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
        #print(message)
        return message

    def send_message(self, client_id, message, to_encrypt):
        if to_encrypt:
            message = json.dumps(message)
            encrypted_message = self.encrypt_message(client_id,message)
            self.socket.send_multipart([client_id.encode(),"".encode(), encrypted_message.encode()])
            self.logger.info(f" WSM - simple_route_server_service - Sent ENCRYPTED to {client_id}")
        else:
            json_message = json.dumps(message)
            self.socket.send_multipart([client_id.encode(),"".encode(), json_message.encode()])
            self.logger.info(f" WSM - simple_route_server_service - Sent NOT encrypted to {client_id}")


    def stop(self):
        # Fecha o socket e termina o contexto
        self.socket.close()
        self.context.term()
        self.logger.info(" WSM - simple_route_server_service - Flexible Router server stopped.")

   
