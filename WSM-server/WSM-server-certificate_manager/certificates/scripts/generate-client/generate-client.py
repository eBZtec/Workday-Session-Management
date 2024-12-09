import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509 import NameOID
from cryptography import x509
from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone

# Load environment variables from .env
load_dotenv()


def create_client_certificate(output_dir):
    # Load CA private key and certificate
    with open(os.getenv("CA_PRIVATE_KEY_PATH"), "rb") as f:
        ca_private_key = serialization.load_pem_private_key(
            f.read(),
            password=os.getenv("CA_PRIVATE_KEY_PASSWORD").encode('utf-8')
        )

    with open(os.getenv("CA_CERTIFICATE_PATH"), "rb") as f:
        ca_certificate = x509.load_pem_x509_certificate(f.read())

    # Get the client common name from .env
    client_common_name = os.getenv("CLIENT_COMMON_NAME")
    if not client_common_name:
        raise ValueError("CLIENT_COMMON_NAME is not set in the .env file.")

    # Generate client's private key
    client_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Serialize and save client's private key
    private_key_path = os.path.join(output_dir, f"{client_common_name}_private_key.pem")
    with open(private_key_path, "wb") as f:
        f.write(client_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # Create client's CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, os.getenv("CLIENT_COUNTRY_NAME")),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, os.getenv("CLIENT_STATE_OR_PROVINCE_NAME")),
        x509.NameAttribute(NameOID.LOCALITY_NAME, os.getenv("CLIENT_LOCALITY_NAME")),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, os.getenv("CLIENT_ORGANIZATION_NAME")),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, os.getenv("CLIENT_ORGANIZATIONAL_UNIT_NAME")),
        x509.NameAttribute(NameOID.COMMON_NAME, client_common_name),
    ])).sign(client_private_key, hashes.SHA256())

    # Serialize and save CSR
    csr_path = os.path.join(output_dir, f"{client_common_name}_csr.pem")
    with open(csr_path, "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))

    # Sign the client's CSR with the CA's private key to create the client certificate
    client_certificate = x509.CertificateBuilder() \
        .subject_name(csr.subject) \
        .issuer_name(ca_certificate.subject) \
        .public_key(csr.public_key()) \
        .serial_number(x509.random_serial_number()) \
        .not_valid_before(datetime.now(timezone.utc) + timedelta(days=int(os.getenv("CLIENT_NOT_VALID_BEFORE")))) \
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=int(os.getenv("CLIENT_NOT_VALID_AFTER")))) \
        .sign(ca_private_key, hashes.SHA256())

    # Serialize and save client certificate
    certificate_path = os.path.join(output_dir, f"{client_common_name}_certificate.pem")
    with open(certificate_path, "wb") as f:
        f.write(client_certificate.public_bytes(serialization.Encoding.PEM))

    print(f"Client '{client_common_name}' certificate, private key, and CSR have been saved in {output_dir}.")


def main():
    # Set output directory to two levels above
    output_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "client_files"))
    os.makedirs(output_directory, exist_ok=True)

    # Generate client certificate
    create_client_certificate(output_directory)


if __name__ == "__main__":
    main()
