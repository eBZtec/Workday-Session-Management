from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os, tempfile

"""
Os logs desta classe são direcionados para o stdout, pois existem configurações do logger que existem aqui.
Caso fosse utilizada a classe de log, existiria referencia circular.
"""

#load and decrypt env file
def load_encrypted_env(encrypted_file_path, key_file_path):
    try:
        #load the crypto file from file
        with open (key_file_path,'rb') as key_file:
            key = key_file.read()
    except FileNotFoundError:
        print(f"[ERROR][WSM - ROUTER Config]  Key file '{key_file_path}' not found.")
        raise 
    except Exception as e:
        print(f"[ERROR][WSM - ROUTER Config]  Error reading the key file: {e}") 
        raise   
    try:    
        fernet = Fernet(key)
    except Exception as e:
        print(f"[ERROR][WSM - ROUTER Config]  Error initializing Fernet with the provided key: {e}")
        raise 

    try:
        # Read and decrypt of encrypted.env content
        with open (encrypted_file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
            decrypted_data = fernet.decrypt(encrypted_data)
    except FileNotFoundError:
        print (f"Encrypted file '{encrypted_file_path}' not found.")
        raise
    except Exception as e:
        print(f"[ERROR][WSM - ROUTER Config]  Error decrypting the file: {e}")
        raise 

    try:
        # Create a temporary file to hold decripted variables
        temp_env_file = tempfile.NamedTemporaryFile(delete=False)
        temp_env_file.write(decrypted_data)
        temp_env_file_path = temp_env_file.name
        temp_env_file.close()
    except Exception as e:
        print(f"[ERROR][WSM - ROUTER Config] Error creating temporary file: {e}")
        raise 
    
    try:
        # Load the variables from the temporary file
        load_dotenv(temp_env_file_path)
    except Exception as e:
        print(f"[ERROR][WSM - ROUTER Config] Error loading environment variables from temporary file: {e}")
        raise
    finally:
        # Remove the temporary file after loading
        if temp_env_file_path and os.path.exists(temp_env_file_path):
            try:
                os.remove(temp_env_file_path)
                print(f"[INFO][WSM - ROUTER Config] Temporary file {temp_env_file_path} removed successfully.")
            except Exception as e:
                print(f"[ERROR][WSM - ROUTER Config]  Error removing temporary file {temp_env_file_path}: {e}")
                raise

        # Remove ini file if it exists
        ini_file_path = '.ini'
        if os.path.exists(ini_file_path):
            try:
                os.remove(ini_file_path)
                print(f"[INFO][WSM - ROUTER Config] Successfully removed {ini_file_path}.")
            except Exception as e:
                print (f"[ERROR][WSM - ROUTER Config] Error removing {ini_file_path}: {e}")
                raise
        else:
            print(f"[INFO][WSM - ROUTER Config] No {ini_file_path} file detected. Skipping removal.")


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
    DATABASE_URL_AUDIT = os.getenv("DEV_DATABASE_URL_AUDIT")
    MQ_ADDRESS_HOST = os.getenv("DEV_MQ_ADDRESS_HOST")
    MQ_HOST_PORT = os.getenv("DEV_MQ_HOST_PORT")
    WORK_HOURS_QUEUE= os.getenv("DEV_WORK_HOURS_QUEUE")
    Z_MQ_PORT= os.getenv("Z_MQ_PORT")
    CA_KEY_PASSWORD = os.getenv("CA_KEY_PASSWORD")
    CA_CERT_CN = os.getenv("CA_CERT_CN")
    CA_KEY_PATH = os.getenv("CA_KEY_PATH")
    CA_CERT_FILE = os.getenv("CA_CERT_FILE")
    WSM_CERT_FILE = os.getenv("WSM_CERT_FILE")
    WSM_CERT_PRIVATE_KEY = os.getenv("WSM_CERT_PRIVATE_KEY")
    WSM_CERT_CN = os.getenv("WSM_CERT_CN")

    AUDIT_QUEUE = os.getenv("AUDIT_QUEUE")
    AUDIT_QUEUE_HOST = os.getenv("AUDIT_QUEUE_HOST")

    #Session cleanup
    CLEANUP_THRESHOLD_MINUTES=os.getenv("CLEANUP_THRESHOLD_MINUTES")
    CLEANUP_INTERVAL_MINUTES=os.getenv("CLEANUP_INTERVAL_MINUTES")


    #Logging configuration
    LOG_FILE = os.getenv("WSM_LOG_PATH")
    LOG_NAME = os.getenv("LOG_NAME")
    LOG_LOGGER = "WSM Logger"
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES"))
    LOG_BACKUP_COUNT = os.getenv("LOG_BKP_COUNT")
    LOG_DIR=os.getenv("LOG_DIR")
    LOG_FORMAT=os.getenv("LOG_FORMAT")
    LOG_FILENAME=os.getenv("LOG_FILENAME")
    LOG_LEVEL=os.getenv("LOG_LEVEL")
    LOG_DESTINATION=os.getenv("LOG_DESTINATION")

    if not DATABASE_URL:
        print ("[ERROR][WSM - ROUTER Config]  A variável de ambiente DATABASE_URL não está definida.")
        raise ValueError("DATABASE_URL não definida.")

    if not Z_MQ_PORT:
        print("[ERROR][WSM - ROUTER Config]  A variável de ambiente Z_MQ_PORT não está definida.")
        raise ValueError("Z_MQ_PORT não definida.")

    if not CA_KEY_PASSWORD:
        print("[ERROR][WSM - ROUTER Config]  A variável de ambiente CA_KEY_PASSWORD não está definida.")
        raise ValueError("CA_KEY_PASSWORD não definida.")

    if not CA_KEY_PATH:
        print("[ERROR][WSM - ROUTER Config]  A variável de ambiente CA_KEY_PATH não está definida.")
        raise ValueError("CA_KEY_PATH não definida.")

    if not CA_CERT_FILE:
        print("[ERROR][WSM - ROUTER Config]  A variável de ambiente CA_CERT_FILE não está definida.")
        raise ValueError("CA_CERT_FILE não definida.")

    if not WSM_CERT_FILE:
        print("[ERROR][WSM - ROUTER Config]  A variável de ambiente WSM_CERT_FILE não está definida.")
        raise ValueError("WSM_CERT_FILE não definida.")

    if not WSM_CERT_PRIVATE_KEY:
        print("[ERROR][WSM - ROUTER Config]  A variável de ambiente WSM_CERT_PRIVATE_KEY não está definida.")
        raise ValueError("WSM_CERT_PRIVATE_KEY não definida.")

    if not WSM_CERT_CN:
        print("[ERROR][WSM - ROUTER Config]  A variável de ambiente WSM_CERT_CN não está definida.")
        raise ValueError("WSM_CERT_CN não definida.")

    if not CA_CERT_CN:
        print("[ERROR][WSM - ROUTER Config] A variável de ambiente CA_CERT_CN não está definida.")
        raise ValueError("CA_CERT_CN não definida.")

    print("[INFO][WSM - ROUTER Config] Todas as variáveis de ambiente foram carregadas com sucesso.")

except Exception as e:
    print("[ERROR][WSM - ROUTER Config] Error loading environment variables: {e}")
    raise 

try:
    load_encrypted_env(encrypted_file_path=encrypted_env_path, key_file_path=key_path)
except Exception as e:
    print(f"[ERROR][WSM - ROUTER Config] Error loading encrypted configuration file: {e}")
    raise