import pika.exceptions

from src.config.wsm_logger import wsm_logger
from src.modules.agent.agent_updater import AgentUpdaterServer


def main():
    wsm_logger.info("Starting connection with WSM Session Database...")
    from src.infra.wsm_session_database import wsm_session_database
    wsm_logger.info("WSM Session Database connected successfully.")

    wsm_logger.info("Starting WSM Agent Updater Server for manage flex time...")
    AgentUpdaterServer.start()


if __name__ == "__main__":
    try:
        wsm_logger.info("Starting WSM Server Flex Time Server - Agent Updater module...")
        main()
        wsm_logger.info("Finished WSM Server Flex Time Server...")
    except Exception as e:
        wsm_logger.error(f"WSM Server Flex time terminated by error: {e}")
