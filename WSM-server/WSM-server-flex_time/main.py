from src.config.wsm_logger import wsm_logger

def init_infra():
    wsm_logger.info("Starting connection with WSM Queue Manager...")
    from src.infra.wsm_queue_manager import wsm_queue_manager
    wsm_logger.info("WSM Queue manager connected successfully.")

    wsm_logger.info("Starting connection with WSM Session Database...")
    from src.infra.wsm_session_database import wsm_session_database
    wsm_logger.info("WSM Session Database connected successfully.")

    wsm_logger.info("Starting connection with WSM ZeroMQ Connection...")
    from src.infra.wsm_session_database import wsm_session_database
    wsm_logger.info("WSM ZeroMQ connected successfully.")

if __name__ == "__main__":
    wsm_logger.info("Starting WSM Server Flex Time Server...")
    init_infra()
    wsm_logger.info("Finished WSM Server Flex Time Server...")
