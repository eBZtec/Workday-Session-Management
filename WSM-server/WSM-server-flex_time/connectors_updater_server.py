import pika.exceptions

from src.config.wsm_logger import wsm_logger
from src.modules.connectors.connectors_updater import ConnectorsUpdater


def main():
    wsm_logger.info("Starting connection with WSM Session Database...")
    from src.infra.wsm_session_database import wsm_session_database
    wsm_logger.info("WSM Session Database connected successfully.")

    wsm_logger.info("Starting connection with WSM Queue Manager...")
    from src.infra.wsm_queue_manager import wsm_queue_manager
    wsm_logger.info("WSM Queue Manager connected successfully.")
    ConnectorsUpdater.start()


if __name__ == "__main__":
    try:
        wsm_logger.info("Starting WSM Server Flex Time Server - Agent Updater module...")
        main()
        wsm_logger.info("Finished WSM Server Flex Time Server...")
    except pika.exceptions.AMQPConnectionError as e:
        wsm_logger.error(f"WSM Server Flex could not connect to RabbitMQ server, reason: {e}")
    except Exception as e:
        wsm_logger.error(f"WSM Server Flex time terminated by error: {e}")