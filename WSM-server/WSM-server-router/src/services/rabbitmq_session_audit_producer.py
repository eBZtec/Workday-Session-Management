import pika
import json
from src.config import config


class RabbitMQSessionAuditProducer:
    def __init__(self, host: str = config.AUDIT_QUEUE_HOST, queue_name: str = config.AUDIT_QUEUE):
        """
        Inicializa o producer do RabbitMQ.
        
        :param host: Endereço do RabbitMQ
        :param queue_name: Nome da fila para envio de mensagens
        """
        self.host = host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        """
        Conecta ao RabbitMQ e inicializa o canal.
        """
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def send_message(self, table: str, data: dict):
        """
        Envia uma mensagem para a fila.

        :param table: Nome da tabela relacionada aos dados
        :param data: Dados no formato dicionário
        """
        try:
            if not self.channel or self.channel.is_closed:
                self._connect()
            
            message = {
                "table": table,
                "data": data
            }

            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)  # Mensagem persistente
            )

            print(f"[x] Mensagem enviada para o RabbitMQ na fila:{self.queue_name} - {message}")
        except pika.exceptions.AMQPConnectionError as conn_error:
            print(f"[Erro de Conexão] Falha ao conectar ao RabbitMQ: {conn_error}")
        except json.JSONDecodeError as json_error:
            print(f"[Erro de JSON] Falha ao codificar os dados da mensagem: {json_error}")
        except Exception as e:
            print(f"[Erro Genérico] Um erro inesperado ocorreu: {e}")

    def close(self):
        """
        Fecha a conexão com o RabbitMQ.
        """
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("[x] Conexão com RabbitMQ encerrada.")