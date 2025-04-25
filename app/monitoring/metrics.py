from prometheus_client import Counter, Gauge, generate_latest
from fastapi import FastAPI, Response
import logging

logger = logging.getLogger("raft3d")

# Metrics
requests_total = Counter('raft3d_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
snapshots_total = Counter('raft3d_snapshots_total', 'Total snapshots taken')
is_leader = Gauge('raft3d_is_leader', 'Whether the node is the leader', ['node_id'])

def setup_metrics(app: FastAPI):
    logger.info("Setting up Prometheus metrics")
    @app.get("/metrics")
    async def metrics():
        logger.info("Serving metrics endpoint")
        requests_total.labels(method="GET", endpoint="/metrics").inc()
        return Response(content=generate_latest(), media_type="text/plain")