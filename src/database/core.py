from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .models.core.base import BaseModel

from ..config import cnf

engine = create_async_engine(
    url=cnf.psql.URL,
    pool_size=50,
    max_overflow=20
)

postgres_conn = async_sessionmaker(engine)


async def init_psql() -> bool:
    """
        Create all tables in db
    :return: True or False
    """
    async with postgres_conn() as s:
        # await s.run_sync(
        #     lambda s_value: Base.metadata.drop_all(
        #         bind=s_value.bind
        #     )
        # )

        await s.run_sync(
            lambda s_value: BaseModel.metadata.create_all(
                bind=s_value.bind
            )
        )
        return True
