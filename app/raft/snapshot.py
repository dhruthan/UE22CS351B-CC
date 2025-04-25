import os
import time
import threading
import logging
from app.monitoring.metrics import snapshots_total

logger = logging.getLogger("raft3d")

class SnapshotManager:
    def __init__(self, fsm, raft_dir: str, interval: int = 300):
        self.fsm = fsm
        self.raft_dir = raft_dir
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        logger.info("Snapshot manager started")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def run(self):
        while self.running:
            time.sleep(self.interval)
            self.take_snapshot()

    def take_snapshot(self):
        try:
            snapshot_data = self.fsm.snapshot()
            snapshot_path = os.path.join(self.raft_dir, f"snapshot_{int(time.time())}.snap")
            with open(snapshot_path, "wb") as f:
                f.write(snapshot_data)
            snapshots_total.inc()  # Increment snapshot counter
            logger.info(f"Snapshot saved to {snapshot_path}")
        except Exception as e:
            logger.error(f"Failed to take snapshot: {str(e)}")