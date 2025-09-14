from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from src.database.models.user import User

from src.keyboards import menu as main_keyboards
from src.callbacks import ActionCallback


router = Router(name="main")


@router.message(
    F.text == "/start"
)
async def start(message: Message):
    user: User = await User.get(
        user_id=message.from_user.id
    )

    if not user:
        user: User = await User.create(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username,
        )

    await message.answer(
        text=f"""
<b>👋 Добро пожаловать в NeuroGenius!</b>

✨ <i>Я — твой личный помощник для генерации текстов и изображений с помощью искусственного интеллекта.</i>

❓ <i>Чтобы узнать больше, используй команду</i> <code>/help</code>

<pre>Твой уникальный ID в системе: #{user.id}</pre>
""",
        reply_markup=main_keyboards.menu,
    )


@router.callback_query(
    ActionCallback.filter(F.action == "start")
)
async def start(call: CallbackQuery):
    user: User = await User.get(
        user_id=call.from_user.id
    )

    if not user:
        user: User = await User.create(
            user_id=call.from_user.id,
            first_name=call.from_user.first_name,
            last_name=call.from_user.last_name,
            username=call.from_user.username,
        )

    try:
        await call.message.edit_text(
            text=f"""
<b>👋 Добро пожаловать в NeuroGenius!</b>

✨ <i>Я — твой личный помощник для генерации текстов и изображений с помощью искусственного интеллекта.</i>

❓ <i>Чтобы узнать больше, используй команду</i> <code>/help</code>

<pre>Твой уникальный ID в системе: #{user.id}</pre>
""",
            reply_markup=main_keyboards.menu,
        )
    except TelegramBadRequest:
        await call.message.delete()
        await call.message.answer(
            text=f"""
<b>👋 Добро пожаловать в NeuroGenius!</b>

✨ <i>Я — твой личный помощник для генерации текстов и изображений с помощью искусственного интеллекта.</i>

❓ <i>Чтобы узнать больше, используй команду</i> <code>/help</code>

<pre>Твой уникальный ID в системе: #{user.id}</pre>
""",
            reply_markup=main_keyboards.menu,
        )


@router.message(
    F.text == "/help"
)
async def help(message: Message):
    await message.answer(
        text="""
<b>📋 Справка по командам и возможностям NeuroGenius</b>

<code>/start</code> — начать работу с ботом
<code>/help</code> — показать это сообщение

<b>🧠 Как это работает?</b>
• Используй кнопки <code>📝 Сгенерировать текст</code> или <code>🖼️ Сгенерировать изображение</code>, чтобы указать тип задания.
• Или просто напиши запрос в чат — я постараюсь сам догадаться, что ты хочешь.
• Я обработаю запрос и отправлю тебе результат.

<b>⚡ Все твои запросы сохраняются для улучшения качества работы.</b>

<b>Жду твоего первого задания!</b>
""",
    )


# rulers 80
