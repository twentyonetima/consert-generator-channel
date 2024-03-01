from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.types import InputChannel
from telethon.sessions import StringSession

from request_methods import post_find_group, post_group_create
from working_with_bot import send_photo_to_channel, pin_channel_message

domain = os.environ.get("DOMAIN")
api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")
name = os.environ.get("NAME_SESSION")
group_title_photo = './static/group_title_photo.jpg'
send_channel_photo = './static/send_group_photo.jpg'
bot_admin_id = os.environ.get("BOT_ADMIN_ID")


async def create_or_check_group_chat(user_data, username, name=name):
    status_post_find_group = await post_find_group(city_from=user_data['residence_city'], city_to=user_data['concert_city'])
    success = status_post_find_group.get('success', False)
    if success:
        data = status_post_find_group.get('data', {})
        if data:
            group_name = data.get('group_name', '')
            async with TelegramClient(name, api_id, api_hash, system_version="4.16.30-vxCUSTOM") as client:
                result = client(functions.messages.AddChatUserRequest(
                    chat_id=int(group_name), user_id=f'@{username}', fwd_limit=1_000_000
                ))
                functions.channels.TogglePreHistoryHiddenRequest(
                    channel=-int(group_name),
                    enabled=False
                )
                group_chat_id = int(group_name)
                chat_invite_link = await client(functions.messages.ExportChatInviteRequest(group_chat_id))
                return chat_invite_link
        else:
            async with TelegramClient(name, api_id=api_id, api_hash=api_hash,
                                      system_version="4.16.30-vxCUSTOM") as client:
                if user_data['concert_city'] == 'Санкт-Петербург':
                    title = "Панкмодернисты | " + user_data['residence_city'] + " -> СПб | 28.01.24"
                else:
                    title = "Панкмодернисты | " + user_data['residence_city'] + " -> МСК | 29.02.24"
                result = await client(functions.channels.CreateChannelRequest(
                    title=title,
                    about="about channel",
                    megagroup=True
                ))

                channel_id = result.chats[0].id
                group_title_upload_response = await client.upload_file(group_title_photo)

                await client(functions.channels.EditPhotoRequest(
                    channel=channel_id,
                    photo=types.InputChatUploadedPhoto(
                        file=group_title_upload_response
                    )
                ))

                print(f"Channel created with ID: {channel_id}")

                await client(functions.channels.InviteToChannelRequest(
                    channel=channel_id,
                    users=[f'@{username}', '@ConcertniyBot', '@bezintima'],
                ))

                await client(functions.channels.EditAdminRequest(
                    channel=channel_id,
                    user_id=bot_admin_id,
                    admin_rights=types.ChatAdminRights(
                        post_messages=True,
                        edit_messages=True,
                        delete_messages=True,
                        pin_messages=True,
                        change_info=True
                    ),
                    rank="Admin"
                ))

                print()

                response_data = await post_group_create(city_from=user_data['residence_city'],
                                                        city_to=user_data['concert_city'],
                                                        group_name=str(channel_id), username=username)

                send_channel_photo_upload_response = await client.upload_file(send_channel_photo)

                photo_message = await client(functions.messages.SendMediaRequest(
                    peer=channel_id,
                    media=types.InputMediaUploadedPhoto(
                        file=send_channel_photo_upload_response,
                    ),
                    message=await format_caption_for_channel(response_data, user_data),
                ))
                print()

                message_id = photo_message.updates[2].message.id

                print(message_id)
                a = await client.pin_message(entity=channel_id, message=message_id, notify=True)

                chat_invite_link = await client(functions.messages.ExportChatInviteRequest(channel_id))
                print(f"Channel invite link: {chat_invite_link.link}")
                return chat_invite_link


async def format_caption_for_channel(response_data, user_data):
    compain_id = response_data["data"]["compain"]["id"]
    if user_data["concert_city"] == 'Москва':
        caption = 'Москва | 29 февраля | Pravda club\n\n' + 'Билеты: ' + domain + f'compain_id={compain_id}&city=moscow'
    else:
        caption = 'Санкт-Петербург | 28 января | Ласточка\n\n' + 'Билеты: ' + domain + f'compain_id={compain_id}&city=saint-petersburg'
    return caption
