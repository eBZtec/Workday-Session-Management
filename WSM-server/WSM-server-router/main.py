from src.models.schema.request_models import *
from src.services.simple_route_server_service import FlexibleRouterServerService
from src.services.encripted_messages_services import CryptoMessages

def main():
   server = FlexibleRouterServerService()
   crypto = CryptoMessages()

   try:
      # crypto.load_public_key("WIN-be7ur9nv6ls")
      # crypto.load_private_key()
      
      server.start()
   except KeyboardInterrupt:
      server.stop() 
      
if __name__ == "__main__":
    main()
