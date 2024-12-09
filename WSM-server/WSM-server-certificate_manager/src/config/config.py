from dotenv import load_dotenv
from cryptography.fernet import Fernet # type: ignore
from src.logs.logger import Logger
import os
import tempfile

# Create a Logger instace for this module
logger = Logger(log_name="Config").get_logger()


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
    
# Path of key and encrypt env
encrypted_env_path = '/root/wsm_certificate_manager/src/config/encrypted.env'
key_path = '/root/wsm_certificate_manager/src/config/secret.key'

try:
    load_encrypted_env(encrypted_file_path=encrypted_env_path, key_file_path=key_path)
except Exception as e:
    logger.error(f"Error loading encrypted configuration file: {e}")
    raise 

try:
    # Configurações gerais
    DATABASE_URL = os.getenv("DEV_DATABASE_URL")
    Z_MQ_PORT = os.getenv("Z_MQ_PORT")
    CA_KEY_PASSWORD = os.getenv("CA_KEY_PASSWORD")
    CA_CERT_CN = os.getenv("CA_CERT_CN")
    CA_KEY_PATH = os.getenv("CA_KEY_PATH")
    CA_CERT_FILE = os.getenv("CA_CERT_FILE")
    WSM_CERT_FILE = os.getenv("WSM_CERT_FILE")
    WSM_CERT_CN = os.getenv("WSM_CERT_CN")

    # Verificações para cada variável de ambiente
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


