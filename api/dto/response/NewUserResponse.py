from pydantic import BaseModel
from typing import Dict, Any

class NewUserResponse(BaseModel):
    status: str
    data: Dict[str, Any]
    timestamp: str