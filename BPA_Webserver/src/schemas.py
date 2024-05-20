from pydantic import BaseModel, field_validator, Field
from datetime import datetime

class InspectionInstance(BaseModel):
    auto_id: str
    href: str
    timestamp: datetime = Field(default_factory=datetime.now)