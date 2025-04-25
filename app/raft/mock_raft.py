import time
import threading
import random
import logging
import os
from typing import List, Any
from app.monitoring.metrics import is_leader

logger = logging.getLogger("raft3d")

class MockRaft:
    def __init__(self, node_id: str, peers: List[str], fsm: Any, raft_dir: str):
        self.node_id = node_id
        self.peers = peers
        self.fsm = fsm
        self.raft_dir = raft_dir
        self.is_leader = False
        self.term = 0
        self.running = False
        self.thread = None
        self.leader_file = os.path.join(raft_dir, "leader.txt")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        logger.info(f"Mock Raft node {self.node_id} started")

    def stop(self):
        self.resign_leader()
        self.running = False
        if self.thread:
            self.thread.join()
        logger.info(f"Mock Raft node {self.node_id} stopped")

    def become_leader(self):
        try:
            if os.path.exists(self.leader_file):
                with open(self.leader_file, "r") as rf:
                    current_leader = rf.read().strip()
                    if current_leader and current_leader != self.node_id:
                        logger.info(f"Node {self.node_id} cannot become leader; {current_leader} is leader")
                        return False
            with open(self.leader_file, "w") as f:
                f.write(self.node_id)
            self.term += 1
            self.is_leader = True
            is_leader.labels(node_id=self.node_id).set(1)
            logger.info(f"Node {self.node_id} elected leader for term {self.term}")
            return True
        except PermissionError as e:
            logger.error(f"Node {self.node_id} election permission error: {str(e)}")
            return False
        except IOError as e:
            logger.error(f"Node {self.node_id} election IO error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Node {self.node_id} election unexpected error: {str(e)}")
            return False

    def resign_leader(self):
        try:
            if os.path.exists(self.leader_file):
                with open(self.leader_file, "r") as f:
                    current_leader = f.read().strip()
                    if current_leader == self.node_id:
                        os.remove(self.leader_file)
                        self.is_leader = False
                        is_leader.labels(node_id=self.node_id).set(0)
                        logger.info(f"Node {self.node_id} resigned as leader")
            elif self.is_leader:
                self.is_leader = False
                is_leader.labels(node_id=self.node_id).set(0)
                logger.info(f"Node {self.node_id} resigned as leader (no leader file)")
        except PermissionError as e:
            logger.error(f"Node {self.node_id} resign permission error: {str(e)}")
        except IOError as e:
            logger.error(f"Node {self.node_id} resign IO error: {str(e)}")
        except Exception as e:
            logger.error(f"Node {self.node_id} resign unexpected error: {str(e)}")

    def run(self):
        while self.running:
            if not self.is_leader:
                # Check for stale leader file first
                try:
                    if os.path.exists(self.leader_file):
                        file_age = time.time() - os.path.getmtime(self.leader_file)
                        if file_age > 10:
                            logger.info(f"Node {self.node_id} removing stale leader file")
                            os.remove(self.leader_file)
                except PermissionError as e:
                    logger.error(f"Node {self.node_id} stale file permission error: {str(e)}")
                    time.sleep(1)
                    continue
                except IOError as e:
                    logger.error(f"Node {self.node_id} stale file IO error: {str(e)}")
                    time.sleep(1)
                    continue
                except Exception as e:
                    logger.error(f"Node {self.node_id} stale file unexpected error: {str(e)}")
                    time.sleep(1)
                    continue

                # Check if a leader exists
                try:
                    if os.path.exists(self.leader_file):
                        with open(self.leader_file, "r") as f:
                            current_leader = f.read().strip()
                            if current_leader:
                                logger.debug(f"Node {self.node_id} sees leader {current_leader}")
                                time.sleep(1)
                                continue
                except PermissionError as e:
                    logger.error(f"Node {self.node_id} leader check permission error: {str(e)}")
                    time.sleep(1)
                    continue
                except IOError as e:
                    logger.error(f"Node {self.node_id} leader check IO error: {str(e)}")
                    time.sleep(1)
                    continue
                except Exception as e:
                    logger.error(f"Node {self.node_id} leader check unexpected error: {str(e)}")
                    time.sleep(1)
                    continue

                # Attempt election
                logger.debug(f"Node {self.node_id} attempting leader election")
                if random.random() < 0.5:  # 50% chance
                    if self.become_leader():
                        time.sleep(random.uniform(5, 10))  # Lead for 5-10 seconds
                        self.resign_leader()
                else:
                    logger.debug(f"Node {self.node_id} skipped election attempt")
            time.sleep(1)

    def apply(self, log_entry: bytes) -> bool:
        result = self.fsm.apply(log_entry)
        logger.info(f"Applied log entry to FSM for node {self.node_id}, result: {result}")
        return isinstance(result, bool) and result