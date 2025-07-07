import zmq
from zmq.utils.monitor import parse_monitor_message
import threading

class ZMQPeerMonitor:
    def __init__(self, context, logger, socket, on_disconnect_callback):
        self.context = context
        self.logger = logger
        self.socket = socket
        self.on_disconnect_callback = on_disconnect_callback
        self.monitor_endpoint = "inproc://monitor.router"
        self.socket.monitor(self.monitor_endpoint, zmq.EVENT_ALL)

    def start(self):
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def _monitor_loop(self):
        monitor = self.context.socket(zmq.PAIR)
        monitor.connect(self.monitor_endpoint)

        while True:
            try:
                msg = monitor.recv_multipart()
                evt = parse_monitor_message(msg)

                evt_type = evt['event']
                client_id = evt.get('routing_id', b'').decode(errors='ignore')
                client_addr = evt.get('peer_address', 'unknown')

                if evt_type == zmq.EVENT_DISCONNECTED:
                    self.logger.info(f"[MONITOR] Disconnected: {client_addr}, id: {client_id}")
                    self.on_disconnect_callback(client_id)
                elif evt_type == zmq.EVENT_ACCEPTED:
                    self.logger.info(f"[MONITOR] Connection accepted from {client_addr}")
                elif evt_type == zmq.EVENT_HANDSHAKE_SUCCEEDED:
                    self.logger.info(f"[MONITOR] Handshake succeeded with: {client_addr}")
            except zmq.ContextTerminated:
                break
            except Exception as e:
                self.logger.error(f"[MONITOR] Unexpected error: {e}")