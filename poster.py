from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import config
from app import dp
from loader import bot

user_keyboard = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text="О нас"),
        KeyboardButton(text="Инструкция")
    ],
    [
        KeyboardButton(text="Разместить пост")
    ],
    [
        KeyboardButton(text="Перейти в канал"),
        KeyboardButton(text="Поддержка")
    ]
], resize_keyboard=True)

support_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Ответить", callback_data="answer_support"),
        InlineKeyboardButton(text="Отклонить", callback_data="cancel_support")
    ]
])

cancel_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ]
])

confirmation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Отправить", callback_data="confirm"),
        InlineKeyboardButton(text="Отмена", callback_data="cancel")
    ]
])

publish_post = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Принять", callback_data="accept"),
        InlineKeyboardButton(text="Отклонить", callback_data="cancel_post")
    ]
])


@dp.message_handler(CommandStart(), user_id=config.ADMIN)  # Приветственное сообщение для модератора.
async def admin_panel(message: types.Message):
    await message.answer(
        "Приветствую! Вы являетесь модератором бота. К вам будут приходить объявления, которые вы можете принять или отклонить. В случае одобрения, данное сообщение опубликуется в вашем канале. В случае отказа, вы можете оставить комментарий, который отправится отправителю объявления.",
        reply_markup=user_keyboard
    )


@dp.message_handler(CommandStart())  # Приветственное сообщение для пользователя.
async def start_user(message: types.Message):
    await message.answer('Приветствую! Нажмите "Инструкция" для получения инструкции.', reply_markup=user_keyboard)


@dp.message_handler(text="О нас")  # Ответ на нажатие кнопки "О нас".
async def send_info(message: types.Message):
    await message.answer("""
В рамках создания и разработки крупнейшего частного социально-экономического информационного проекта Республики Ингушетия представляем: 
•	"ingprofi" - бот, позволяющий специалистам всех возможных сфер услуг заявить о себе;
•	vprofi.ingushetia - канал, в котором бот публикует пост (размещает анкету), предложенный специалистом.
Задачи проекта:
- формирование базы специалистов для дальнейшего размещения на сайте сервиса;
- оказание помощи клиентам в поиске специалистов.
    """)


@dp.message_handler(text="Инструкция")  # Ответ на нажатие кнопки "Инструкция"
async def send_instruction(message: types.Message):
    await message.answer("""
Для того чтобы опубликовать объявление нажмите "Разместить пост".
Вы должны заполнить 5 полей для ответов, которые вам будет присылать бот, после чего ваше объявление отправится на проверку.
Модератор проверит ваш пост и, в случае одобрения, опубликует его в канале. Он также вправе отклонить пост.
После решения модератора вам придет оповещение.
Если хотите связаться с нами, нажмите "Поддержка".
    """)


@dp.message_handler(text="Перейти в канал")  # Ответ на нажатие кнопки "Перейти в канал". Бот присылает ссылку на канал.
async def go_to_channel(message: types.Message):  # Бот присылает ссылку на канал.
    link = "https://t.me/vprofi_ingushetia"
    await message.answer(f"Перейдите по данной ссылке: {link}")


@dp.message_handler(text="Поддержка")  # Ответ на нажатие кнопки "Поддержка". Бот просит пользователя ввести вопрос.
async def support(message: types.Message, state: FSMContext):  # Бот просит пользователя ввести вопрос.
    await message.answer("Введите свой вопрос", reply_markup=cancel_keyboard)
    await state.set_state("support")


@dp.message_handler(state="support")
async def send_to_support(message: types.Message, state: FSMContext):  # Бот пересылает сообщение модератору
    await message.answer("Ваше сообщение было успешно отправлено модератору. Ожидайте ответа.")
    await bot.send_message(
        chat_id=config.ADMIN,
        text=f"{message.from_user.id}$$$\nПришло сообщение от пользователя {message.from_user.full_name}:\n\n{message.text}",
        reply_markup=support_keyboard
    )
    await state.reset_state()


@dp.callback_query_handler(
    text="cancel_support")  # Ответ на нажатие кнопки "Отклонить". Т. е., модератор не хочет отвечать на вопрос пользователя.
async def cancel_support(call: types.CallbackQuery):
    await call.answer(text="Вы отклонили сообщение.", show_alert=True)
    await call.message.edit_reply_markup()


@dp.callback_query_handler(text="answer_support")  # Ответ на нажатие кнопки "Ответить"
async def answer_to_support(call: types.CallbackQuery,
                            state: FSMContext):  # Бот просит модератора ввести ответ на вопрос пользователя
    text = call.message.text
    user_id = text.split("$$$")[0]
    await call.message.answer('Если вы передумали, введите "Отклонить".\nВведите ответ. ')
    await call.message.edit_reply_markup()
    await state.update_data({"user_id": user_id})
    await state.set_state("send_answer")


@dp.message_handler(state="send_answer", text="Отклонить")  # Пользователь ввел "Отклонить"
async def cancel_answer_to_support(message: types.Message, state: FSMContext):
    await message.answer("Вы отклонили сообщение.")
    await state.reset_state()


@dp.message_handler(state="send_answer")
async def send_answer_to_support(message: types.Message,
                                 state: FSMContext):  # Бот пересылает ответ модератора пользователю
    data = await state.get_data()
    user_id = data.get("user_id")
    await message.answer(f"Ваш ответ был успешно отправлен пользователю.")
    await bot.send_message(chat_id=int(user_id), text=f"Модератор ответил на ваше сообщение:\n\n{message.text}.")
    await state.reset_state()


@dp.callback_query_handler(text="cancel", state="*")  # Ответ на нажатие кнопки "Отмена".
async def cancel(call: types.CallbackQuery, state: FSMContext):  # Бот выходит из всех состояний.
    await call.answer(text="Отмена", show_alert=True)
    await call.message.edit_reply_markup()
    await state.reset_state()


@dp.message_handler(text="Разместить пост")  # Ответ на нажатие кнопки "Разместить пост".
async def get_name(message: types.Message, state: FSMContext):
    await message.answer("1. Введите свое имя.", reply_markup=cancel_keyboard)
    await state.set_state("get_name")


@dp.message_handler(state="get_name")
async def get_specialization(message: types.Message, state: FSMContext):
    await message.answer("2. Введите свою специализацию.", reply_markup=cancel_keyboard)
    await state.update_data({"user_name": message.text})
    await state.set_state("get_specialization")


@dp.message_handler(state="get_specialization")
async def get_town(message: types.Message, state: FSMContext):
    await message.answer("3. Введите свой населенный пункт.", reply_markup=cancel_keyboard)
    await state.update_data({"user_specialization": message.text})
    await state.set_state("get_town")


@dp.message_handler(state="get_town")
async def get_organization(message: types.Message, state: FSMContext):
    await message.answer('4. Введите организацию, к которой вы относитесь. Если ее нет, введите "Нет".',
                         reply_markup=cancel_keyboard)
    await state.update_data({"user_town": message.text})
    await state.set_state("get_organization")


@dp.message_handler(state="get_organization")
async def get_phone_number(message: types.Message, state: FSMContext):
    await message.answer("5. Введите свой номер телефона.", reply_markup=cancel_keyboard)
    await state.update_data({"user_organization": message.text})
    await state.set_state("get_phone_number")


@dp.message_handler(state="get_phone_number")
async def get_text(message: types.Message, state: FSMContext):
    await message.answer("6. Введите текст объявления.", reply_markup=cancel_keyboard)
    await state.update_data({"user_phone_number": message.text})
    await state.set_state("get_text")


@dp.message_handler(state="get_text")
async def get_text(message: types.Message, state: FSMContext):  # Подтверждение отправки поста на проверку
    await message.answer(f"Вы действительно хотите отправить его на проверку?", reply_markup=confirmation_keyboard)
    await state.update_data({"user_text": message.text})
    await state.set_state("confirmation_post")


@dp.callback_query_handler(text="confirm", state="confirmation_post")
async def confirm_post(call: types.CallbackQuery, state: FSMContext):  # Отправка поста
    data = await state.get_data()
    user_name = data.get("user_name")
    user_specialization = data.get("user_specialization")
    user_town = data.get("user_town")
    user_organization = data.get("user_organization")
    user_phone_number = data.get("user_phone_number")
    user_text = data.get("user_text")
    await call.answer()
    await call.message.answer("Ваш пост успешно отправлен на проверку.")
    await bot.send_message(chat_id=config.ADMIN, text=f"""
{call.from_user.id}$$$    
    
Пост пользователя {call.from_user.full_name}:

1. Имя: {user_name}
2. Специализация: {user_specialization}
3. Населенный пункт: {user_town}
4. Организация: {user_organization}
5. Номер телефона: {user_phone_number}
6. Текст объявления:
{user_text}

#{user_specialization} #{user_town}
    """, reply_markup=publish_post)
    await state.reset_state()


@dp.callback_query_handler(text="cancel_post")  # Ответ на кнопку "Отклонить".
async def cancel_post(call: types.CallbackQuery, state: FSMContext):
    text = call.message.text.split("$$$")
    user_id = text[0]
    post = text[1]
    await call.message.answer('Введите причину отклонения. Если не хотите указывать причину, введите "Нет".')
    await call.message.edit_reply_markup()
    await state.update_data({"user_id": user_id, "post": post})
    await state.set_state("send_cause_cancel")


@dp.message_handler(state="send_cause_cancel")
async def send_cause_cancel(message: types.Message, state: FSMContext): # Отклонение поста, отправка оповещания пользователю.
    data = await state.get_data()
    user_id = data.get("user_id")
    if message.text.lower() == "нет":
        await message.answer(f"Вы отклонили пост.")
        await bot.send_message(chat_id=int(user_id), text=f"Ваш пост был отклонен.")
    else:
        await message.answer(f"Вы отклонили пост по причине: {message.text}")
        await bot.send_message(chat_id=int(user_id), text=f"Ваш пост был отклонен по причине: {message.text}")
    await state.reset_state()


@dp.callback_query_handler(text="accept") # Ответ на кнопку "Принять"
async def send_post_to_channel(call: types.CallbackQuery): # Публикуем пост в канале, отправляем пользователю оповещание о том, что его пост опубликовали.
    text = call.message.text.split("$$$")
    user_id = text[0]
    post = text[1]
    await call.answer(text="Вы опубликовали пост", show_alert=True)
    await bot.send_message(chat_id=config.CHANNEL, text=post)
    await bot.send_message(chat_id=user_id, text="Ваш пост был опубликован")
    await call.message.edit_reply_markup()
