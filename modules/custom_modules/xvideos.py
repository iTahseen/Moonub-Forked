 
import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from io import BytesIO
import asyncio

from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# Function to perform video search using the provided API
def video_search(query):
    url = f'https://api-aswin-sparky.koyeb.app/api/search/xvideos?search={requests.utils.quote(query)}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('status') and isinstance(data.get('data'), list):
            return data.get('data')
    return None

# Function to get video download link using the provided API
def get_video_download_link(video_url):
    url = f'https://api-aswin-sparky.koyeb.app/api/downloader/xdl?url={requests.utils.quote(video_url)}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get('status'):
            return data.get('data')
    return None

# Dictionary to store search results
search_results = {}

@Client.on_message(filters.command(["xvideos", "xvid"], prefix) & filters.me)
async def video_search_command(client, message: Message):
    try:
        # Check if the command is a reply to another message
        if message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        else:
            command_parts = message.text.split(' ', 1)
            if len(command_parts) < 2:
                await message.reply_text("Please provide a search query after the command or reply to a message containing the search query.")
                return
            query = command_parts[1]

        results = video_search(query)
        if not results:
            await message.reply_text("No results found.")
            return

        # Edit the original command message to "Please wait..."
        await message.edit_text("Please wait...")

        result_text = f"**Video Search Results for:** _{query}_\n\n"
        for i, result in enumerate(results[:15]):  # Limit to 15 results
            result_text += (f"{i+1}. **{result.get('title', 'Unknown')}**\n"
                            f"Duration: {result.get('duration', 'Unknown')}\n"
                            f"[Watch Video]({result.get('url', '#')})\n\n")

        # Store search results with message id as key
        search_results[message.chat.id] = {i+1: result.get('url', '') for i, result in enumerate(results)}

        # Update the message with search results
        result_message = await message.edit_text(result_text, parse_mode=enums.ParseMode.MARKDOWN)
        
        # Schedule deletion of the message and cleanup of the search results
        await asyncio.sleep(60)
        await result_message.delete()
        
        # Remove search results entry if it exists
        search_results.pop(message.chat.id, None)
    
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

@Client.on_message(filters.reply & filters.me)
async def download_video(client, message: Message):
    try:
        if message.reply_to_message and message.reply_to_message.text:
            chat_id = message.chat.id
            if chat_id in search_results:
                try:
                    selected_number = int(message.text.strip())
                except ValueError:
                    return  # Ignore invalid video numbers

                if selected_number in search_results[chat_id]:
                    video_url = search_results[chat_id][selected_number]
                    download_link = get_video_download_link(video_url)
                    if download_link:
                        # Edit the video number message to "Please wait..."
                        await message.edit_text("Please wait...")

                        # Download the video
                        response = requests.get(download_link)
                        if response.status_code == 200:
                            video_data = BytesIO(response.content)
                            video_data.name = f"{selected_number}.mp4"

                            # Upload the video to Telegram
                            await client.send_video(
                                chat_id=message.chat.id,
                                video=video_data,
                                caption=""  # Remove the caption
                            )

                        # Delete the "Please wait..." message after sending the video
                        await message.delete()
                    else:
                        await message.reply_text("Failed to get the download link.")
                else:
                    await message.reply_text("Invalid video number.")
    
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

modules_help["xvideos"] = {
    "xvideos [search query]": "Searches and downloads videos",
    "xvid [search query]": "Searches and downloads videos",
}
