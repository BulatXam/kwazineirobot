"""Логика чат-бота для обработки заказов с профессиональным общением"""

# import httpx
import openai
import asyncio
import redis.asyncio as redis

from typing import List, Optional, Tuple
from loguru import logger

from sqlalchemy import select, desc

from src.database.core import conn
from src.database.models.neiro import NeiroMessage
from src.database.models.user import User

from src.config import cnf

from src.schemas.neiro import DialogSchema, MessageSchema



class NeiroChat:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=cnf.openai.TOKEN,
            base_url="https://api.hydraai.ru/v1"
        )
        self.redis = redis.from_url(cnf.redis.URL)

        self.history_len = 3

    ############################## History #####################################

    async def _get_chat_history(
            self, chat_id: int
        ) -> DialogSchema:
        """Получаем историю чата из Redis (последние 3 сообщения)"""
        async with conn() as session:
            results = await session.execute(
                select(NeiroMessage).join(User).where(
                    User.user_id == chat_id
                ).order_by(desc(NeiroMessage.created_at)).limit(3)
            )
            messages: List[NeiroMessage] = results.scalars().all()

        dialog_schema = DialogSchema(
            messages=[
                MessageSchema(
                    role="user",
                    content=message.content
                ) for message in messages
            ]
        )

        logger.debug(
            f"Get dialog history: {dialog_schema}"
        )

        return dialog_schema

    async def _append_in_chat_history(
        self, chat_id: int, message: MessageSchema
    ) -> None:
        async with conn() as session:
            user_query = await session.execute(
                select(User).where(User.user_id == chat_id)
            )
            user = user_query.scalar_one_or_none()
            neiro_message = NeiroMessage(
                user=user,
                role=message.role,
                content=message.content
            )

            session.add(neiro_message)

            await session.commit()

        logger.debug(
            f"Append message {message} in chat history"
        )

    async def _generate_text(
        self, 
        chat_id: int,
        prompts: List[str] = None,
        dialog_history: Optional[DialogSchema] = None,
        model: str = "hydra-gemini"
    ) -> Optional[Tuple[str, int]]:
        if not dialog_history:
            dialog_history = await self._get_chat_history(chat_id=chat_id)

        if prompts:
            system_messages = [MessageSchema(
                role="system",
                content=prompt,
            ) for prompt in prompts]
        else:
            system_messages = []

        messages = [message.model_dump() for message in dialog_history.messages]

        response = None

        for _ in range(5):
            try:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=[
                        *system_messages, *messages
                    ],
                    temperature=0.3,
                    max_tokens=300,
                    timeout=10,
                )
                break
            except openai.RateLimitError:
                logger.warning(f"Превышен лимит токенов, ожидание 25 секунд")
                await asyncio.sleep(25)
                continue
        
        if response:
            return (
                response.choices[0].message.content,
                response.usage.total_tokens
            )
        else:
            return

    async def _generate_image(
        self,
        prompt: str,
        model: str = "flux.1-schnell"
    ) -> Optional[Tuple[str, int]]:
        """
        Генерирует изображение по текстовому описанию через HydraAI API.
        Возвращает URL изображения или None.
        """
        try:
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                n=1,
                size="1024x1024",
                timeout=30,
                response_format="url"
            )

            return response.data[0].url, response.usage.total_tokens
        except Exception as e:
            (f"prompt: {prompt} : model: {model}")
            logger.error(f"Image generation error: {e} : prompt: {prompt} : model: {model}")
            return None

    async def send_message(
        self, 
        chat_id: int, 
        prompt: str,
        is_image: bool = False
    ) -> Tuple[str, int]:
        """Основной метод обработки сообщений
        
        chat_id: идентификатор чата
        content: текст сообщения
        """

        # Проверка на команду генерации изображения
        if is_image:
            return await self._generate_image(
                prompt=prompt
            )

        message = MessageSchema(
            role="user",
            content=prompt
        )

        await self._append_in_chat_history(
            chat_id=chat_id,
            message=message
        )

        answer, total_tokens = await self._generate_text(
            chat_id=chat_id,
        )

        await self._append_in_chat_history(
            chat_id=chat_id,
            message=MessageSchema(
                role="assistant",
                content=answer,
            )
        )

        return answer, total_tokens


neiro_chat = NeiroChat()
