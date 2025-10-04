from pydantic import BaseModel
from typing import Optional

class ImpactRequest(BaseModel):
    """Модель запиту для симуляції удару"""
    lat: float
    lon: float
    size: float
    speed: float
    angle: float
    material: Optional[str] = "stone"
    scenario: Optional[str] = "ground"