import aiohttp

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user import User
from src.database.models.neiro import NeiroResponse

from src.filters.user import UserFilter

from src.keyboards import neiro as neiro_keyboards
from src.keyboards import menu as menu_keyboards

from src.states import neirochat as neiro_states
from src.callbacks import ActionCallback, ActionDataCallback

from src.utils.neiro import neiro_chat

router = Router(name="neirochat")
router.message.filter(UserFilter())
router.callback_query.filter(UserFilter())


@router.callback_query(ActionCallback.filter(F.action == "generate_text_choice_model"))
async def gen_text(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        text="Пожалуйста выберите модель для генерации текста.",
        reply_markup=neiro_keyboards.gen_text_choice_model
    )


@router.callback_query(ActionDataCallback.filter(F.action == "generate_text"))
async def gen_text(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext):
    model = callback_data.data

    await state.update_data(
        model=model
    )

    text = f"Вы выбрали модель: {model}\n\n"

    await call.message.delete()
    await call.message.answer(
        text=text + "Начните диалог. Чтобы остановить диалог нажмите на клавиатуре ниже 'Главное меню'",
        reply_markup=menu_keyboards.back_in_menu
    )

    await state.set_state(neiro_states.NeiroChatStates.waiting_for_text_prompt)


@router.message(neiro_states.NeiroChatStates.waiting_for_text_prompt)
async def waiting_text_message(message: Message, session: AsyncSession, state: FSMContext):
    state_data = await state.get_data()
    
    model = state_data.get("model")
    prompt = message.text

    user: User = await User.get(
        session=session,
        user_id=message.from_user.id
    )

    if user.daily_text_limit < 1.4:
        await message.answer(
            text="К сожалению ваш дневной лимит текстовых запросов исчерпан!",
            reply_markup=menu_keyboards.back_in_menu
        )
        return
    
    if model == "hydra-gemini":
        subtracting_responces = 1 # Сколько запросов надо вычесть
    else:
        subtracting_responces = 1.4

    user.daily_text_limit = user.daily_text_limit - subtracting_responces

    neiro_answer, total_tokens = await neiro_chat.send_message(
        chat_id=message.from_user.id,
        prompt=prompt,
    )

    await NeiroResponse.create(
        session=session,
        user=user,
        type="text",
        prompt=prompt,
        content=neiro_answer,
        total_tokens=total_tokens,
        model=model
    )

    await session.commit()
    await session.refresh(user)

    available_responses = round(user.daily_text_limit)

    await message.answer(
        text=f"""
<b> Сейчас вам доступно {available_responses} запросов.
Ответ нейросети: </b>

{neiro_answer}
""",
        reply_markup=menu_keyboards.back_in_menu,
    )


@router.callback_query(ActionCallback.filter(F.action == "generate_image_choice_model"))
async def choice_model(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text="Выберите модель:",
        reply_markup=neiro_keyboards.gen_img_choice_model
    )


@router.callback_query(ActionDataCallback.filter(F.action == "generate_image"))
async def generate_image(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext):
    model = callback_data.data

    await state.update_data(
        model=model
    )

    text = f"Вы выбрали модель: {model}\n\n"

    await call.message.answer(text+"Введите ваш промпт для изображения: ")

    await state.set_state(neiro_states.NeiroChatStates.waiting_for_image_prompt)


@router.message(neiro_states.NeiroChatStates.waiting_for_image_prompt)
async def image_gen(message: Message, session: AsyncSession, state: FSMContext):
    state_data = await state.get_data()

    model = state_data.get("model")
    prompt = message.text

    user: User = await User.get(
        session=session,
        user_id=message.from_user.id
    )

    if user.daily_image_limit < 1.4:
        await message.answer(
            text="К сожалению ваш дневной лимит запросов изображений исчерпан!",
            reply_markup=menu_keyboards.back_in_menu
        )
        return

    neiro_answer, total_tokens = await neiro_chat.send_message(
        chat_id=message.from_user.id,
        prompt=prompt,
        is_image=True
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(neiro_answer) as resp:
            img_bytes = await resp.read()

    await NeiroResponse.create(
        session=session,
        user=user,
        type="image",
        prompt=prompt,
        content=neiro_answer,
        total_tokens=total_tokens
    )
    
    if model == "flux.1-schnell":
        subtracting_responces = 1 # Сколько запросов надо вычесть
    else:
        subtracting_responces = 1.4
    
    user.daily_image_limit = user.daily_image_limit - subtracting_responces

    await session.commit()
    await session.refresh(user)

    available_responses = round(user.daily_image_limit)

    await message.answer_photo(
        caption=f"Поздравляем, вы создали изображение! Сейчас вам доступно: <b>{available_responses}</b> запросов!",
        photo=BufferedInputFile(file=img_bytes, filename="img.jpg"),
        reply_markup=menu_keyboards.back_in_menu,
    )

# rulers 80
