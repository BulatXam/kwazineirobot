"""Логика чат-бота для обработки заказов с профессиональным общением"""

# import httpx
import openai
import asyncio
import redis.asyncio as redis
import base64
import io

from typing import List, Optional
from loguru import logger

from src.schemas.chatgpt import MessageSchema, DialogSchema

from src.config import cnf


class ChatGPT:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=cnf.chatgpt.TOKEN,
            # http_client=httpx.AsyncClient(
            #     proxy=proxy,
            #     transport=httpx.HTTPTransport(local_address="0.0.0.0")
            # )
            base_url="https://api.hydraai.ru/v1"
        )
        self.redis = redis.from_url(cnf.redis.URL)

        self.history_len = 3

    @staticmethod
    def history_key_prefix(chat_id: str):
        return f"chat_history:{chat_id}"
    
    @staticmethod
    def project_key_prefix(chat_id: str):
        return f"project_params:{chat_id}"

    ############################## History #####################################

    async def get_chat_history(
            self, chat_id: str
        ) -> DialogSchema:
        """Получаем историю чата из Redis (последние 10 сообщений)"""
        key = self.history_key_prefix(chat_id)
    
        dialog_json = await self.redis.get(
            name=key
        )

        if dialog_json:
            dialog_schema = DialogSchema.model_validate_json(dialog_json)
        else:
            dialog_schema = DialogSchema()

        logger.debug(
            f"Get key<{self.history_key_prefix(chat_id)}> "
            f"Dialog history: {dialog_schema}"
        )

        return dialog_schema

    async def save_chat_history(
        self, chat_id: str, history: DialogSchema
    ) -> None:
        """Сохраняем историю чата в Redis"""

        if len(history.messages) > 10:
            history.messages = history.messages[-10:]

        key = self.history_key_prefix(chat_id=chat_id)
        value = history.model_dump_json()

        await self.redis.set(
            name=key,
            value=value,
            ex=86400
        )  # TTL 24 часа

        logger.debug(f"Set key:{key}, value: {history}")


    async def append_chat_history(
        self, chat_id: str, message: MessageSchema
    ) -> None:
        history = await self.get_chat_history(chat_id=chat_id)
        messages = history.messages[-self.history_len:]
        messages.append(message)

        await self.save_chat_history(
            chat_id=chat_id, history=DialogSchema(
                messages=messages
            )
        )

        logger.debug(
            f"Append message {message} in chat history"
        )
    
    async def clear_history(
            self, chat_id: str
        ) -> None:
        """Очищаем историю диалога для указанного chat_id"""
        await self.save_chat_history(
            chat_id=chat_id,
            history=DialogSchema(
                messages=[]
            )
        )
    
    async def _generate_ai_response(
        self, 
        chat_id: str,
        prompts: List[str] = None,
        dialog_history: Optional[DialogSchema] = None
    ) -> str:
        if not dialog_history:
            dialog_history = await self.get_chat_history(chat_id=chat_id)

        if prompts:
            system_messages = [MessageSchema(
                role="system",
                content=prompt,
            ) for prompt in prompts]
        else:
            system_messages = []

        messages = [message.model_dump() for message in dialog_history.messages]

        for _ in range(5):
            try:
                response = await self.client.chat.completions.create(
                    model="gpt-4o-mini",
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

        return response.choices[0].message.content

    async def _generate_image(
        self,
        prompt: str,
        model: str = "hydra-gemini"
    ) -> Optional[bytes]:
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
            )

            return base64.b64decode(response.data[0].b64_json)
        except Exception as e:
            (f"prompt: {prompt} : model: {model}")
            logger.error(f"Image generation error: {e} : prompt: {prompt} : model: {model}")
            return None

    async def send_message(
        self, 
        chat_id: str, 
        text: str,
        is_image: bool = False
    ) -> str|bytes:
        """Основной метод обработки сообщений
        
        chat_id: идентификатор чата
        text: текст сообщения
        """

        # Проверка на команду генерации изображения
        if is_image:
            model = "flux.1-schnell"
            prompt = text
            image_bytes = await self._generate_image(prompt, model)
            # await self.append_chat_history(
                # chat_id=chat_id,
                # message=MessageSchema(
                    # role="assistant",
                    # content=answer,
                # )
            # )
            return image_bytes

        message = MessageSchema(
            role="user",
            content=text
        )

        await self.append_chat_history(
            chat_id=chat_id,
            message=message
        )

        answer = await self._generate_ai_response(
            chat_id=chat_id
        )

        await self.append_chat_history(
            chat_id=chat_id,
            message=MessageSchema(
                role="assistant",
                content=answer,
            )
        )

        return answer


chatgpt = ChatGPT()
