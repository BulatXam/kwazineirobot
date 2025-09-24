from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from src.database.models.user import User
from src.database.models.neiro import NeiroResponse


async def get_neiro_responses_count(period: str|None = None, model: str|None = None, user: User|None = None, session: AsyncSession = None) -> int:
	"""
	Возвращает количество объектов NeiroResponse за указанный период, модель и пользователя.
	period: "yesterday", "week", "month", "year", None - за весь период
	model: название модели нейросети, None - все модели
	user: объект модели User, None - все пользователи
	"""
	query = select(func.count()).select_from(NeiroResponse)
	now = datetime.now()
	if period is None or period == "all":
		pass  # Без фильтра по времени
	elif period == "yesterday":
		start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
		end = start + timedelta(days=1)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	elif period == "week":
		start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
		start = start - timedelta(days=7)
		end = start + timedelta(days=7)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	elif period == "month":
		start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		end = (start + timedelta(days=32)).replace(day=1)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	elif period == "year":
		start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
		end = start.replace(year=start.year + 1)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	else:
		raise ValueError("Invalid period value")
	if model:
		query = query.where(NeiroResponse.model == model)
	if user:
		query = query.where(NeiroResponse.user_id == user.id)
	result = await session.execute(query)
	return result.scalar() or 0


async def get_neiro_tokens_spent(period: str = None, model: str = None, user=None, session: AsyncSession = None) -> int:
	"""
	Возвращает количество потраченных токенов по периодам, моделям и пользователю.
	period: "yesterday", "week", "month", "year", None - за весь период
	model: название модели нейросети, None - все модели
	user: объект модели User, None - все пользователи
	"""
	query = select(func.sum(NeiroResponse.total_tokens)).select_from(NeiroResponse)
	now = datetime.now()
	if period is None or period == "all":
		pass  # Без фильтра по времени
	elif period == "yesterday":
		start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
		end = start + timedelta(days=1)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	elif period == "week":
		start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
		start = start - timedelta(days=7)
		end = start + timedelta(days=7)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	elif period == "month":
		start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		end = (start + timedelta(days=32)).replace(day=1)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	elif period == "year":
		start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
		end = start.replace(year=start.year + 1)
		query = query.where(NeiroResponse.created_at >= start, NeiroResponse.created_at < end)
	else:
		raise ValueError("Invalid period value")
	if model:
		query = query.where(NeiroResponse.model == model)
	if user:
		query = query.where(NeiroResponse.user_id == user.user_id)
	result = await session.execute(query)
	tokens = result.scalar()
	return int(tokens) if tokens else 0


async def get_statics_text(session: AsyncSession, user: User|None = None):
	return f"""
Всего было запросов:
<b>За все время:</b>
- Всего: <b>{await get_neiro_responses_count("all", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_responses_count("all", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_responses_count("all", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_responses_count("all", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_responses_count("all", "chatgpt-4-turbo", user=user, session=session)}

<b>За вчера:</b>
- Всего: <b>{await get_neiro_responses_count("yesterday", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_responses_count("yesterday", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_responses_count("yesterday", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_responses_count("yesterday", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_responses_count("yesterday", "chatgpt-4-turbo", user=user, session=session)}

<b>За неделю:</b>
- Всего: <b>{await get_neiro_responses_count("week", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_responses_count("week", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_responses_count("week", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_responses_count("week", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_responses_count("week", "chatgpt-4-turbo", user=user, session=session)}

<b>За месяц:</b>
- Всего: <b>{await get_neiro_responses_count("month", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_responses_count("month", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_responses_count("month", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_responses_count("month", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_responses_count("month", "chatgpt-4-turbo", user=user, session=session)}

<b>За год:</b>
- Всего: <b>{await get_neiro_responses_count("year", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_responses_count("year", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_responses_count("year", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_responses_count("year", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_responses_count("year", "chatgpt-4-turbo", user=user, session=session)}

Всего потрачено токенов:
<b>За все время:</b>
- Всего: <b>{await get_neiro_tokens_spent("all", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_tokens_spent("all", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_tokens_spent("all", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_tokens_spent("all", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_tokens_spent("all", "chatgpt-4-turbo", user=user, session=session)}

<b>За вчера:</b>
- Всего: <b>{await get_neiro_tokens_spent("yesterday", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_tokens_spent("yesterday", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_tokens_spent("yesterday", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_tokens_spent("yesterday", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_tokens_spent("yesterday", "chatgpt-4-turbo", user=user, session=session)}

<b>За неделю:</b>
- Всего: <b>{await get_neiro_tokens_spent("week", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_tokens_spent("week", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_tokens_spent("week", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_tokens_spent("week", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_tokens_spent("week", "chatgpt-4-turbo", user=user, session=session)}

<b>За месяц:</b>
- Всего: <b>{await get_neiro_tokens_spent("month", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_tokens_spent("month", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_tokens_spent("month", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_tokens_spent("month", "dall-e-3", user=user, session=session)}
- chatgpt-4-turbo: {await get_neiro_tokens_spent("month", "chatgpt-4-turbo", user=user, session=session)}

<b>За год:</b>
- Всего: <b>{await get_neiro_tokens_spent("year", user=user, session=session)}</b>
- hydra-gemini: {await get_neiro_tokens_spent("year", "hydra-gemini", user=user, session=session)}
- flux.1-schnell: {await get_neiro_tokens_spent("year", "flux.1-schnell", user=user, session=session)}
- dall-e-3: {await get_neiro_tokens_spent("year", "dall-e-3", user, session=session)}
- chatgpt-4-turbo: {await get_neiro_tokens_spent("year", "chatgpt-4-turbo", user, session=session)}
"""
