import threading
import time
from datetime import datetime, timezone
from src.logs.logger import logger

class PingScheduler:
    def __init__(self, logger, db_manager, send_ping_callback, on_peer_timeout_callback, interval_seconds=1800, max_attempts=3):
        self.logger = logger
        self.db_manager = db_manager  # usado para buscar hostnames ativos
        self.send_ping_callback = send_ping_callback
        self.on_peer_timeout_callback = on_peer_timeout_callback
        self.interval = interval_seconds
        self.max_attempts = max_attempts

        self._running = False
        self._attempts = {}  # hostname -> número de tentativas pendentes
        self._lock = threading.Lock()

    def start(self):
        self._running = True
        threading.Thread(target=self._ping_loop, daemon=True).start()

    def stop(self):
        self._running = False

    def receive_pong(self, hostname):
        with self._lock:
            self._attempts.pop(hostname, None)

    def has_received_pong(self, hostname):
        with self._lock:
            return hostname not in self._attempts

    def _ping_loop(self):
        while self._running:
            time.sleep(self.interval)
            self.logger.info("[PING] Iniciando varredura de hostnames ativos no banco...")

            try:
                active_hostnames = self.db_manager.get_active_hostnames()
            except Exception as e:
                self.logger.error(f"[PING] Erro ao buscar sessões ativas: {e}")
                continue

            now = datetime.now(timezone.utc)

            with self._lock:
                for hostname in active_hostnames:
                    attempts = self._attempts.get(hostname, 0)

                    if attempts >= self.max_attempts:
                        self.logger.warning(f"[PING FAIL] {hostname} excedeu {self.max_attempts} tentativas — executando limpeza.")
                        self.on_peer_timeout_callback(hostname)
                        self._attempts.pop(hostname, None)
                        continue

                    self.logger.info(f"[PING] Enviando ping para {hostname} (tentativa {attempts + 1})")
                    self.send_ping_callback(hostname)
                    self._attempts[hostname] = attempts + 1
