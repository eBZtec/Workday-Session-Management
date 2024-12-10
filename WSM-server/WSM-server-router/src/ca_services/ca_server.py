from src.models.schema.request_models import *
from src.models.models import Certificate_Authority
from src.connections.database_manager import DatabaseManager
from src.logs.logger import Logger
from configparser import ConfigParser
from src.config import config
import zmq, json, logging, datetime, os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key


class Server():
   
   def __init__(self):
      self.logger = Logger(log_name=self.__class__.__name__).get_logger()
      self.database_url = config.DATABASE_URL
      self.zmq_port = config.Z_MQ_PORT
      self.db = DatabaseManager()

      with open(config.WSM_CERT_FILE, "rb") as cert_file:
         certificate_data = cert_file.read()
         self.parseCertificateAndInsert(certificate_data)
         self.logger.info("Session server certificate updated in database.")

      with open(config.CA_CERT_FILE, "rb") as cert_file:
         certificate_data = cert_file.read()
         self.parseCertificateAndInsert(certificate_data)
         self.logger.info("Certification authority certificate updated in database.")

   def load_server_certificate(self):
        """! Loads the server certificate from database.
        @return  server certificate.
        """
        return self.db.get_cert_by_fqdn(Certificate_Authority,config.WSM_CERT_CN).certificate

   def load_user_certificate(self, username):
      """! Loads a user's certificate from database by his Windows username.
      @param username   The Windows username to search in database.
      @return  The Windows user certificate.
      """
      return self.db.get_cert_by_fqdn(Certificate_Authority,username).certificate

   def load_ca_certificate(self, args=[]):
      """! Loads the CA certificate from database.
      @param args Optional argument. If 'pem' returns in PEM format, otherwise, returns raw certificate.
      @return The certification authority certificate in the specified format or None if not found.
      @exception Logs an info message if the CA certificate was not found or another exception occurs. 
      """
      try:
         CA_WSM = self.db.get_cert_by_fqdn(Certificate_Authority,config.CA_CERT_CN).certificate
         if args == 'pem':
               return x509.load_pem_x509_certificate(CA_WSM.encode(), backend=default_backend())
         else:
               return CA_WSM
      except Exception as e:
         self.logger.info(f"CA certificate not found: {e}")
         return None

   def load_ca_private_key(self):
      """! Loads from file the certification authority private key
      @return The CA private key.
      """
      self.logger.info(config.CA_KEY_PATH)
      with open(config.CA_KEY_PATH, "rb") as key_file:
         ca_private_key = load_pem_private_key(
               key_file.read(),
               password=config.CA_KEY_PASSWORD.encode(),
               backend=default_backend())
      return ca_private_key

   def sign_csr(self, csr_str):
      """! Sign the received CSR with CA certificate and CA private key.
      @param csr_str Certification signing request from windows user.
      @return Certificate public bytes.
      @exception Logs an info message if the CSR is invalid. 
      """
      try:
         csr = x509.load_pem_x509_csr(csr_str.encode(), default_backend())
      except Exception as e:
         self.logger.info(f"Received an invalid CSR: {e}")
         return None

      builder = x509.CertificateBuilder().subject_name(
         csr.subject
      ).issuer_name(
         self.load_ca_certificate('pem').subject
      ).public_key(
         csr.public_key()
      ).serial_number(
         x509.random_serial_number()
      ).not_valid_before(
         datetime.datetime.now(datetime.timezone.utc)
      ).not_valid_after(
         datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)  # 1 year validity
      )
      certificate = builder.sign(
         private_key=self.load_ca_private_key(),
         algorithm=hashes.SHA256(),
         backend=default_backend()
      )
      self.logger.info(f"{csr.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value} certificate successfully signed")
      return certificate.public_bytes(serialization.Encoding.PEM)

   def parseCertificateAndInsert(self, cert_data):
      """! Parse the certificate and insert in database. If FQDN already exists, update database with new value, otherwise, insert new row.
      @param cert_data Certificate public bytes for parsing an insertion in database.
      @return Certificate raw data.
      @exception Logs an info message if insertion goes wrong or another exception occurs.  
      """
      cert_load_data = x509.load_pem_x509_certificate(cert_data)
      certificate_authority = Certificate_Authority(
          fqdn = cert_load_data.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value,
          certificate = cert_data.decode(),
          validity = cert_load_data.not_valid_after_utc.date()
      )

      try:
         exists_cert = self.db.get_cert_by_fqdn(Certificate_Authority,certificate_authority.fqdn)
         if exists_cert:
            payload = {"fqdn":cert_load_data.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value,
                       "certificate":cert_data.decode(),
                       "validity": cert_load_data.not_valid_after_utc.date()
                       }
            self.db.update_entry(Certificate_Authority,exists_cert.id,payload)
         else:
            self.db.add_entry(certificate_authority)
         
         return cert_data.decode()

      except Exception as e:
         self.logger.error(f"An error occurred while inserting certificate in postgres: {e}")

   def processRequests(self, request, client_id):
      """! Processes certificate-related requests.
      @param request JSON object containing the request details. The request must include an 'action' key and may include additional data.
      @return JSON string containing the result of the request. The JSON includes a 'status' key ()'success' or 'error') and additional data.
      @exception Logs an info message and returns an error as JSON if an exception occurs during processing or if an unknown action is specified.
      """
      
      def handle_request_ca_certificate():
         try:
               data = self.load_ca_certificate()
               self.logger.info(f"CA certificate requested")
               return json.dumps({
                  "status": "success",
                  "data": data
               })
         except Exception as e:
               return json.dumps({
                  "status": "error",
                  "message": f"CA certificate not found in database: {e}"
               })

      def handle_request_server_certificate():
         try:
               data = self.load_server_certificate()
               self.logger.info(f"Session server certificate requested")

               return json.dumps({
                  "status": "success",
                  "data": data
               })
         except Exception as e:
               return json.dumps({
                  "status": "error",
                  "message": "Session server not found in database"
               })

      def handle_request_user_certificate():
         try:
               certificate = self.load_user_certificate(client_id)
               self.logger.info(f"{client_id} certificate requested by connector")
               return json.dumps({
                  "status": "success",
                  "data": certificate
               })
         except Exception as e:
               return json.dumps({
                  "status": "error",
                  "message": "User certificate not found in database"
               })

      def handle_request_signed_certificate():
         try:
               signed_cert = self.sign_csr(request['csr'])
               cert_string = self.parseCertificateAndInsert(signed_cert)

               print (json.dumps({
                  "status": "success",
                  "data": cert_string
               }))

               return json.dumps({
                  "status": "success",
                  "data": cert_string
               })
         except Exception as e:
               self.logger.error(f"Cant response signed certificate: {e}")
               return json.dumps({
                  "status": "error",
                  "message": "Invalid CSR: it's not possible to get signed certificate"
               })

      action_map = {
         'REQUEST_CA_CERTIFICATE': handle_request_ca_certificate,
         'REQUEST_SERVER_CERTIFICATE': handle_request_server_certificate,
         'REQUEST_USER_CERTIFICATE': handle_request_user_certificate,
         'REQUEST_SIGNED_CERTIFICATE': handle_request_signed_certificate
      }
      try:
         action = request.get('action')
         if action in action_map:
               return action_map[action]()
         else:
               raise Exception("Action not found")
      except Exception as e:
         return json.dumps({
               "status": "error",
               "message": str(e)
         })

   def zmqClient(self):
      context = zmq.Context()
      socket = context.socket(zmq.REP)
      port = config.Z_MQ_PORT
      socket.bind(f"tcp://*:{port}")
      self.logger.info(f"ZeroMQ initiated on port {port}")
      
      while True:
         try:
               message = socket.recv()
               self.logger.info(str(message))
               if isinstance(json.loads(message), dict):
                  response = self.processRequests(json.loads(message))
               else:
                  response = json.dumps({"status":"success","message":message})
               socket.send_string(response)

         except Exception as e:
               logging.info(f"An error occurred: {e}")
               try:
                  socket.send_string(json.dumps({"status":"erro","message":{e}}))
               except zmq.erro.ZMQerro as send_erro:
                  logging.info(f"Failed to send error response: {send_erro}")