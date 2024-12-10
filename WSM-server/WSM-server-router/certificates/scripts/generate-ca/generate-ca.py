import os
import datetime
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.x509 import NameOID
from cryptography import x509
from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone

# Load environment variables from .env
load_dotenv()


def create_ca_certificate(output_dir):
    # Generate CA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Get the password from .env
    password = os.getenv("CA_PRIVATE_KEY_PASSWORD").encode('utf-8')

    # Serialize private key to PEM format with password
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(password),
    )

    # Save private key to a file
    with open(f"{output_dir}/ca_private_key.pem", "wb") as f:
        f.write(private_key_pem)

    # Create subject and issuer (self-signed CA)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, os.getenv("CA_COUNTRY_NAME")),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, os.getenv("CA_STATE_OR_PROVINCE_NAME")),
        x509.NameAttribute(NameOID.LOCALITY_NAME, os.getenv("CA_LOCALITY_NAME")),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, os.getenv("CA_ORGANIZATION_NAME")),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, os.getenv("CA_ORGANIZATIONAL_UNIT_NAME")),
        x509.NameAttribute(NameOID.COMMON_NAME, os.getenv("CA_COMMON_NAME")),
    ])

    # Parse validity offsets from .env
    not_valid_before = datetime.now(timezone.utc) + timedelta(days=int(os.getenv("CA_NOT_VALID_BEFORE")))
    not_valid_after = datetime.now(timezone.utc) + timedelta(days=int(os.getenv("CA_NOT_VALID_AFTER")))

    # Build the CA certificate
    certificate = x509.CertificateBuilder() \
        .subject_name(subject) \
        .issuer_name(issuer) \
        .public_key(private_key.public_key()) \
        .serial_number(x509.random_serial_number()) \
        .not_valid_before(not_valid_before) \
        .not_valid_after(not_valid_after) \
        .add_extension(
        x509.BasicConstraints(ca=True, path_length=None),
        critical=True,
    ) \
        .sign(private_key, hashes.SHA256())

    # Serialize certificate to PEM format
    certificate_pem = certificate.public_bytes(serialization.Encoding.PEM)

    # Save certificate to a file
    with open(f"{output_dir}/ca_certificate.pem", "wb") as f:
        f.write(certificate_pem)

    print("CA Certificate and Password-Protected Private Key have been created!")


def main():
    # Set output directory to two levels above
    output_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "ca_files"))
    os.makedirs(output_directory, exist_ok=True)

    # Generate client certificate
    create_ca_certificate(output_directory)


if __name__ == "__main__":
    main()
