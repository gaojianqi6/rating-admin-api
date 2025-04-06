# app/schemas/item.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from app.lib.model_base import APIBaseModel


class ItemFieldValueBase(APIBaseModel):
    field_id: int
    field_name: str
    display_name: str
    field_type: str
    value: Any


class ItemStatisticsBase(APIBaseModel):
    avg_rating: float
    ratings_count: int
    views_count: int
    last_calculated_at: datetime


class ItemBase(APIBaseModel):
    title: str
    template_id: int


class ItemCreate(ItemBase):
    field_values: List[Dict[str, Any]]


class ItemResponse(BaseModel):
    id: int
    title: str
    slug: str
    template_id: int
    template_name: str
    created_by: int
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    avg_rating: float = 0
    ratings_count: int = 0
    views_count: int = 0
    field_values: Optional[List[ItemFieldValueBase]] = None


class ItemListItem(BaseModel):
    id: int
    title: str
    slug: str
    template_id: int
    template_name: str
    created_by: int
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    avg_rating: float = 0
    ratings_count: int = 0
    views_count: int = 0


class ItemListResponse(BaseModel):
    list: List[ItemListItem]
    pageNo: int
    pageSize: int
    total: int


class RatingBase(APIBaseModel):
    rating: float
    review_text: Optional[str] = None


class RatingCreate(RatingBase):
    item_id: int


class RatingResponse(BaseModel):
    id: int
    item_id: int
    user_id: int
    username: str
    rating: float
    review_text: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RatingListResponse(BaseModel):
    list: List[RatingResponse]
    pageNo: int
    pageSize: int
    total: int