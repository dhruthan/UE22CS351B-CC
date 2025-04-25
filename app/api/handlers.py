from fastapi import APIRouter, HTTPException, Depends
from app.models.printer import Printer, Filament
from app.models.printjob import PrintJob
from app.raft.store import RaftNode
from typing import List, Optional
import logging

logger = logging.getLogger("raft3d")
router = APIRouter()

# Store RaftNode globally (set in main.py)
_raft_node: Optional[RaftNode] = None

def set_raft_node(node: RaftNode):
    global _raft_node
    _raft_node = node

def get_raft_node() -> RaftNode:
    if _raft_node is None:
        raise HTTPException(status_code=500, detail="RaftNode not initialized")
    return _raft_node

@router.post("/printers")
async def create_printer(printer: Printer, raft_node: RaftNode = Depends(get_raft_node)):
    if printer.id in raft_node.get_printers():
        raise HTTPException(status_code=400, detail="Printer ID already exists")
    success = raft_node.apply("add_printer", printer.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create printer")
    logger.info(f"Created printer {printer.id}")
    return printer

@router.get("/printers")
async def list_printers(raft_node: RaftNode = Depends(get_raft_node)):
    return list(raft_node.get_printers().values())

@router.post("/filaments")
async def create_filament(filament: Filament, raft_node: RaftNode = Depends(get_raft_node)):
    if filament.id in raft_node.get_filaments():
        raise HTTPException(status_code=400, detail="Filament ID already exists")
    success = raft_node.apply("add_filament", filament.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create filament")
    logger.info(f"Created filament {filament.id}")
    return filament

@router.get("/filaments")
async def list_filaments(raft_node: RaftNode = Depends(get_raft_node)):
    return list(raft_node.get_filaments().values())

@router.post("/print_jobs")
async def create_print_job(job: PrintJob, raft_node: RaftNode = Depends(get_raft_node)):
    if job.id in raft_node.get_print_jobs():
        raise HTTPException(status_code=400, detail="Print job ID already exists")
    if job.printer_id not in raft_node.get_printers():
        raise HTTPException(status_code=400, detail="Invalid printer ID")
    if job.filament_id not in raft_node.get_filaments():
        raise HTTPException(status_code=400, detail="Invalid filament ID")
    
    filament = raft_node.get_filaments()[job.filament_id]
    queued_running_weight = sum(
        j.print_weight_in_grams for j in raft_node.get_print_jobs().values()
        if j.filament_id == job.filament_id and j.status in ["Queued", "Running"]
    )
    if job.print_weight_in_grams > filament.remaining_weight_in_grams - queued_running_weight:
        raise HTTPException(status_code=400, detail="Insufficient filament weight")

    job.status = "Queued"
    success = raft_node.apply("add_print_job", job.dict())
    if not success:
        raise HTTPException(status_code=500, detail="Failed to create print job")
    logger.info(f"Created print job {job.id}")
    return job

@router.get("/print_jobs")
async def list_print_jobs(status: Optional[str] = None, raft_node: RaftNode = Depends(get_raft_node)):
    return list(raft_node.get_print_jobs(status).values())

@router.post("/print_jobs/{job_id}/status")
async def update_print_job_status(
    job_id: str, status: str, raft_node: RaftNode = Depends(get_raft_node)
):
    if job_id not in raft_node.get_print_jobs():
        raise HTTPException(status_code=404, detail="Print job not found")
    if status not in ["Running", "Done", "Cancelled"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    success = raft_node.apply("update_print_job_status", {"job_id": job_id, "status": status})
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update print job status")
    logger.info(f"Updated print job {job_id} to status {status}")
    return {"job_id": job_id, "status": status}