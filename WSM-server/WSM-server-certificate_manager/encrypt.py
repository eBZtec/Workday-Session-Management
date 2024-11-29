from cryptography.fernet import Fernet

key = Fernet.generate_key()

with open('secret.key', 'wb') as key_file:
    key_file.write(key)

with open('.env', 'rb') as file:
    file_data = file.read()

fernet = Fernet(key)
encrypted_data = fernet.encrypt(file_data)

with open('encrypted.env', 'wb') as encrypted_file:
    encrypted_file.write(encrypted_data)