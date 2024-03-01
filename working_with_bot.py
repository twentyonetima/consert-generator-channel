from aiogram import Bot
from aiogram.types import FSInputFile

bot_token = os.environ.get('BOT_TOKEN')

bot = Bot(token=bot_token)
domain = os.environ.get("DOMAIN")


async def format_caption_for_channel(response_data, user_data):
    compain_id = response_data["data"]["compain"]["id"]
    if user_data["concert_city"] == 'Москва':
        caption = 'Москва | 29 февраля | Pravda club\n\n' + 'Билеты: ' + domain + f'compain_id={compain_id}&city=moscow'
    else:
        caption = 'Санкт-Петербург | 28 января | Ласточка\n\n' + 'Билеты: ' + domain + f'compain_id={compain_id}&city=saint-petersburg'
    return caption


async def send_photo_to_channel(channel_id, response_data, user_data):

    # Send a message to the channel
    photo_path = './static/send_group_photo.jpg'
    caption = await format_caption_for_channel(response_data, user_data)

    # Send the photo to the channel
    message = await bot.send_photo(chat_id=-channel_id, photo=FSInputFile(photo_path), caption=caption)
    return message.message_id


async def pin_channel_message(channel_id, message_id):
    await bot.pin_chat_message(chat_id=-channel_id, message_id=message_id)
