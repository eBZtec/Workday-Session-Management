import zmq, json
from src.logs.logger import Logger
from src.config import config
from src.serialization.message_processor import MessageProcessor

class FlexibleRouterServerService:
    
    def __init__(self, bind_address="tcp://*:5555"):
        self.logger = Logger(log_name=self.__class__.__name__).get_logger()
        self.context = zmq.Context()
        self.bind_address = bind_address
        self.message_processor = MessageProcessor()

        # socket ROUTER config
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(self.bind_address)


    def start(self):
        print("Flexible Router server started...")
        #self.logger.info("Flexible Router server started...")
        while True:
            # Receive two parts message: [identidade, mensagem]
            identity, message = self.socket.recv_multipart()
            client_id = identity.decode()
            message_text = message.decode()
            print(f"Received from {client_id}: {message_text}")
            # process the message
            self.handle_message(client_id, message_text)


    def handle_message(self, client_id, message):
        try:
            message_data = json.loads(message)
            print(f"Parsing message : {message_data}")
            if "Client" in message_data:
                response =  self.message_processor.process_client_message(client_id,message_data["Client"])
            elif "Session" in message_data:
                response = self.message_processor.process_session_message(client_id,message_data["Session"])
            elif "Event" in message_data:
                response = self.message_processor.process_event_message(client_id,message_data["Event"])
            else:
                response = self.send_message(client_id,{"status":"error","message":"unknown message type"})
            self.send_message(client_id,response)
           
        except json.JSONDecodeError:
            print("Failed to decode JSON message")
            self.send_message(client_id, {"status": "error", "message": "Invalid JSON format"})


    def send_message(self, client_id, message):
        """
        Envia uma mensagem arbitrária para um cliente específico.
        """
        json_message = json.dumps(message)
        self.socket.send_multipart([client_id.encode(), json_message.encode()])
        print(f"Sent to {client_id}: {json_message}")


    def stop(self):
        # Fecha o socket e termina o contexto
        self.socket.close()
        self.context.term()
        print("Flexible Router server stopped.")
