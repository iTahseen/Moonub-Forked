from asyncio import sleep
from pyrogram import Client, filters, enums
from pyrogram.raw import functions
from pyrogram.types import Message, InputReplyToMessage
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# Define the available actions with their corresponding chat actions
commands = {
    'ftype': enums.ChatAction.TYPING,
    'faudio': enums.ChatAction.UPLOAD_AUDIO,
    'fvideo': enums.ChatAction.UPLOAD_VIDEO,
    'fphoto': enums.ChatAction.UPLOAD_PHOTO,
    'fdocument': enums.ChatAction.UPLOAD_DOCUMENT,
    'flocation': enums.ChatAction.FIND_LOCATION,
    'frvideo': enums.ChatAction.RECORD_VIDEO,
    'frvoice': enums.ChatAction.RECORD_AUDIO,
    'frvideor': enums.ChatAction.RECORD_VIDEO_NOTE,
    'fvideor': enums.ChatAction.UPLOAD_VIDEO_NOTE,
    'fgame': enums.ChatAction.PLAYING,
    'fcontact': enums.ChatAction.CHOOSE_CONTACT,
    'fstop': 'stop',  # special handling for stop
    'fscrn': 'screenshot'
}

active_action = False  # Flag to track if an action is currently active

@Client.on_message(filters.command(list(commands), prefix) & filters.me)
async def fakeactions_handler(client: Client, message: Message):
    global active_action
    cmd = message.command[0]
    action = commands.get(cmd)

    # If 'fstop' command is triggered, stop ongoing actions
    if cmd == 'fstop':
        active_action = False
        await message.delete()
        return

    # Parse the duration (default to 1 if invalid)
    try:
        sec = int(message.command[1]) if len(message.command) > 1 else 1
    except ValueError:
        sec = 1  # Default to 1 second if an invalid duration is provided

    # Delete the original command message
    await message.delete()

    if action == 'screenshot':
        # Special handling for screenshot action
        if message.reply_to_message:
            for _ in range(sec):
                if not active_action:  # If stopped, break out of the loop
                    break
                await client.invoke(
                    functions.messages.SendScreenshotNotification(
                        peer=await client.resolve_peer(message.chat.id),
                        reply_to=InputReplyToMessage(reply_to_message_id=message.reply_to_message.id),
                        random_id=client.rnd_id(),
                    )
                )
                await sleep(1)
        else:
            await client.send_message('me', "Error: 'fscrn' requires a reply to a message.")
    else:
        # Handle other chat actions for the specified duration
        active_action = True
        end_time = sec
        while end_time > 0 and active_action:
            await client.send_chat_action(chat_id=message.chat.id, action=action)
            await sleep(5)  # Resend every 5 seconds
            end_time -= 5

    # Reset action state when the duration is complete or action is stopped
    active_action = False

# Module help documentation for each command
modules_help['fakeactions'] = {
    'ftype [sec]': 'Typing... action',
    'faudio [sec]': 'Uploading audio... action',
    'fvideo [sec]': 'Uploading video... action',
    'fphoto [sec]': 'Uploading photo... action',
    'fdocument [sec]': 'Uploading document... action',
    'flocation [sec]': 'Finding location... action',
    'frvideo [sec]': 'Recording video... action',
    'frvoice [sec]': 'Recording voice... action',
    'frvideor [sec]': 'Recording round video... action',
    'fvideor [sec]': 'Uploading round video... action',
    'fgame [sec]': 'Playing game... action',
    'fcontact [sec]': 'Sending contact... action',
    'fstop': 'Stop any ongoing actions',
    'fscrn [sec] [reply_to_message]*': 'Simulate screenshot action (requires reply to a message)',
}
