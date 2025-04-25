from pydantic import BaseModel
from typing import Literal

class PrintJob(BaseModel):
    id: str
    printer_id: str
    filament_id: str
    filepath: str
    print_weight_in_grams: int
    status: Literal["Queued", "Running", "Done", "Cancelled"]