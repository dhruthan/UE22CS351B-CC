from pydantic import BaseModel, validator
from typing import Literal

class Printer(BaseModel):
    id: str
    company: str
    model: str

class Filament(BaseModel):
    id: str
    type: Literal["PLA", "PETG", "ABS", "TPU"]
    color: str
    total_weight_in_grams: int
    remaining_weight_in_grams: int

    @validator("remaining_weight_in_grams")
    def check_remaining_weight(cls, v, values):
        if v > values.get("total_weight_in_grams", v):
            raise ValueError("Remaining weight cannot exceed total weight")
        return v