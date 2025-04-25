import os
import json
import logging
from typing import Dict, Optional
from app.raft.fsm import Raft3DFSM
from app.raft.snapshot import SnapshotManager
from app.raft.mock_raft import MockRaft

logger = logging.getLogger("raft3d")

class RaftNode:
    def __init__(self, node_id: str, raft_port: int, raft_dir: str, cluster: str):
        self.node_id = node_id
        self.fsm = Raft3DFSM()
        self.raft_dir = raft_dir
        os.makedirs(raft_dir, exist_ok=True)

        # Initialize mock Raft
        try:
            if not cluster or "=" not in cluster:
                raise ValueError(f"Invalid CLUSTER format: {cluster}")
            # Extract peers from CLUSTER (e.g., "nodes=raft3d-node1:9090,raft3d-node2:9090,raft3d-node3:9090")
            peers_str = cluster.split("nodes=", 1)[1] if "nodes=" in cluster else cluster
            peers = [p.strip() for p in peers_str.split(",") if p.strip()]
            if not peers:
                raise ValueError("No valid peers found in CLUSTER")
            logger.info(f"Parsed peers for node {node_id}: {peers}")
        except Exception as e:
            logger.error(f"Failed to parse CLUSTER '{cluster}': {str(e)}")
            raise

        self.raft = MockRaft(node_id, peers, self.fsm, raft_dir)
        self.raft.start()

        # Start snapshot manager
        self.snapshot_manager = SnapshotManager(self.fsm, raft_dir)
        self.snapshot_manager.start()

    def apply(self, op: str, value: dict) -> bool:
        cmd = {"op": op, "value": value}
        return self.raft.apply(json.dumps(cmd).encode())

    def get_printers(self) -> Dict[str, 'Printer']:
        return self.fsm.printers

    def get_filaments(self) -> Dict[str, 'Filament']:
        return self.fsm.filaments

    def get_print_jobs(self, status: Optional[str] = None) -> Dict[str, 'PrintJob']:
        if status:
            return {k: v for k, v in self.fsm.print_jobs.items() if v.status == status}
        return self.fsm.print_jobs