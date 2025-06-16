import json
from src.logs.logger import logger


class MessageProcessor:
    """
    Classe responsável por processar as mensagens recebidas.
    """

    def __init__(self, zmq_sender):
        self.zmq_sender = zmq_sender
        self.logger = logger

    def process_message(self, message):
        """
        Processa a mensagem recebida e a envia via ZeroMQ.
        
        :param message: Mensagem JSON recebida.
        """
        try:
            data = json.loads(message)
            data = {"RoutingClientMessage":data}
            self.zmq_sender.send(data)
        except json.JSONDecodeError:
            self.logger.error("Mensagem recebida não é um JSON válido.")
        except Exception as e:
            self.logger.error(f"Erro ao processar a mensagem: {str(e)}")