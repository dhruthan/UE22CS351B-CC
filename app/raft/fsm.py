import json
from typing import Dict, Any
from threading import Lock
from app.models.printer import Printer, Filament
from app.models.printjob import PrintJob

class Raft3DFSM:
    def __init__(self):
        self.printers: Dict[str, Printer] = {}
        self.filaments: Dict[str, Filament] = {}
        self.print_jobs: Dict[str, PrintJob] = {}
        self.lock = Lock()

    def apply(self, log_entry: bytes) -> Any:
        with self.lock:
            try:
                cmd = json.loads(log_entry.decode())
                op = cmd.get("op")
                value = cmd.get("value")

                if op == "add_printer":
                    printer = Printer(**value)
                    self.printers[printer.id] = printer
                    return True
                elif op == "add_filament":
                    filament = Filament(**value)
                    self.filaments[filament.id] = filament
                    return True
                elif op == "add_print_job":
                    job = PrintJob(**value)
                    self.print_jobs[job.id] = job
                    return True
                elif op == "update_print_job_status":
                    job_id = value.get("job_id")
                    new_status = value.get("status")
                    job = self.print_jobs.get(job_id)
                    if not job:
                        return False

                    # Validate status transitions
                    valid_transitions = {
                        "Queued": ["Running", "Cancelled"],
                        "Running": ["Done", "Cancelled"],
                        "Done": [],
                        "Cancelled": []
                    }
                    if new_status not in valid_transitions[job.status]:
                        return False

                    job.status = new_status
                    if new_status == "Done":
                        filament = self.filaments.get(job.filament_id)
                        if filament:
                            filament.remaining_weight_in_grams -= job.print_weight_in_grams
                    return True
                return False
            except Exception as e:
                return str(e)

    def snapshot(self) -> bytes:
        with self.lock:
            state = {
                "printers": {k: v.dict() for k, v in self.printers.items()},
                "filaments": {k: v.dict() for k, v in self.filaments.items()},
                "print_jobs": {k: v.dict() for k, v in self.print_jobs.items()}
            }
            return json.dumps(state).encode()

    def restore(self, snapshot: bytes) -> None:
        with self.lock:
            state = json.loads(snapshot.decode())
            self.printers = {k: Printer(**v) for k, v in state.get("printers", {}).items()}
            self.filaments = {k: Filament(**v) for k, v in state.get("filaments", {}).items()}
            self.print_jobs = {k: PrintJob(**v) for k, v in state.get("print_jobs", {}).items()}