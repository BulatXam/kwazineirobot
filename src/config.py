from pathlib import Path

from aiogram.types import BotCommand
from pydantic import field_validator
from pydantic_settings import BaseSettings


class ChatGPTConfig(BaseSettings):
    TOKEN: str

    class Config:
        env_prefix = 'CHATGPT_'
        env_file = '.env'
        extra = 'ignore'


class ProjConfig(BaseSettings):
    DATA_DIR: Path = Path(__file__).parent / 'data'
    STATIC_DIR: Path =  DATA_DIR / "static"
    MEDIA_DIR: Path =  DATA_DIR / "media"

    class Config:
        env_prefix = 'PROJ_'
        env_file = '.env'
        extra = 'ignore'


class BotConfig(BaseSettings):
    TOKEN: str
    ADMINS: list[int] | None = []
    COMMANDS: list[BotCommand] = [
        BotCommand(
            command='start',
            description='Меню'
        )
    ]
    ADMIN_COMMANDS: list[BotCommand] = [
        BotCommand(
            command='admin',
            description='Админ-Панель'
        )
    ]

    class Config:
        env_prefix = 'BOT_'
        env_file = '.env'
        extra = 'ignore'

    @field_validator('ADMINS', mode='before')
    def split_admins(cls, v):
        try:
            return [int(admin_id) for admin_id in str(v).split(',')]

        except Exception as e:
            raise ValueError('ADMINS value must be int,int,int')


class PostgresConfig(BaseSettings):
    NAME: str
    HOST: str
    PORT: int
    PASSWORD: str
    USER: str

    @property
    def URL(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"

    class Config:
        env_prefix = 'POSTGRES_'
        env_file = '.env'
        extra = 'ignore'


class RedisConfig(BaseSettings):
    NAME: str
    HOST: str
    PORT: int
    PASSWORD: str
    USER: str

    class Config:
        env_prefix = 'REDIS_'
        env_file = '.env'
        extra = 'ignore'

    @property
    def URL(self) -> str:
        return f"redis://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


class Config:
    psql = PostgresConfig()
    redis = RedisConfig()
    bot = BotConfig()
    proj = ProjConfig()
    chatgpt = ChatGPTConfig()


cnf = Config()
