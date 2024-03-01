import os

from aiogram import types, F, Router
from aiogram.enums import ChatType
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods.export_chat_invite_link import ExportChatInviteLink
from aiogram import Bot
from dotenv import load_dotenv

from ext import volonter_text, help_text
from working_with_group import create_or_check_group_chat
from request_methods import post_user_request, update_user_request
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')

router = Router()
concert_cities = ["Санкт-Петербург", "Москва", "Екатеринбург"]
residence_cities = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань", "Нижний Новгород", "Челябинск", "Самара",
    "Уфа", "Ростов-на-Дону", "Омск", "Красноярск", "Воронеж", "Пермь", "Волгоград", "Краснодар", "Тюмень", "Саратов"
]


def is_valid_city(text: str, cities) -> bool:
    return text.lower() in map(str.lower, cities)


class OrderConcert(StatesGroup):
    choosing_concert_city = State()
    choosing_residence_city = State()


@router.message(Command("help"))
async def help_command(message: types.Message):
    photo_path = './static/help_photo.jpg'

    # Send the photo with a caption
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=help_text,
        # parse_mode=ParseMode.MARKDOWN  # You can adjust the parse mode accordingly
    )


@router.message(Command("volonter"))
async def volonter_command(message: types.Message):
    photo_path = './static/volonter_photo.jpg'

    # Send the photo with a caption
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=volonter_text,
        # parse_mode=ParseMode.MARKDOWN  # You can adjust the parse mode accordingly
    )


async def setup_bot_commands(bot):
    bot_commands = [
        types.BotCommand(command="/start", description="start bot to find group"),
        types.BotCommand(command="/help", description="Get info about me"),
        types.BotCommand(command="/volonter", description="Get info about volonter")
    ]
    await bot.set_my_commands(bot_commands)


@router.message(Command("start"))
async def cmd_concert(message: Message, state: FSMContext):
    if message.chat.type == ChatType.GROUP or message.chat.type == ChatType.SUPERGROUP:
        # Don't show the /start command in groups
        return

    await help_command(message)

    kb = [
        [types.KeyboardButton(text="Санкт-Петербург")],
        [types.KeyboardButton(text="Москва")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )
    await message.answer("Выберете город концерта?", reply_markup=keyboard)
    await state.set_state(OrderConcert.choosing_concert_city)
    username = message.from_user.username
    await post_user_request(username)


@router.message(StateFilter("OrderConcert:choosing_concert_city"), F.text.in_(concert_cities))
async def concert_city_chosen(message: Message, state: FSMContext):
    selected_city = next((city for city in concert_cities if city.lower() == message.text.lower()), None)
    await state.update_data(concert_city=selected_city)
    await message.answer(f"Ваш город концерта - {selected_city}")

    # Now, ask for the city of residence
    kb = [
        (types.KeyboardButton(text=residence_cities[i]), types.KeyboardButton(text=residence_cities[i + 1]))
        for i in range(0, len(residence_cities), 2)
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите способ подачи"
    )
    await message.answer("Выберете город проживания?", reply_markup=keyboard)

    await state.set_state(OrderConcert.choosing_residence_city)


@router.message(StateFilter("OrderConcert:choosing_residence_city"), F.text.in_(residence_cities))
async def residence_city_chosen(message: Message, state: FSMContext):
    selected_city = next((city for city in residence_cities if city.lower() == message.text.lower()), None)
    await state.update_data(residence_city=selected_city)
    user_data = await state.get_data()

    username = message.from_user.username

    await update_user_request(username, user_data['residence_city'], user_data['concert_city'])

    chat_invite_link = await create_or_check_group_chat(user_data=user_data, username=username)

    await volonter_command(message)

    await message.answer(f"Ваш город проживания - {user_data['residence_city']}."
                         f" Ваш город концерта - {user_data['concert_city']}."
                         f" Ссылка на чат: {chat_invite_link.link}",
                         reply_markup=ReplyKeyboardRemove())

