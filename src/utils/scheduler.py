from sqlalchemy import select

from src.database.core import conn
from src.database.models.user import User


async def update_users_limits():
    async with conn() as session:
        all_users_query = await session.execute(
            select(User)
        )
        all_users = all_users_query.scalars().all()

        for user in all_users:
            user.daily_image_limit = user.const_daily_image_limit
            user.daily_text_limit = user.const_daily_text_limit

        await session.commit()
