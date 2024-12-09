# Configuração Certification Authority
## WorkDay Session Management

1. **`.env`**: variáveis de inicialização que indicam caminho dos arquivos, valores de CN (nomes dos certificados) e senhas.

    ```ini
    Z_MQ_PORT=<porta onde CA escuta>
    CA_CERT_CN=<valor do campo "CN" do certificado da CA>
    WSM_CERT_CN=<valor do campo "CN" do certificado do session server>
    CA_KEY_PASSWORD=<senha para acessar private key da CA>
    CA_CERT_FILE=<caminho para arquivo ca.cert.pem>
    CA_KEY_PATH=<caminho para arquivo ca.key.pem>
    WSM_CERT_FILE=<caminho para arquivo WSM.cert.pem>
    ```

2. **`encrypt_env_file.py`**: script para criptografar valores definidos no .env. Gera dois arquivos:
    
    - **`encrypted.env`**: variáveis e valores criptografados
    - **`secret.key`**: chave para descriptografar valores descritos acima

    a. Para executá-lo:
    
        ``` bash
        source bin/activate #ativa virtualenv
        cd config
        python3 encrypt_env_file.py
        ```

3. **`config.py`**: script que realiza descriptografia do arquivo **`encrypted.env`** e permite acesso às variáveis necessárias ao serviço da CA.

    - variáveis **`encrypted_env_path`** e **`key_path`** precisam receber caminhos dos arquivos **`encrypted.env`** e **`secret.key`**, respectivamente

## Importante

1. **`EXCLUIR ARQUIVO .env APÓS APLICAÇÃO DE CRIPTOGRAFIA`**

2. **`RESTRINGIR ACESSO AOS ARQUIVOS:`**
    - **`encrypted.env`**
    - **`secret.key`**

3. Comando para tornar acesso restrito:
    
    ``` bash
    cd src/config/
    chmod 600 encrypted.env
    chmod 600 secret.key
    ```

