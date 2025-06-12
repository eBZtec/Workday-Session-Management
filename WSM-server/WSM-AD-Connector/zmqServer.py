import os
import zmq
import json
import base64
import pika
import datetime
import logging
import sys

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


load_dotenv()

LOG_NAME = os.getenv("LOG_NAME", "wsm_logger")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "[%(asctime)s] [%(levelname)s] %(message)s")
LOG_DESTINATION = os.getenv("LOG_DESTINATION", "both").lower()

# Cria o logger
logger = logging.getLogger(LOG_NAME)
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# Evita duplicar handlers
if not logger.handlers:
    formatter = logging.Formatter(LOG_FORMAT)

    if LOG_DESTINATION in ("file", "both"):
        LOG_DIR = os.getenv("LOG_DIR", "./logs")
        LOG_FILENAME = os.getenv("LOG_FILENAME", "wsm.log")
        LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 1048576))
        LOG_BKP_COUNT = int(os.getenv("LOG_BKP_COUNT", 5))

        os.makedirs(LOG_DIR, exist_ok=True)
        file_path = os.path.join(LOG_DIR, LOG_FILENAME)
        file_handler = TimedRotatingFileHandler(
            file_path,
            when='D',
            interval=7,
            backupCount=LOG_BKP_COUNT
        )
        file_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if LOG_DESTINATION in ("journal", "both"):
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)


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

    def start_consuming(self, callback):
        """
        Basic consume make it blocked until a message comes to
        """
        self.channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        self.channel.start_consuming()

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
    with open(str(os.getenv("PRIVATE_KEY_LOCATION")), "rb") as key_file:
    #with open("private_key.pem", "rb") as key_file:
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
    #print(f"PUBLIC KEY:{str(public_key)}")
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

    # RabbitMq Reader
    rabbit_reader = RabbitMQReader(queue_name="AD", host="localhost")
    rabbit_reader.connect()

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://"+ str(os.getenv("ZERO_MQ_URL")))
    logger.info("Client is running and sending JSON messages...")



    def process_rabbit_message(ch, method, properties, body):
        """
        Callback to process RabbitMQ messages.
        This function is called automatically to each message that comes in to queue Rabbit
        """
        try:
            data = json.loads(body.decode('utf-8'))
            logger.info(f"Message consumed from RabbitMQ: {data}")

            if data.get('status') == 'error' and data.get('message') == 'Action not found':
                logger.warning("RabbitMQ message with no processable JSON")
                return

            message = process_message(data)
            if message:
                try:
                    message_json = json.dumps(message)
                    request = process_request(message_json)
                    socket.send_string(request)
                    response = socket.recv_string()
                    process_response(response)
                except Exception as e:
                    logger.error(f"Error processing ZeroMQ message: {e}")
        except Exception as e:
            logger.error(f"Error processing RabbitMQ message: {e}")

    logger.info("Starting to read RabbitMQ messages...")
    rabbit_reader.start_consuming(process_rabbit_message)

def process_message(message):
    processed_message = None
    try:
        action = "ad_update"
        user = message.get("uid")

        allowed_work_hours = None
        enable = None
        unlock = None

        if "logon_hours" in message:
            allowed_work_hours = message.get("logon_hours")

        if "account_status" in message:
            enable = message.get("account_status")

        if "account_unlock" in message:
            unlock = message.get("account_unlock")

        timezone = str(datetime.datetime.now().astimezone().tzinfo)
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        processed_message = {
            "uid": user,
            "action": action,
            "allowed_work_hours": allowed_work_hours,
            "timezone": timezone,
            "timestamp": timestamp,
            "enable": enable,
            "unlock": unlock
        }
        logger.info(f"Message defined as {processed_message}")
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
    return request


def process_response(response):
    # Load private RSA key for decrypting AES key and IV
    private_key = load_private_key()

    data = json.loads(response)
    logger.info("Response JSON message: " + json.dumps(data, indent=4))

    encrypted_message = base64.b64decode(data["EncryptedMessage"])

    decrypted_aes_key = decrypt_rsa(base64.b64decode(data["EncryptedAESKey"]), private_key)
    decrypted_aes_iv = decrypt_rsa(base64.b64decode(data["EncryptedAESIV"]), private_key)
    decrypted_message = decrypt_message(encrypted_message, decrypted_aes_key, decrypted_aes_iv)

    decrypted_response = {
        "DecryptedAESKey": base64.b64encode(decrypted_aes_key).decode(),
        "DecryptedAESIV": base64.b64encode(decrypted_aes_iv).decode(),
        "DecryptedMessage": decrypted_message
    }

    logger.info("Decrypted JSON response:" + json.dumps(decrypted_response, indent=4))

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
        logger.info("Starting process to get Active Directory agent certificate")
        table_name = "certificate_authority"
        # Conectar ao banco de dados
        connection = psycopg2.connect(database_url)
        cursor = connection.cursor(cursor_factory=RealDictCursor)

        # Query para buscar todos os registros
        hostname = str(os.getenv("AD_HOSTNAME"))
        logger.debug(f"Active directory FQDN defined as \"{hostname}\"")
        query = f"SELECT certificate FROM {table_name} WHERE fqdn=%s"
        cursor.execute(query, (hostname,))
        results = cursor.fetchone()
        logger.debug(f"Results found \"{results} for FQDN \"{hostname}\"")
        result = results["certificate"]
        return result
    except psycopg2.Error as e:
        logger.error(f"Erro ao acessar o banco de dados: {e}")
        return []
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
