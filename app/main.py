import os
import uvicorn
from fastapi import FastAPI
from app.api.handlers import router, set_raft_node
from app.raft.store import RaftNode
from app.monitoring.metrics import setup_metrics, is_leader
import logging

# Configure logging with DEBUG level
logger = logging.getLogger("raft3d")
logger.setLevel(logging.DEBUG)  # Changed from INFO to DEBUG
logger.handlers = [logging.StreamHandler()]

app = FastAPI(title="Raft3D API")
app.include_router(router, prefix="/api/v1")
setup_metrics(app)

def main():
    node_id = os.getenv("NODE_ID")
    raft_port = int(os.getenv("RAFT_PORT", "9090"))
    http_port = int(os.getenv("HTTP_PORT", "8080"))
    raft_dir = os.getenv("RAFT_DIR")
    cluster = os.getenv("CLUSTER")

    raft_node = RaftNode(node_id, raft_port, raft_dir, cluster)
    set_raft_node(raft_node)

    # Set initial leader status
    leader_status = 1 if raft_node.raft.is_leader else 0
    is_leader.labels(node_id=node_id).set(leader_status)
    logger.info(f"Set initial raft3d_is_leader for {node_id} to {leader_status}")

    logger.info(f"Starting Raft3D node {node_id} on HTTP port {http_port} and Raft port {raft_port}")
    uvicorn.run(app, host="0.0.0.0", port=http_port)

if __name__ == "__main__":
    main()