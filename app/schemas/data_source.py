from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DataSourceOptionCreate(BaseModel):
    value: str
    display_text: str

class DataSourceCreate(BaseModel):
    name: str
    source_type: str
    configuration: Optional[Dict[str, Any]] = None
    options: Optional[List[DataSourceOptionCreate]] = None

class DataSourceResponse(BaseModel):
    id: int
    name: str
    source_type: str
    configuration: Optional[Dict[str, Any]] = None
    options: List[dict] = []