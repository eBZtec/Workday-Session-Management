import os
import zmq
import json
import base64
import argparse
import pika
import datetime
import logging

from logging.handlers import TimedRotatingFileHandler
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography import x509
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os


logger = logging.getLogger('zmqServer_logger')
logger.setLevel(logging.DEBUG)
load_dotenv()

handler = TimedRotatingFileHandler(
    'zmqServer.log',  # Nome do arquivo
    when='D',  # Roda com base no dia
    interval=7,  # Intervalo de 7 dias
    backupCount=2,  # Número de backups. 0 apaga logs antigos.
)
handler.setLevel(logging.DEBUG)

# Formatting log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add  handler to logger
logger.addHandler(handler)


# RabbitMQ Reader Class
class RabbitMQReader:
    def __init__(self, queue_name, host='localhost'):
        self.queue_name = queue_name
        self.host = host
        self.data = None  # Variable to store the RabbitMQ message

    def connect(self):
        """Connect to RabbitMQ."""
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=True)

    def consume_message(self):
        """Consume a single message from the queue."""
        method_frame, _, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        if method_frame:
            self.data = json.loads(body.decode('utf-8'))
            self.data.pop('_sa_instance_state', None)
            logger.info(f"Message consumed from RabbitMQ: {self.data}")
            return self.data

# Generate a random AES key and IV
def generate_aes_key_iv():
    aes_key = os.urandom(32)  # 256-bit key
    aes_iv = os.urandom(16)  # 128-bit IV
    return aes_key, aes_iv


# Encrypt message using AES
def encrypt_message_aes(message, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # Pad message to multiple of block size (16 bytes)
    padded_message = message + (16 - len(message) % 16) * chr(16 - len(message) % 16)
    encrypted_message = encryptor.update(padded_message.encode()) + encryptor.finalize()
    return encrypted_message


# Encrypt data using RSA
def encrypt_rsa(data, public_key):
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# Load private RSA key
def load_private_key():
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

# Windows client public key
def load_public_key():
    certificate_pem = get_certs(str(os.getenv("DATABASE_URL")))
    if not certificate_pem:
        raise ValueError("Can't find certificate")

    certificate = x509.load_pem_x509_certificate(certificate_pem.encode('utf-8'))
    public_key = certificate.public_key()

    """with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )"""
    print(f"PUBLIC KEY:{str(public_key)}")
    return public_key

# Decrypt AES key and IV using RSA
def decrypt_rsa(encrypted_data, private_key):
    return private_key.decrypt(
        encrypted_data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

# Decrypt AES-encrypted message
def decrypt_message(encrypted_message, key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return decrypted_message.decode('utf-8').strip()

def main():
    #parser = argparse.ArgumentParser(description="Script that get rabbitMQ messages and sent to AD Connector")
    #parser.add_argument("host", type=str, help="tcp://host:port")
    #args = parser.parse_args()

    # RabbitMq Reader
    rabbit_reader = RabbitMQReader(queue_name="AD", host="localhost")
    rabbit_reader.connect()

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ str(os.getenv("ZERO_MQ_URL")))
    logger.info("Client is running and sending JSON messages...")

    """
    data = {
        "action": "notify",
        "hostname": "server01.example.com",
        "user": "test_user",
        "timezone": "UTC-03:00",
        "allowed_schedule": {
            "sunday": [{"start": 0, "end": 0}],
            "monday": [{"start": 0, "end": 0}],
            "tuesday": [{"start": 540, "end": 1080}],
            "wednesday": [{"start": 540, "end": 1080}],
            "thursday": [{"start": 540, "end": 1080}],
            "friday": [{"start": 540, "end": 1080}],
            "saturday": [{"start": 540, "end": 1080}]
        },
        "timestamp": "2024-11-21T15:30:00Z",
        "message": "Scheduled maintenance will occur this weekend.",
        "title": "System Notification",
        "options": "Dismiss, Snooze"
    }
    
    """
    #get_certs(os.getenv("DATABASE_URL"))
    #load_public_key()

    print("Starting to read RabbitMQ messages...")
    while True:
        data = rabbit_reader.consume_message()
        if data:
            if data.get('status') == 'error' and data.get('message') == 'Action not found':
                print("RabbitMQ message with no processable json")
            else:
                try:
                    message=process_message(data)
                    try:
                        message=json.dumps(data)
                        request = process_request(message)
                        socket.send_string(request)
                        response = socket.recv_string()
                        process_response(response)
                    except Exception as e :
                        logger.error(f"ZmqServer - Can't process Zmq message, because error: {e} ")
                        continue
                except Exception as e:
                    logger.error("ZmqServer- Can't process rabbitMQ data")
                    continue

def process_message(message):
    processed_message = None
    try:
        action = "ad_update"
        allowed_work_hours = message.get("allowed_work_hours")
        user = message.get("uid")
        timezone = str(datetime.datetime.now().astimezone().tzinfo)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        processed_message = {"user": user, "action":action, "allowed_work_hours": allowed_work_hours, "timezone": timezone, "timestamp": timestamp}
    except Exception as e:
        logger.error("Error to process message to AD")
        return processed_message

def process_request(request):
    public_key = load_public_key()

    aes_key, aes_iv = generate_aes_key_iv()
    encrypted_message = encrypt_message_aes(request, aes_key, aes_iv)

    encrypted_aes_key = encrypt_rsa(aes_key, public_key)
    encrypted_aes_iv = encrypt_rsa(aes_iv, public_key)

    # Construct the payload
    payload = {
        "EncryptedAESKey": base64.b64encode(encrypted_aes_key).decode(),
        "EncryptedAESIV": base64.b64encode(encrypted_aes_iv).decode(),
        "EncryptedMessage": base64.b64encode(encrypted_message).decode()
    }
    request = json.dumps(payload, indent=4)
    print(request)
    return request


def process_response(response):
    # Load private RSA key for decrypting AES key and IV
    private_key = load_private_key()

    data = json.loads(response)
    logger.info("\nResponse JSON message:\n", json.dumps(data, indent=4))

    encrypted_message = base64.b64decode(data["EncryptedMessage"])

    decrypted_aes_key = decrypt_rsa(base64.b64decode(data["EncryptedAESKey"]), private_key)
    decrypted_aes_iv = decrypt_rsa(base64.b64decode(data["EncryptedAESIV"]), private_key)
    decrypted_message = decrypt_message(encrypted_message, decrypted_aes_key, decrypted_aes_iv)

    decrypted_response = {
        "DecryptedAESKey": base64.b64encode(decrypted_aes_key).decode(),
        "DecryptedAESIV": base64.b64encode(decrypted_aes_iv).decode(),
        "DecryptedMessage": decrypted_message
    }

    logger.info("\nDecrypted JSON response:\n", json.dumps(decrypted_response, indent=4))

def get_certs(database_url:str ):
    """
    Faz um SELECT * em todos os registros de uma tabela no PostgreSQL.

    Args:
        connection_params (dict): Parâmetros de conexão com o banco (host, dbname, user, password).
        table_name (str): Nome da tabela no banco de dados.

    Returns:
        List[dict]: Lista de registros como dicionários.
    """
    try:
        table_name = "certificate_authority"
        # Conectar ao banco de dados
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # Query para buscar todos os registros
        hostname = str(os.getenv("AD_HOSTNAME"))
        query = f"SELECT certificate FROM {table_name} WHERE fqdn=%s"
        cursor.execute(query, (hostname,))
        results = cursor.fetchone()
        print (f"Results: {results} ")
        result = results["certificate"]
        return result
    except psycopg2.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return []
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
