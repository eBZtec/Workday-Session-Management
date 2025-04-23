import zmq

class ZMQClient:
    def __init__(self, server_address="tcp://localhost:5555"):
        self.server_address = server_address
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(self.server_address)

    def send_message(self, message: str) -> str:
        # Envia mensagem
        self.socket.send_string(message)

        # Aguarda resposta
        response = self.socket.recv_string()
        return response

    def close(self):
        self.socket.close()
        self.context.term()
