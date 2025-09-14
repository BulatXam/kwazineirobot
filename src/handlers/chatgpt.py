from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.keyboards import chatgpt as chatgpt_keyboards

from src.states import neirochat as neirochat_states

router = Router(name="neirochat")


@router.message(F.text == "📝 Сгенерировать текст")
async def gen_text(message: Message, state: FSMContext):
    await message.answer(
        text="Пожалуйста выберите модель для генерации текста.",
        reply_markup=chatgpt_keyboards.gen_text_choice_model
    )


@router.callback_query(F.data.startswith() == "generate_text")
async def gen_text(call: CallbackQuery, state: FSMContext):
    pass


@router.message(neirochat_states.NeiroChatStates.waiting_for_text_prompt)
async def handle_text_prompt(message: Message, state: FSMContext):
    user_prompt = message.text

    # Здесь должна быть логика генерации текста с помощью ИИ
    generated_text = f"Сгенерированный текст на основе вашего запроса: {user_prompt}"

    await message.answer(
        text=generated_text
    )
    user = await User.get(user_id=message.from_user.id)
    await GeneratedText.create(
        author=user,
        prompt=user_prompt,
        content=generated_text
    )

    await state.clear()


@router.message(F.text == "🖼️ Сгенерировать изображение")
async def gen_image(message: Message, state: FSMContext):
    await message.answer(
        text="🖼️ Пожалуйста, введите текстовый запрос для генерации изображения с помощью искусственного интеллекта."
    )

    await state.set_state(neirochat_states.NeiroChatStates.waiting_for_image_prompt)


@router.message(neirochat_states.NeiroChatStates.waiting_for_image_prompt)
async def handle_image_prompt(message: Message, state: FSMContext):
    user_prompt = message.text

    # Здесь должна быть логика генерации изображения с помощью ИИ
    # Для демонстрации мы просто отправим заглушку
    image_file = FSInputFile(
        STATIC_DIR / "404.jpg",
        filename="generated_image.png"
    )

    try:
        await message.answer_photo(
            photo=image_file,
            caption=f"Сгенерированное изображение на основе вашего запроса: {user_prompt}"
        )
        user = await User.get(user_id=message.from_user.id)
        await GeneratedImage.create(
            author=user,
            prompt=user_prompt,
            image_path=STATIC_DIR / "404.jpg"
        )
    except TelegramBadRequest as e:
        await message.answer(
            text="Произошла ошибка при отправке изображения. Пожалуйста, попробуйте снова."
        )

    await state.clear()

# rulers 80
