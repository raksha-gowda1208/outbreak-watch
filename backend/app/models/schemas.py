"""
Pydantic Schemas for OutbreakWatch API
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class OutbreakInjectionRequest(BaseModel):
    district_name: str = Field(..., example="Pune")
    syndrome_id: str = Field(..., example="SYN-ADD")
    spike_percentage: int = Field(..., ge=50, le=800, example=350, description="Percentage surge above baseline")
    days_duration: int = Field(default=3, ge=1, le=7, example=3)

class PrivacyConfigRequest(BaseModel):
    epsilon: float = Field(..., ge=0.1, le=5.0, example=1.0)
    k_threshold: int = Field(default=5, ge=2, le=20, example=5)

class HealthStatus(BaseModel):
    status: str
    version: str
    service: str
    timestamp: str
