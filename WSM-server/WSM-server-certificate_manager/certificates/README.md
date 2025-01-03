# Basic configuration

## Activate virtualenv from `wsm_certificate_manager` directory

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## How to generate CA and clients

### Defining CA certificate parameters in *.env* file:

1. Create a file named *.env* in ``scripts/generate_ca/``
2. Place the content:

    ```
    # CA Certificate Information
    CA_COUNTRY_NAME=BR
    CA_STATE_OR_PROVINCE_NAME=SP
    CA_LOCALITY_NAME=Locality
    CA_ORGANIZATION_NAME=Organization
    CA_ORGANIZATIONAL_UNIT_NAME=Workday Session Management Certification Authority
    CA_COMMON_NAME=WSM-CA

    # CA Certificate Validity (in days)
    CA_NOT_VALID_BEFORE=0
    CA_NOT_VALID_AFTER=3650

    # Password for CA Private Key
    CA_PRIVATE_KEY_PASSWORD=<password_goes_here>
    ```

3. Replace `CA_PRIVATE_KEY_PASSWORD` value. This password will be required for clients to get their signed certificates.

### Create Certification Authority

1. From the `certificates` folder and with the virtualenv activated, run:
```bash
python3 scripts/generate-ca/generate-ca.py
```
2. Files generated will be stored in `certificates/ca_files`


### Defining client certificate parameters in *.env* file:
1. Create a file named *.env* in ``scripts/generate_client/``
2. Place the content:

    ```
    # CA Paths
    CA_PRIVATE_KEY_PATH=ca_files/ca_private_key.pem
    CA_CERTIFICATE_PATH=ca_files/ca_certificate.pem
    CA_PRIVATE_KEY_PASSWORD=<password defined in CA creation>

    # Client Certificate Information
    CLIENT_COUNTRY_NAME=BR
    CLIENT_STATE_OR_PROVINCE_NAME=SP
    CLIENT_LOCALITY_NAME=Locality
    CLIENT_ORGANIZATION_NAME=Organization
    CLIENT_ORGANIZATIONAL_UNIT_NAME=Workday Session Management
    CLIENT_COMMON_NAME=WSM-SESSION-SERVER

    # Validity Period for the Client Certificate
    CLIENT_NOT_VALID_BEFORE=0  # Days offset from now
    CLIENT_NOT_VALID_AFTER=365  # Days offset from now
    ```

3. Replace `CA_PRIVATE_KEY_PASSWORD` value by the one previously configured.

### Create a client

1. From the directory `certificates` and with the virtualenv activated, run:
```bash
python3 scripts/generate-client/generate-client.py
```
2. Files generated will be stored in `certificates/client_files`

## Protecting sensitive information

1. **Set restricted permissions to `ca_private_key.pem` file with command:**

```bash
chmod 600 ca_private_key.pem
```
2. **Remove client's `_private_key.pem` file from the directory after copping it to *wsm-session-server* project folder**.
