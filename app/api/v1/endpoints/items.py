# app/api/v1/endpoints/items.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select, Session, func, and_, or_, col
from typing import List, Optional, Dict, Any
from app.db.session import get_session
from app.models.item import Item
from app.models.item_field_value import ItemFieldValue
from app.models.item_statistics import ItemStatistics
from app.models.template import Template
from app.models.template_field import TemplateField
from app.models.user import User
from app.models.user_rating import UserRating
from app.models.admin_user import AdminUser
from app.schemas.item import ItemResponse, ItemListResponse, RatingListResponse
from app.api.v1.endpoints.users import get_current_user
from datetime import datetime, date
import logging

router = APIRouter(prefix="/items", tags=["items"])
logger = logging.getLogger(__name__)

@router.get("", response_model=ItemListResponse)
@router.get("/", response_model=ItemListResponse)
async def get_items(
        pageNo: int = Query(1),
        pageSize: int = Query(10),
        title: Optional[str] = None,
        templateId: Optional[int] = Query(None),
        createdTimeStart: Optional[date] = Query(None),
        createdTimeEnd: Optional[date] = Query(None),
        sortField: Optional[str] = Query("created_at"),
        sortOrder: Optional[str] = Query("desc"),
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    """
    Get a list of items with optional filtering and sorting.
    Admin users can see all items with ratings statistics.
    """
    # Calculate offset for pagination
    offset = (pageNo - 1) * pageSize

    # Build base query - join with statistics and template
    query = (
        select(
            Item,
            Template.display_name.label("template_name"),
            ItemStatistics.avg_rating,
            ItemStatistics.ratings_count,
            ItemStatistics.views_count
        )
        .join(Template, Item.template_id == Template.id)
        .join(ItemStatistics, Item.id == ItemStatistics.item_id, isouter=True)
    )

    count_query = select(func.count(Item.id))
    count_query = count_query.join(Template, Item.template_id == Template.id)

    # Apply filters
    filters = []

    # Title filter
    if title:
        filters.append(Item.title.ilike(f"%{title}%"))

    # Template filter
    if templateId:
        filters.append(Item.template_id == templateId)

    # Date range filter
    if createdTimeStart:
        created_date_start = datetime.combine(createdTimeStart, datetime.min.time())
        filters.append(Item.created_at >= created_date_start)

    if createdTimeEnd:
        created_date_end = datetime.combine(createdTimeEnd, datetime.max.time())
        filters.append(Item.created_at <= created_date_end)

    # Apply all filters
    if filters:
        filter_condition = and_(*filters)
        query = query.where(filter_condition)
        count_query = count_query.where(filter_condition)

    # Apply sorting
    sort_column_map = {
        "id": Item.id,
        "title": Item.title,
        "created_at": Item.created_at,
        "updated_at": Item.updated_at,
        "avg_rating": ItemStatistics.avg_rating,
        "ratings_count": ItemStatistics.ratings_count,
        "views_count": ItemStatistics.views_count
    }

    sort_column = sort_column_map.get(sortField, Item.created_at)

    if sortOrder.lower() == "asc":
        query = query.order_by(sort_column)
    else:
        query = query.order_by(sort_column.desc())

    # Get total count
    total = session.exec(count_query).one()

    # Apply pagination
    query = query.offset(offset).limit(pageSize)

    # Execute query
    results = session.exec(query).all()

    # Prepare items list
    items_list = []
    for item, template_name, avg_rating, ratings_count, views_count in results:
        # Get creator
        creator = session.get(User, item.created_by)

        items_list.append({
            "id": item.id,
            "title": item.title,
            "slug": item.slug,
            "template_id": item.template_id,
            "template_name": template_name,
            "created_by": item.created_by,
            "created_by_name": creator.username if creator else None,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "avg_rating": float(avg_rating or 0),
            "ratings_count": int(ratings_count or 0),
            "views_count": int(views_count or 0)
        })

    return {
        "list": items_list,
        "pageNo": pageNo,
        "pageSize": pageSize,
        "total": total
    }


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item_details(
        item_id: int,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    """
    Get detailed information about a specific item including field values.
    """
    # Query item with template and stats
    query = (
        select(
            Item,
            Template.display_name.label("template_name"),
            ItemStatistics.avg_rating,
            ItemStatistics.ratings_count,
            ItemStatistics.views_count
        )
        .join(Template, Item.template_id == Template.id)
        .join(ItemStatistics, Item.id == ItemStatistics.item_id, isouter=True)
        .where(Item.id == item_id)
    )

    result = session.exec(query).first()

    if not result:
        raise HTTPException(status_code=404, detail="Item not found")

    item, template_name, avg_rating, ratings_count, views_count = result

    # Get creator
    creator = session.get(User, item.created_by)

    # Get field values
    field_values_query = (
        select(ItemFieldValue, TemplateField)
        .join(TemplateField, ItemFieldValue.field_id == TemplateField.id)
        .where(ItemFieldValue.item_id == item_id)
    )

    field_values_result = session.exec(field_values_query).all()

    field_values = []
    for field_value, template_field in field_values_result:
        # Determine the value based on field type
        value = None
        if template_field.field_type == "text" or template_field.field_type == "textarea"  or template_field.field_type == "select":
            value = field_value.text_value
        elif template_field.field_type == "number":
            value = field_value.numeric_value
        elif template_field.field_type == "date":
            value = field_value.date_value
        elif template_field.field_type == "boolean":
            value = field_value.boolean_value
        elif template_field.field_type in ["json", "multiselect"]:
            value = field_value.json_value

        field_values.append({
            "field_id": field_value.field_id,
            "field_name": template_field.name,
            "display_name": template_field.display_name,
            "field_type": template_field.field_type,
            "value": value
        })

    return {
        "id": item.id,
        "title": item.title,
        "slug": item.slug,
        "template_id": item.template_id,
        "template_name": template_name,
        "created_by": item.created_by,
        "created_by_name": creator.username if creator else None,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "avg_rating": float(avg_rating or 0),
        "ratings_count": int(ratings_count or 0),
        "views_count": int(views_count or 0),
        "field_values": field_values
    }


@router.get("/{item_id}/ratings", response_model=RatingListResponse)
async def get_item_ratings(
        item_id: int,
        pageNo: int = Query(1),
        pageSize: int = Query(10),
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    """
    Get all ratings for a specific item.
    """
    # Check if item exists
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Calculate offset for pagination
    offset = (pageNo - 1) * pageSize

    # Query ratings
    query = select(UserRating).where(UserRating.item_id == item_id)
    count_query = select(func.count(UserRating.id)).where(UserRating.item_id == item_id)

    # Sort by creation date (newest first)
    query = query.order_by(UserRating.created_at.desc())

    # Get total count
    total = session.exec(count_query).one()

    # Apply pagination
    query = query.offset(offset).limit(pageSize)

    # Execute query
    ratings = session.exec(query).all()

    # Format response
    ratings_list = []
    for rating in ratings:
        # Get user info
        user = session.get(User, rating.user_id)

        ratings_list.append({
            "id": rating.id,
            "item_id": rating.item_id,
            "user_id": rating.user_id,
            "username": user.username if user else "Unknown",
            "rating": float(rating.rating),
            "review_text": rating.review_text,
            "created_at": rating.created_at,
            "updated_at": rating.updated_at
        })

    return {
        "list": ratings_list,
        "pageNo": pageNo,
        "pageSize": pageSize,
        "total": total
    }


@router.delete("/{item_id}")
async def delete_item(
        item_id: int,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    """
    Delete an item and all associated data (field values, statistics, ratings).
    """
    # Check if item exists
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Cascading delete should handle related records, but we'll be explicit

    # Delete field values
    session.exec(
        select(ItemFieldValue).where(ItemFieldValue.item_id == item_id)
    ).all()

    for field_value in session.exec(
            select(ItemFieldValue).where(ItemFieldValue.item_id == item_id)
    ).all():
        session.delete(field_value)

    # Delete ratings
    for rating in session.exec(
            select(UserRating).where(UserRating.item_id == item_id)
    ).all():
        session.delete(rating)

    # Delete statistics
    statistics = session.exec(
        select(ItemStatistics).where(ItemStatistics.item_id == item_id)
    ).first()
    if statistics:
        session.delete(statistics)

    # Delete the item
    session.delete(item)
    session.commit()

    logger.info(f"Deleted item ID: {item_id} by admin user: {current_user.id} ({current_user.username})")

    return {"status": "success", "message": "Item deleted successfully"}