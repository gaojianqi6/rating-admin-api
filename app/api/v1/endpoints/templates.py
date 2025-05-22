from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, Session, func, delete
from typing import List, Optional, Dict, Any
from app.db.session import get_session
from app.models.template import Template
from app.models.template_field import TemplateField
from app.models.admin_user import AdminUser
from app.schemas.template import TemplateCreate, TemplateResponse
from app.api.v1.endpoints.users import get_current_user
from datetime import datetime
import logging

router = APIRouter(prefix="/templates", tags=["templates"])
logger = logging.getLogger(__name__)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=TemplateResponse)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TemplateResponse)
async def create_template(
        template: TemplateCreate,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    # Create template
    db_template = Template(
        name=template.name,
        display_name=template.display_name,
        description=template.description,
        full_marks=template.full_marks,
        created_by=current_user.id,
        updated_by=current_user.id
    )
    session.add(db_template)
    session.commit()
    session.refresh(db_template)

    # Create template fields
    for field in template.fields:
        db_field = TemplateField(
            template_id=db_template.id,
            name=field.name,
            display_name=field.display_name,
            description=field.description,
            field_type=field.field_type,
            is_required=field.is_required,
            is_searchable=field.is_searchable,
            is_filterable=field.is_filterable,
            display_order=field.display_order,
            data_source_id=field.data_source_id,
            validation_rules=field.validation_rules
        )
        session.add(db_field)

    session.commit()

    # Load creator name
    creator = session.get(AdminUser, current_user.id)
    creator_name = creator.username if creator else None

    # Load fields for response
    fields = session.exec(
        select(TemplateField).where(TemplateField.template_id == db_template.id)
    ).all()

    return {
        "id": db_template.id,
        "name": db_template.name,
        "display_name": db_template.display_name,
        "description": db_template.description,
        "full_marks": db_template.full_marks,
        "is_published": db_template.is_published,
        "created_at": db_template.created_at.isoformat(),
        "updated_at": db_template.updated_at.isoformat(),
        "created_by": db_template.created_by,
        "updated_by": db_template.updated_by,
        "creator_name": creator_name,
        "updater_name": creator_name,  # Same as creator for new template
        "fields": [
            {
                "id": field.id,
                "name": field.name,
                "display_name": field.display_name,
                "description": field.description,
                "field_type": field.field_type,
                "is_required": field.is_required,
                "is_searchable": field.is_searchable,
                "is_filterable": field.is_filterable,
                "display_order": field.display_order,
                "data_source_id": field.data_source_id,
                "validation_rules": field.validation_rules
            }
            for field in fields
        ]
    }


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
        template_id: int,
        template: TemplateCreate,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    logger.info(f"=== TEMPLATE UPDATE START ===")
    logger.info(f"Template ID: {template_id}")
    logger.info(f"Current User: {current_user.username} (ID: {current_user.id})")

    # Check if template exists
    db_template = session.get(Template, template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update template fields only if provided
    db_template.name = template.name
    db_template.display_name = template.display_name
    db_template.description = template.description
    db_template.full_marks = template.full_marks
    db_template.updated_by = current_user.id
    db_template.updated_at = datetime.utcnow()

    # Fetch existing fields
    existing_fields = {
        field.id: field for field in session.exec(
            select(TemplateField).where(TemplateField.template_id == template_id)
        ).all()
    }

    # Process incoming fields
    incoming_field_ids = set()
    for field_data in template.fields:
        if field_data.id is not None and field_data.id != -1:
            # Update existing field
            if field_data.id in existing_fields:
                db_field = existing_fields[field_data.id]
                db_field.name = field_data.name
                db_field.display_name = field_data.display_name
                db_field.description = field_data.description
                db_field.field_type = field_data.field_type
                db_field.is_required = field_data.is_required
                db_field.is_searchable = field_data.is_searchable
                db_field.is_filterable = field_data.is_filterable
                db_field.display_order = field_data.display_order
                db_field.data_source_id = field_data.data_source_id
                db_field.validation_rules = field_data.validation_rules
                session.add(db_field)
                incoming_field_ids.add(field_data.id)
            else:
                raise HTTPException(status_code=400, detail=f"Field with id {field_data.id} does not exist")
        else:
            # Check for duplicate field name
            existing_field_names = {field.name for field in existing_fields.values()}
            if field_data.name in existing_field_names:
                raise HTTPException(status_code=400,
                                    detail=f"Field with name {field_data.name} already exists for this template")
            # Create new field
            db_field = TemplateField(
                template_id=db_template.id,
                name=field_data.name,
                display_name=field_data.display_name,
                description=field_data.description,
                field_type=field_data.field_type,
                is_required=field_data.is_required,
                is_searchable=field_data.is_searchable,
                is_filterable=field_data.is_filterable,
                display_order=field_data.display_order,
                data_source_id=field_data.data_source_id,
                validation_rules=field_data.validation_rules
            )
            session.add(db_field)

    # Delete fields not in the payload
    for field_id in existing_fields:
        if field_id not in incoming_field_ids:
            session.delete(existing_fields[field_id])

    session.commit()
    session.refresh(db_template)

    # Load creator and updater
    creator = session.get(AdminUser, db_template.created_by) if db_template.created_by else None
    updater = session.get(AdminUser, current_user.id)

    # Load fields for response
    fields = session.exec(
        select(TemplateField).where(TemplateField.template_id == db_template.id)
    ).all()

    return {
        "id": db_template.id,
        "name": db_template.name,
        "display_name": db_template.display_name,
        "description": db_template.description,
        "full_marks": db_template.full_marks,
        "is_published": db_template.is_published,
        "created_at": db_template.created_at.isoformat(),
        "updated_at": db_template.updated_at.isoformat(),
        "created_by": db_template.created_by,
        "updated_by": db_template.updated_by,
        "creator_name": creator.username if creator else None,
        "updater_name": updater.username if updater else None,
        "fields": [
            {
                "id": field.id,
                "name": field.name,
                "display_name": field.display_name,
                "description": field.description,
                "field_type": field.field_type,
                "is_required": field.is_required,
                "is_searchable": field.is_searchable,
                "is_filterable": field.is_filterable,
                "display_order": field.display_order,
                "data_source_id": field.data_source_id,
                "validation_rules": field.validation_rules
            }
            for field in fields
        ]
    }

@router.get("")
@router.get("/")
async def get_templates(
        page_no: int = Query(1, alias="pageNo"),
        page_size: int = Query(10, alias="pageSize"),
        search: Optional[str] = None,
        is_published: Optional[bool] = None,
        status: Optional[str] = None,  # Added status filter similar to your frontend
        session: Session = Depends(get_session)
):
    # Calculate offset for pagination
    offset = (page_no - 1) * page_size

    # Construct base query
    query = select(Template)
    count_query = select(func.count(Template.id))

    # Add filters
    if is_published is not None:
        query = query.where(Template.is_published == is_published)
        count_query = count_query.where(Template.is_published == is_published)

    # Handle status filter (convert from string to boolean)
    if status is not None:
        if status.lower() == "published":
            query = query.where(Template.is_published == True)
            count_query = count_query.where(Template.is_published == True)
        elif status.lower() == "draft":
            query = query.where(Template.is_published == False)
            count_query = count_query.where(Template.is_published == False)

    # Add search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Template.name.ilike(search_term)) |
            (Template.display_name.ilike(search_term)) |
            (Template.description.ilike(search_term))
        )
        count_query = count_query.where(
            (Template.name.ilike(search_term)) |
            (Template.display_name.ilike(search_term)) |
            (Template.description.ilike(search_term))
        )

    # Get total count for pagination
    total = session.exec(count_query).one()

    # Apply pagination
    query = query.offset(offset).limit(page_size)

    # Execute query
    templates = session.exec(query).all()

    # Process templates
    template_list = []
    for tmpl in templates:
        # Get creator and updater
        creator = session.get(AdminUser, tmpl.created_by) if tmpl.created_by else None
        updater = session.get(AdminUser, tmpl.updated_by) if tmpl.updated_by else None

        # Get fields
        fields = session.exec(
            select(TemplateField).where(TemplateField.template_id == tmpl.id)
        ).all()

        # Get field count
        field_count = len(fields)

        template_list.append({
            "id": tmpl.id,
            "name": tmpl.name,
            "displayName": tmpl.display_name,  # Convert to camelCase for frontend
            "description": tmpl.description,
            "fullMarks": tmpl.full_marks,
            "status": "published" if tmpl.is_published else "draft",  # Add string status
            "isPublished": tmpl.is_published,  # Keep the original boolean field
            "createdAt": tmpl.created_at.isoformat(),
            "updatedAt": tmpl.updated_at.isoformat(),
            "createdBy": tmpl.created_by,
            "updatedBy": tmpl.updated_by,
            "creatorName": creator.username if creator else None,
            "updaterName": updater.username if updater else None,
            "fieldCount": field_count,  # Add field count for the UI
            "fields": [
                {
                    "id": field.id,
                    "name": field.name,
                    "displayName": field.display_name,
                    "description": field.description,
                    "fieldType": field.field_type,
                    "isRequired": field.is_required,
                    "isSearchable": field.is_searchable,
                    "isFilterable": field.is_filterable,
                    "displayOrder": field.display_order,
                    "dataSourceId": field.data_source_id,
                    "validationRules": field.validation_rules
                }
                for field in fields
            ]
        })

    # Return in the same format as your users endpoint
    return {
        "list": template_list,
        "pageNo": page_no,
        "pageSize": page_size,
        "total": total
    }


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, session: Session = Depends(get_session)):
    template = session.get(Template, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Get creator and updater
    creator = session.get(AdminUser, template.created_by) if template.created_by else None
    updater = session.get(AdminUser, template.updated_by) if template.updated_by else None

    # Get fields
    fields = session.exec(
        select(TemplateField).where(TemplateField.template_id == template.id)
    ).all()

    return {
        "id": template.id,
        "name": template.name,
        "display_name": template.display_name,
        "description": template.description,
        "full_marks": template.full_marks,
        "is_published": template.is_published,
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat(),
        "created_by": template.created_by,
        "updated_by": template.updated_by,
        "creator_name": creator.username if creator else None,
        "updater_name": updater.username if updater else None,
        "fields": [
            {
                "id": field.id,
                "name": field.name,
                "display_name": field.display_name,
                "description": field.description,
                "field_type": field.field_type,
                "is_required": field.is_required,
                "is_searchable": field.is_searchable,
                "is_filterable": field.is_filterable,
                "display_order": field.display_order,
                "data_source_id": field.data_source_id,
                "validation_rules": field.validation_rules
            }
            for field in fields
        ]
    }


@router.patch("/{template_id}/publish")
async def publish_template(
        template_id: int,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    template = session.get(Template, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.is_published = True
    template.updated_at = datetime.utcnow()
    template.updated_by = current_user.id

    session.add(template)
    session.commit()

    return {"status": "success", "message": "Template published successfully"}


@router.patch("/{template_id}/unpublish")
async def unpublish_template(
        template_id: int,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    template = session.get(Template, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template.is_published = False
    template.updated_at = datetime.utcnow()
    template.updated_by = current_user.id

    session.add(template)
    session.commit()

    return {"status": "success", "message": "Template unpublished successfully"}


@router.delete("/{template_id}")
async def delete_template(
        template_id: int,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    template = session.get(Template, template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Delete associated fields first (cascade delete might be set up, but being explicit)
    session.exec(
        delete(TemplateField).where(TemplateField.template_id == template_id)
    )

    # Delete the template
    session.delete(template)
    session.commit()

    logger.info(f"Deleting template ID: {template_id} by user: {current_user.id}, {current_user.username}")

    return {"status": "success", "message": "Template deleted successfully"}


@router.post("/{template_id}/clone")
async def clone_template(
        template_id: int,
        session: Session = Depends(get_session),
        current_user: AdminUser = Depends(get_current_user)
):
    # Get the original template
    original = session.get(Template, template_id)
    if not original:
        raise HTTPException(status_code=404, detail="Template not found")

    # Create a new template based on the original
    new_template = Template(
        name=f"{original.name} (Copy)",
        display_name=f"{original.display_name} (Copy)",
        description=original.description,
        full_marks=original.full_marks,
        is_published=False,  # Always unpublished for clones
        created_by=current_user.id,
        updated_by=current_user.id
    )
    session.add(new_template)
    session.flush()  # Get the new ID

    # Get all fields from the original template
    original_fields = session.exec(
        select(TemplateField).where(TemplateField.template_id == template_id)
    ).all()

    # Clone each field
    for field in original_fields:
        new_field = TemplateField(
            template_id=new_template.id,
            name=field.name,
            display_name=field.display_name,
            description=field.description,
            field_type=field.field_type,
            is_required=field.is_required,
            is_searchable=field.is_searchable,
            is_filterable=field.is_filterable,
            display_order=field.display_order,
            data_source_id=field.data_source_id,
            validation_rules=field.validation_rules
        )
        session.add(new_field)

    session.commit()
    session.refresh(new_template)

    # Load creator name
    creator = session.get(AdminUser, current_user.id)
    creator_name = creator.username if creator else None

    logger.info(f"Clone template: {new_template.id}, {new_template.name} by user: {current_user.id}, {current_user.username}")

    return {
        "status": "success",
        "message": "Template cloned successfully",
        "template": {
            "id": new_template.id,
            "name": new_template.name,
            "display_name": new_template.display_name,
            "description": new_template.description,
            "full_marks": new_template.full_marks,
            "is_published": new_template.is_published,
            "created_at": new_template.created_at.isoformat(),
            "updated_at": new_template.updated_at.isoformat(),
            "created_by": new_template.created_by,
            "updated_by": new_template.updated_by,
            "creator_name": creator_name,
            "updater_name": creator_name
        }
    }