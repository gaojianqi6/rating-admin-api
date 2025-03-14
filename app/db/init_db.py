from sqlmodel import select
from app.models.admin_role import AdminRole
from app.models.admin_user import AdminUser
from app.core.security import hash_password
from app.db.session import get_session


async def init_super_admin():
    session = get_session()

    query = select(AdminRole).where(AdminRole.name == "Administrator")
    result = session.execute(query)
    admin_role = result.scalar_one_or_none()

    if not admin_role:
        admin_role = AdminRole(name="Administrator")
        session.add(admin_role)
        session.commit()
        session.refresh(admin_role)

    query = select(AdminUser).where(AdminUser.username == "jerome")
    result = session.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        super_admin = AdminUser(username="jerome", password=hash_password("123456"), role_id=admin_role.id)
        session.add(super_admin)
        session.commit()
