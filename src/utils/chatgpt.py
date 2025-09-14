"""Логика чат-бота для обработки заказов с профессиональным общением"""

import openai

from io import BytesIO

import json
import asyncio

from typing import List, Dict, Optional, Tuple
from loguru import logger

from src.schemas.chatgpt import ProjectSchema, MessageSchema, DialogSchema

from src.config import cnf


class ChatGPT:
    def __init__(self, api_key=cnf.chatgpt.TOKEN):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            # http_client=httpx.AsyncClient(
            #     proxy=proxy,
            #     transport=httpx.HTTPTransport(local_address="0.0.0.0")
            # )
        )
        self.redis = redis.from_url(redis_url)

        self.history_len = 20

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
        await self.save_project(
            chat_id=chat_id,
            project=ProjectSchema()
        )
    
    ############################## Project #####################################

    async def get_project(self, chat_id: str):
        project_params_json = await self.redis.get(
            self.project_key_prefix(chat_id=chat_id)
        )

        if project_params_json:
            project_params = json.loads(project_params_json)

            project_schema = ProjectSchema(
                **project_params
            )
        else:
            project_schema = ProjectSchema()

        logger.debug(f"Get project schema {project_schema}")

        return project_schema

    async def save_project(self, chat_id: str, project: ProjectSchema):
        logger.debug(f"Save project {project}")

        await self.redis.set(
            name=self.project_key_prefix(chat_id=chat_id),
            value=project.model_dump_json()
        )

    ################################ Messages ##################################

    async def _extract_project_description_param(
        self, chat_id: str, dialog_history: Optional[DialogSchema]
    ):
        project = await self.get_project(chat_id=chat_id)
        
        tz = await self._generate_ai_response(
            chat_id=chat_id,
            prompts=[
                await self.get_project_description_prompt()
            ],
            dialog_history=dialog_history
        )

        project.description = tz

        logger.debug(f"Save project description: {tz}")

        await self.save_project(
            chat_id=chat_id,
            project=project
        )

    async def _extract_project_params(
        self, chat_id: str
    ) -> ProjectSchema:
        """Извлекаем параметры проекта из сообщения"""
        project_params_json = await self._generate_ai_response(
            chat_id=chat_id, 
            prompts=[
                await self.get_project_promt(chat_id=chat_id)
            ]
        )

        try:
            project_params = json.loads(project_params_json)
        except json.decoder.JSONDecodeError:
            logger.error(
                f"Ошибка json.decoder.JSONDecodeError для json: {project_params_json}"
            )
            project_params = {}

        project_schema = ProjectSchema(**project_params)

        await self.save_project(
            chat_id=chat_id, project=project_schema
        )
    
    async def _generate_ai_response(
        self, 
        chat_id: str,
        prompts: List[str],
        dialog_history: Optional[DialogSchema] = None
    ) -> str:
        if not dialog_history:
            dialog_history = await self.get_chat_history(chat_id=chat_id)

        system_messages = [MessageSchema(
            role="system",
            content=prompt,
        ) for prompt in prompts]

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

    async def send_message(
        self, 
        chat_id: str, 
        text: str, 
        files: List[Dict] = [],
    ) -> Tuple[str, ProjectSchema]:
        """Основной метод обработки сообщений
        
        chat_id: идентификатор чата
        text: текст сообщения
        files: [{
            "blob": BytesIO,
            "extension": расширение файла(.pdf, .doc|.docx, .xlsx)
        }]
        """

        if files:
            extract_messages: List[MessageSchema] = []

            for file in files:
                file_blob = file["blob"]
                file_extension = file["extension"]

                if file_extension == "pdf":
                    pdf_text = file_to_text.pdf_to_text(file_blob)

                    extract_messages.append(
                        MessageSchema(
                            role="user",
                            content=pdf_text
                        )
                    )
                elif file_extension == "docx" or file_extension == "doc":
                    docx_text = file_to_text.doc_to_text(file_blob)

                    extract_messages.append(
                        MessageSchema(
                            role="user",
                            content=docx_text
                        )
                    )
                elif file_extension == "xlsx":
                    xlsx_text = file_to_text.xlsx_to_text(file_to_text)

                    extract_messages.append(
                        MessageSchema(
                            role="user",
                            content=xlsx_text
                        )
                    )

            if extract_messages:
                await self._extract_project_description_param(
                    chat_id=chat_id, dialog_history=DialogSchema(
                        messages=extract_messages
                    )
                )

        message = MessageSchema(
            role="user",
            content=text if text else "Мне необходимо сделать программу по ТЗ"
        )

        await self.append_chat_history(
            chat_id=chat_id,
            message=message
        )

        answer = await self._generate_ai_response(
            chat_id=chat_id,
            prompts=[
                await self.get_dialog_promt(chat_id=chat_id)
            ],
        )

        await self.append_chat_history(
            chat_id=chat_id,
            message=MessageSchema(
                role="assistant",
                content=answer,
            )
        )

        await self._extract_project_params(chat_id=chat_id)
        
        project_schema = await self.get_project(chat_id=chat_id)

        return answer, project_schema
