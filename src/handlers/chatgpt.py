import io

from loguru import logger

from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from src.database.models.user import User, NeiroResponse

from src.keyboards import chatgpt as chatgpt_keyboards
from src.keyboards import menu as menu_keyboards

from src.states import neirochat as chatgpt_states
from src.callbacks import ActionCallback, ActionDataCallback

from src.utils.chatgpt import chatgpt

router = Router(name="neirochat")


@router.callback_query(ActionCallback.filter(F.action == "generate_text_choice_model"))
async def gen_text(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        text="Пожалуйста выберите модель для генерации текста.",
        reply_markup=chatgpt_keyboards.gen_text_choice_model
    )


@router.callback_query(ActionDataCallback.filter(F.action == "generate_text"))
async def gen_text(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext):
    data = callback_data.data

    if data == "gpt-4-turbo":
        text = "Вы выбрали модель: gpt-4-turbo\n\n"
    elif data == "gpt-4":
        text = "Вы выбрали модель: gpt-4\n\n"

    await call.message.delete()
    await call.message.answer(
        text=text + "Начните диалог с chatGPT. Чтобы остановить диалог нажмите на клавиатуре ниже 'Остановить'",
        reply_markup=chatgpt_keyboards.stop_chat
    )

    await state.set_state(chatgpt_states.NeiroChatStates.waiting_for_text_prompt)


@router.message(chatgpt_states.NeiroChatStates.waiting_for_text_prompt)
async def waiting_text_message(message: Message, state: FSMContext):
    text = message.text

    if text == "Остановить":
        await state.clear()
        await message.answer(
            "Вы остановили диалог с ботом! Нажмите чтобы перейти в главное меню",
            reply_markup=menu_keyboards.back_in_menu
        )
        return

    neiro_answer = await chatgpt.send_message(
        chat_id=message.from_user.id,
        text=text,
    )

    if isinstance(neiro_answer, str):
        await message.answer(
            text=neiro_answer
        )
    elif isinstance(neiro_answer, bytes):
        await message.answer_photo(
            photo=BufferedInputFile(file=neiro_answer, filename="img.jpg"),
            parse_mode=None
        )

    user = await User.get(user_id=message.from_user.id)

    await NeiroResponse.create(
        user_id=user.id,
        prompt=text,
        msg_type="text"
    )


@router.callback_query(ActionCallback.filter(F.action == "generate_image_choice_model"))
async def choice_model(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        text="Выберите модель:",
        reply_markup=chatgpt_keyboards.gen_img_choice_model
    )


@router.callback_query(ActionDataCallback.filter(F.action == "generate_image"))
async def generate_image(call: CallbackQuery, callback_data: ActionDataCallback, state: FSMContext):
    data = callback_data.data

    if data == "hydro-gemini":
        text = "Вы выбрали модель: hydro-gemini\n\n"
    elif data == "flux.1-schnell":
        text = "Вы выбрали модель: flux.1-schnell\n\n"

    await call.message.answer(text+"Введите ваш промпт для изображения: ")

    await state.set_state(chatgpt_states.NeiroChatStates.waiting_for_image_prompt)


@router.message(chatgpt_states.NeiroChatStates.waiting_for_image_prompt)
async def image_gen(message: Message, state: FSMContext):
    text = message.text

    neiro_answer = await chatgpt.send_message(
        chat_id=message.from_user.id,
        text=text,
        is_image=True
    )

    if isinstance(neiro_answer, str):
        await message.answer(
            text=neiro_answer
        )
    elif isinstance(neiro_answer, bytes):
        await message.answer_photo(
            caption="Поздравляем, вы создали изображение!",
            photo=BufferedInputFile(file=neiro_answer, filename="img.jpg"),
            reply_markup=menu_keyboards.back_in_menu,
        )
    
    user = await User.get(user_id=message.from_user.id)

    await NeiroResponse.create(
        user_id=user.id,
        prompt=text,
        msg_type="img"
    )

# rulers 80
