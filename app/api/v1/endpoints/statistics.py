from fastapi import APIRouter, Depends
from sqlmodel import select, Session, func
from app.db.session import get_session
from app.models.item import Item
from app.models.template import Template
from app.models.item_statistics import ItemStatistics
from app.api.v1.endpoints.users import get_current_user
from app.models.admin_user import AdminUser
from typing import Dict

router = APIRouter(prefix="/statistics", tags=["statistics"])

@router.get("/total", summary="Get total statistics")
async def get_total_statistics(
    session: Session = Depends(get_session),
    current_user: AdminUser = Depends(get_current_user)
) -> Dict:
    """
    Get total statistics including:
    - Total number of items
    - Number of items per template
    - Average rating across all items
    """
    # Get total items count
    total_items = session.exec(select(func.count(Item.id))).one()

    # Get items count per template
    template_counts_query = (
        select(Template.name, func.count(Item.id))
        .outerjoin(Item, Template.id == Item.template_id)
        .group_by(Template.name)
    )
    template_counts = {
        name: count
        for name, count in session.exec(template_counts_query).all()
    }

    # Calculate overall average rating
    avg_rating_query = select(
        func.coalesce(func.avg(ItemStatistics.avg_rating), 0.0).label("avg_rating"),
        func.sum(ItemStatistics.ratings_count).label("total_ratings")
    )
    avg_rating_result = session.exec(avg_rating_query).one()
    
    return {
        "total_items": total_items,
        "items_by_template": template_counts,
        "overall_statistics": {
            "average_rating": round(float(avg_rating_result[0]), 2),
            "total_ratings": avg_rating_result[1] or 0
        }
    } 