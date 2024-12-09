import os, json
from logging.handlers import TimedRotatingFileHandler
from cryptography import x509
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from src.connections.database_manager import DatabaseManager
from src.logs.logger import Logger


class CryptoMessages:

    def __init__(self):
        self.dm = DatabaseManager()
        self.logger = Logger().get_logger()

    # Generate a random AES key and IV
    def generate_aes_key_iv(self):
        aes_key = os.urandom(32)  # 256-bit key
        aes_iv = os.urandom(16)  # 128-bit IV
        return aes_key, aes_iv


    # Encrypt message using AES
    def encrypt_message_aes(self,message, key, iv):
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()

        message = json.dumps(message)

        # Pad message to multiple of block size (16 bytes)
        padded_message = message + (16 - len(message) % 16) * chr(16 - len(message) % 16)
        encrypted_message = encryptor.update(padded_message.encode()) + encryptor.finalize()
        return encrypted_message

    # Encrypt data using RSA
    def encrypt_rsa(self,data, public_key):
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    # Load private RSA key
    def load_private_key(self):
        with open("/root/wsm_certificate_manager/certificates/client_files/WSM-SESSION-SERVER_private_key.pem", "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        '''
        # Serialize the private key to PEM format as bytes
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()  # No password protection
        )

        # Convert bytes to string
        private_key_str = private_key_pem.decode("utf-8")
        print(private_key_str)  # Print the private key as a string
        '''

        return private_key


    # Windows client public key
    def load_public_key(self,_hostname):
        row = self.dm.get_cert_by_hostname("wsm:"+_hostname.lower())
        certificate_data = row[0].encode("utf-8")

        # Parse the certificate
        certificate = x509.load_pem_x509_certificate(certificate_data)

        # Extract the public key
        public_key = certificate.public_key()

        # Serialize the public key to PEM format
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Print the public key
        print(public_key_pem.decode("utf-8"))

        """
        with open("public_key.pem", "rb") as key_file:
            public_key = serialization.load_pem_public_key(
                key_file.read(),
                backend=default_backend()
            )
        """
        return public_key

    # Decrypt AES key and IV using RSA
    def decrypt_rsa(self,encrypted_data, private_key):
        return private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    # Decrypt AES-encrypted message
    def decrypt_message(self,encrypted_message, key, iv):
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
        return decrypted_message.decode('utf-8').strip()
     
