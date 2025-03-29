from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select, Session
from typing import List
from app.db.session import get_session
from app.models.field_data_source import FieldDataSource
from app.models.field_data_source_option import FieldDataSourceOption
from app.schemas.data_source import DataSourceCreate, DataSourceResponse
from app.api.v1.endpoints.users import get_current_user
from app.models.admin_user import AdminUser

router = APIRouter(prefix="/data-sources", tags=["data-sources"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=DataSourceResponse)
async def create_data_source(
        data_source: DataSourceCreate,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    # Create data source
    db_data_source = FieldDataSource(
        name=data_source.name,
        source_type=data_source.source_type,
        configuration=data_source.configuration,
        created_by=current_user.id
    )
    session.add(db_data_source)
    session.commit()
    session.refresh(db_data_source)

    # Create options if provided
    if data_source.options:
        for option in data_source.options:
            db_option = FieldDataSourceOption(
                data_source_id=db_data_source.id,
                value=option.value,
                display_text=option.display_text
            )
            session.add(db_option)
        session.commit()

    # Fetch options for response
    options = session.exec(
        select(FieldDataSourceOption).where(FieldDataSourceOption.data_source_id == db_data_source.id)
    ).all()

    return {
        "id": db_data_source.id,
        "name": db_data_source.name,
        "source_type": db_data_source.source_type,
        "configuration": db_data_source.configuration,
        "options": [{"id": opt.id, "value": opt.value, "display_text": opt.display_text} for opt in options]
    }


@router.get("/", response_model=List[DataSourceResponse])
async def get_data_sources(session: Session = Depends(get_session)):
    data_sources = session.exec(select(FieldDataSource)).all()
    result = []

    for ds in data_sources:
        options = session.exec(
            select(FieldDataSourceOption).where(FieldDataSourceOption.data_source_id == ds.id)
        ).all()

        result.append({
            "id": ds.id,
            "name": ds.name,
            "source_type": ds.source_type,
            "configuration": ds.configuration,
            "options": [{"id": opt.id, "value": opt.value, "display_text": opt.display_text} for opt in options]
        })

    return result