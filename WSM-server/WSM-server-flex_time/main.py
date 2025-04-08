import argparse

import pika.exceptions

from src.config.wsm_logger import wsm_logger


def main():
    parser = argparse.ArgumentParser(
        description="WSM Flex time server for agent/connector update",
        usage="main.py --updater agents | main.py --updater connectors")

    parser.add_argument(
        "--updater",
        choices=["agents", "connectors"],
        default="agents",
        help="The name of updater who will be executed by the script. Updater can be \"agents\" or \"connectors\""
    )

    args = parser.parse_args()
    wsm_logger.debug(f"Executing \"{args.updater}\" updater by command arguments")

    wsm_logger.info("Starting connection with WSM Session Database...")
    from src.infra.wsm_session_database import wsm_session_database
    wsm_logger.info("WSM Session Database connected successfully.")

    if args.updater == "agents":
        wsm_logger.info("Starting connection with WSM ZeroMQ Connection...")
        from src.infra.wsm_zeromq_manager import wsm_zeromq_manager
        wsm_logger.info("WSM ZeroMQ connected successfully.")
    elif args.updater == "connectors":
        wsm_logger.info("Starting connection with WSM Queue Manager...")
        from src.infra.wsm_queue_manager import wsm_queue_manager
        wsm_logger.info("WSM Queue manager connected successfully.")



if __name__ == "__main__":
    try:
        wsm_logger.info("Starting WSM Server Flex Time Server...")
        main()
        wsm_logger.info("Finished WSM Server Flex Time Server...")
    except pika.exceptions.AMQPConnectionError as e:
        wsm_logger.error(f"WSM Server Flex could not connect to RabbitMQ server, reason: {e}")
    except Exception as e:
        wsm_logger.error(f"WSM Server Flex time terminated by error: {e}")
