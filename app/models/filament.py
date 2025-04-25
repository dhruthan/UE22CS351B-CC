from pydantic import BaseModel, Field
from typing import Optional

class Filament(BaseModel):
    id: str = Field(..., description="Unique identifier for the filament")
    type: str = Field(..., description="Type of filament (e.g., PLA, ABS)")
    color: str = Field(..., description="Color of the filament")
    total_weight_in_grams: int = Field(..., gt=0, description="Total weight of the filament in grams")
    remaining_weight_in_grams: int = Field(..., ge=0, description="Remaining weight of the filament in grams")
    printer_id: Optional[str] = Field(None, description="ID of the printer using this filament, if assigned")

    class Config:
        schema_extra = {
            "example": {
                "id": "f1",
                "type": "PLA",
                "color": "Blue",
                "total_weight_in_grams": 1000,
                "remaining_weight_in_grams": 1000,
                "printer_id": "p1"
            }
        }