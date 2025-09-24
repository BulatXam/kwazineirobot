from typing import TypeVar, Generic, Sequence

from sqlalchemy import Column, BigInteger, DateTime, func
from sqlalchemy.orm import DeclarativeBase, selectinload, load_only
from sqlalchemy.sql import select, update as sqlalchemy_update, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from loguru import logger

T = TypeVar("T")

class ModelCRUD(Generic[T]):
    @classmethod
    async def create(cls, session: AsyncSession, **kwargs) -> T:
        """
            Создает новый объект и возвращает его.
        :param kwargs: Поля и значения для объекта.
        :return: Созданный объект.
        """

        obj = cls(**kwargs)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj
    
    @classmethod
    async def add(cls, session: AsyncSession, **kwargs) -> None:
        """
            Создает новый объект.
        :param kwargs: Поля и значения для объекта.
        """

        session.add(cls(**kwargs))
        await session.commit()

    async def update(self, session: AsyncSession, **kwargs) -> None:
        """
            Обновляет текущий объект.
        :param kwargs: Поля и значения, которые надо поменять.
        """
        await session.execute(
            sqlalchemy_update(self.__class__), [{"id": self.id, **kwargs}]
        )
        await session.commit()

    async def delete(self, session: AsyncSession) -> None:
        """
            Удаляет объект.
        """
        await session.delete(self)
        await session.commit()

    @classmethod
    async def get(cls, session: AsyncSession, select_in_load: str | None = None, **kwargs) -> T|None:
        """
            Возвращает одну запись, которая удовлетворяет введенным параметрам.
        :param select_in_load: Загрузить сразу связанную модель.
        :param kwargs: Поля и значения.
        :return: Объект или вызовет исключение DoesNotExists.
        """

        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls).where(*params)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        try:
            results = await session.execute(query)
            (result,) = results.one()
            return result
        except NoResultFound:
            return None

    @classmethod
    async def check(cls, session: AsyncSession, **kwargs) -> int | None:
        """
            Проверить наличие записи в таблице не тяжелым запросом и вернуть только его id
        :param kwargs: Id of obj
        """
        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls.id).where(*params)

        try:
            results = await session.execute(query)
            (result,) = results.one()
            return result
        except NoResultFound:
            return None

    @classmethod
    async def filter(cls, session: AsyncSession, select_in_load: str | None = None, **kwargs) -> Sequence[T]:
        """
            Возвращает все записи, которые удовлетворяют введенным параметрам.
        :param select_in_load: Загрузить сразу связанную модель.
        :param kwargs: Поля и значения.
        :return: Перечень записей.
        """

        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(cls).where(*params)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        try:
            results = await session.execute(query)
            return results.scalars().all()
        except NoResultFound:
            return ()
    
    @classmethod
    async def count(cls, session: AsyncSession, select_in_load: str | None = None, **kwargs) -> int|None:
        params = [getattr(cls, key) == val for key, val in kwargs.items()]
        query = select(func.count()).select_from(cls).where(*params)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        try:
            results = await session.execute(query)
            return results.scalar()
        except NoResultFound:
            return ()

    @classmethod
    async def all(cls, session: AsyncSession, select_in_load: str = None, values: list[str] = None) -> Sequence[T]:
        """
            Получение всех записей
        :param select_in_load: Загрузить сразу связанную модель.
        :param values: Список полей, которые надо вернуть, если нет, то все (default None).
        """
        if values and isinstance(values, list):
            # Определенные поля
            values = [getattr(cls, val) for val in values if isinstance(val, str)]
            query = select(cls).options(load_only(*values))
        else:
            # Все поля
            query = select(cls)

        if select_in_load:
            query.options(selectinload(getattr(cls, select_in_load)))

        result = await session.execute(query)
        return result.scalars().all()


class BaseModel(DeclarativeBase, ModelCRUD):
    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
