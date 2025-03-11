import zmq
from src.logs.logger import Logger
import json

class ZeroMQSender:
    """
    Classe responsável por enviar mensagens via ZeroMQ.
    """

    def __init__(self,router_queue, client_id ="wsm-agent-updater",):
        self.logger = Logger(log_name='WSM Server Agent Updater').get_logger()
        self.router_queue = router_queue
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.identity = client_id.encode()
        self.socket.connect(self.router_queue)
        

    def send(self, message):
        """
        Envia uma mensagem via ZeroMQ.
        
        :param client_id: Identidade do cliente (hostname).
        :param message: Mensagem JSON a ser enviada.
        """
        try:
            if "uid" in message["RoutingClientMessage"]:
                uid = message["RoutingClientMessage"]["uid"]
                message = json.dumps(message, ensure_ascii=False)
                self.socket.setsockopt(zmq.IDENTITY, self.socket.identity)
                self.socket.send_string(message)
                self.logger.info(f"Mensagem enviada para client_uid= {uid}: {message}")
            elif "user" in message["RoutingClientMessage"]:
                uid = message["RoutingClientMessage"]["user"]
                message = json.dumps(message, ensure_ascii=False)
                self.socket.setsockopt(zmq.IDENTITY, self.socket.identity)
                self.socket.send_string(message)
                self.logger.info(f"Mensagem enviada para client_uid= {uid}: {message}")
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem via ZeroMQ: {str(e)}")

    def close(self):
        """
        Encerra o socket e o contexto ZeroMQ.
        """
        self.socket.close()
        self.context.term()