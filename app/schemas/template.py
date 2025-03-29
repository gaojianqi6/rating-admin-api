from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TemplateFieldCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    field_type: str
    is_required: bool = False
    is_searchable: bool = False
    is_filterable: bool = False
    display_order: int
    data_source_id: Optional[int] = None
    validation_rules: Optional[Dict[str, Any]] = None

class TemplateCreate(BaseModel):
    name: str
    display_name: str
    description: str
    full_marks: int = 10
    fields: List[TemplateFieldCreate]

class TemplateResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str
    full_marks: int
    is_published: bool
    created_at: str
    updated_at: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    creator_name: Optional[str] = None
    updater_name: Optional[str] = None
    fields: List[dict] = []