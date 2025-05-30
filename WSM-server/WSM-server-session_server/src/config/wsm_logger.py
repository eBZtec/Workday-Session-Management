import os
import logging
import logging.handlers 
from src.config import config

try:
    from systemd.journal import JournalHandler
    HAS_JOURNAL = True
except:
    HAS_JOURNAL = False

# Log path
cwd = os.path.dirname(os.path.abspath(__file__))
log_file = config.LOG_FILE

# Main logger
logger = logging.getLogger(config.LOG_LOGGER)
logger.setLevel(config.LOG_LEVEL)

# Log rotate handler
log_handle = logging.handlers.RotatingFileHandler(
    log_file,
    maxBytes=config.LOG_MAX_BYTES,
    backupCount=config.LOG_BACKUP_COUNT
)
log_handle.setLevel(config.LOG_LEVEL)
log_format = logging.Formatter('%(asctime)s - %(levelname)s - Work Session Management - %(message)s')
log_handle.setFormatter(log_format)
logger.addHandler(log_handle)

# Optional handler to journalctl
if HAS_JOURNAL:
    journal_handler = JournalHandler()
    journal_handler.setLevel(config.LOG_LEVEL)
    journal_formatter = logging.Formatter('%(levelname)s - Work Session Management - %(message)s')
    journal_handler.setFormatter(journal_formatter)
    logger.addHandler(journal_handler)
else:
    logger.warning("systemd.journal.JournalHandler not available. Log to journalctl deactivated.")
