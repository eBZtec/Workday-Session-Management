import zmq
import time
import json

class SimpleDealerClient:
    def __init__(self, client_id="fixed-id", connect_address="tcp://localhost:5555"):
        self.context = zmq.Context()
        self.connect_address = connect_address

        # Configuração do socket DEALER
        self.socket = self.context.socket(zmq.DEALER)
        self.socket.identity = client_id.encode()  # Unique identity for client
        self.socket.connect(self.connect_address)

    def send_message(self, message):
        """
        Envia uma mensagem para o servidor.
        """
        json_message = json.dumps(message)
        self.socket.send(json_message.encode())
        print(f"Sent: {json_message}")

    def receive_message(self):
        """
        Recebe uma mensagem do servidor.
        """
        try:
            json_message = self.socket.recv(flags=zmq.NOBLOCK).decode()
            message= json.loads(json_message)
            print(f"Received: {message}")
        except zmq.Again:
            # Nenhuma mensagem foi recebida no momento
            pass
        except json.JSONDecoderError:
            print("Failed to decode JSON message")

    def close(self):
        # Fecha o socket e termina o contexto
        self.socket.close()
        self.context.term()
        print("Client closed.")


if __name__ == "__main__":
    client = SimpleDealerClient(client_id="client-123")

    try:
        # Enviar mensagens de teste para o servidor
        
        """
        client.send_message(
            {"Client":{
                "hostname":"client_safra_host",
                 "ip_address":"192.168.4.6",
                 "client_version":"1.5.1",
                 "os_name":"GNU/Linux",
                 "os_version":"6.9.0-47-generic",
                 "agent_info": None
                }
            }
        )
        
        """
        client.send_message(
            {"Session":{
                "hostname":"client_safra_host",
                "event_type": "4624",
                "user": "Outro cara logo ali",
                "status":"opened",
                "start_time":"2024-10-24 13:32:45.64553-03",
                "end_time":None
            }})
        """
        
        client.send_message(
            {"Event":
                {
                    "event_type": "4624",
                    "description": "A user successfully logged on to a computer"
                }
            }
        )

        """
        # Aguardar para receber mensagens do servidor
        for _ in range(5):
            client.receive_message()
            time.sleep(1)

    finally:
        client.close()

