from src.models.schema.request_models import *
from src.services.simple_route_server_service import FlexibleRouterServerService


def main():
   server = FlexibleRouterServerService()

   try:
      server.start()
   except KeyboardInterrupt:
      server.stop() 

if __name__ == "__main__":
   main()
