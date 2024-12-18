from src.logs.logger import Logger
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os, tempfile


logger_instance = Logger(log_name='app', log_dir='logs', level='INFO', retention_days=7)

logger = logger_instance.get_logger()


#load and decrypt env file
def load_encrypted_env(encrypted_file_path, key_file_path):
    try:
        #load the crypto file from file
        with open (key_file_path,'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        logger.error(f"Key file '{key_file_path}' not found.")
        raise 
    except Exception as e:
        logger.error(f"Error reading the key file: {e}") 
        raise   
    try:    
        fernet = Fernet(key)
    except Exception as e:
        logger.error(f"Error initializing Fernet with the provided key: {e}")
        raise 

    try:
        # Read and decrypt of encrypted.env content
        with open (encrypted_file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
            decrypted_data = fernet.decrypt(encrypted_data)
    except FileNotFoundError:
        logger.error(f"Encrypted file '{encrypted_file_path}' not found.")
        raise
    except Exception as e:
        logger.error(f"Error decrypting the file: {e}")
        raise 

    try:
        # Create a temporary file to hold decripted variables
        temp_env_file = tempfile.NamedTemporaryFile(delete=False)
        temp_env_file.write(decrypted_data)
        temp_env_file_path = temp_env_file.name
        temp_env_file.close()
    except Exception as e:
        logger.error(f"Error creating temporary file: {e}")
        raise 
    
    try:
        # load the variables from temporary file
        load_dotenv(temp_env_file_path)
    except Exception as e:
        logger.error(f"Error loading environment variables from temporary file: {e}")
        raise
     
    finally:
        # Remove the temporary file after loading
        if temp_env_file_path and os.path.exists(temp_env_file_path):
            try:
                os.remove(temp_env_file_path)
            except Exception as e:
                logger.error(f"Error removing temporary file: {e}")
                raise 
            # remove ini file if exists
            try:
                os.remove('.ini')
            except Exception as e:
                logger.error("INFO - NO .ini file detected")
                print("INFO - NO .ini file detected")


# Carregar as variáveis do arquivo .env
load_dotenv()


# Path of key and encrypt env

current_dir = os.path.dirname(os.path.abspath(__file__))
relative_path = os.path.join(current_dir, '../../src/config/encrypted.env')


encrypted_env_path = os.path.abspath(relative_path)
key_path = os.path.abspath(os.path.join(current_dir, '../../src/config/secret.key'))

try:
    # Configurações gerais
    DATABASE_URL = os.getenv("DEV_DATABASE_URL")
    MQ_ADDRESS_HOST = os.getenv("DEV_MQ_ADDRESS_HOST")
    MQ_HOST_PORT = os.getenv("DEV_MQ_HOST_PORT")
    WORK_HOURS_QUEUE= os.getenv("DEV_WORK_HOURS_QUEUE")
    Z_MQ_PORT= os.getenv("Z_MQ_PORT")
    CA_KEY_PASSWORD = os.getenv("CA_KEY_PASSWORD")
    CA_CERT_CN = os.getenv("CA_CERT_CN")
    CA_KEY_PATH = os.getenv("CA_KEY_PATH")
    CA_CERT_FILE = os.getenv("CA_CERT_FILE")
    WSM_CERT_FILE = os.getenv("WSM_CERT_FILE")
    WSM_CERT_CN = os.getenv("WSM_CERT_CN")

    AUDIT_QUEUE = os.getenv("AUDIT_QUEUE")
    AUDIT_QUEUE_HOST = os.getenv("AUDIT_QUEUE_HOST")


    if not DATABASE_URL:
        logger.error("A variável de ambiente DATABASE_URL não está definida.")
        raise ValueError("DATABASE_URL não definida.")

    if not Z_MQ_PORT:
        logger.error("A variável de ambiente Z_MQ_PORT não está definida.")
        raise ValueError("Z_MQ_PORT não definida.")

    if not CA_KEY_PASSWORD:
        logger.error("A variável de ambiente CA_KEY_PASSWORD não está definida.")
        raise ValueError("CA_KEY_PASSWORD não definida.")

    if not CA_KEY_PATH:
        logger.error("A variável de ambiente CA_KEY_PATH não está definida.")
        raise ValueError("CA_KEY_PATH não definida.")

    if not CA_CERT_FILE:
        logger.error("A variável de ambiente CA_CERT_FILE não está definida.")
        raise ValueError("CA_CERT_FILE não definida.")

    if not WSM_CERT_FILE:
        logger.error("A variável de ambiente WSM_CERT_FILE não está definida.")
        raise ValueError("WSM_CERT_FILE não definida.")

    if not WSM_CERT_CN:
        logger.error("A variável de ambiente WSM_CERT_CN não está definida.")
        raise ValueError("WSM_CERT_CN não definida.")

    if not CA_CERT_CN:
        logger.error("A variável de ambiente CA_CERT_CN não está definida.")
        raise ValueError("CA_CERT_CN não definida.")

    logger.info("Todas as variáveis de ambiente foram carregadas com sucesso.")

except Exception as e:
    logger.error("Error loading environment variables: {e}")
    raise 

try:
    load_encrypted_env(encrypted_file_path=encrypted_env_path, key_file_path=key_path)
except Exception as e:
    logger.error(f"Error loading encrypted configuration file: {e}")
    raise









