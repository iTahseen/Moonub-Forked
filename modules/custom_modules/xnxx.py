 
import requests
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InputMediaPhoto
from io import BytesIO
import asyncio

from utils.misc import modules_help, prefix
from utils.scripts import format_exc

# Function to perform video search using the provided API
def video_search(query):
    try:
        url = f'https://www.samirxpikachu.run.place/xnxx/search?query={requests.utils.quote(query)}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
    except Exception as e:
        print(f"Error in video_search: {e}")
    return None

# Function to get video download link using the provided API
def get_video_download_link(video_url):
    try:
        url = f'https://www.samirxpikachu.run.place/xnxx/down?url={requests.utils.quote(video_url)}'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if 'url' in data:
            return data['url'], data.get('thumb', None)
    except Exception as e:
        print(f"Error in get_video_download_link: {e}")
    return None, None

# Dictionary to store search results
search_results = {}

@Client.on_message(filters.command(["xnxx", "xnvid"], prefix) & filters.me)
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
                            f"Views: {result.get('views', 'Unknown')}\n"
                            f"Quality: {result.get('quality', 'Unknown')}\n"
                            f"[Watch Video]({result.get('link', '#')})\n\n")

        # Store search results with message id as key
        search_results[message.chat.id] = {i+1: result for i, result in enumerate(results)}

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
                    result = search_results[chat_id][selected_number]
                    video_url = result.get('link', '')
                    thumbnail_url = result.get('thumb', '')

                    download_link, _ = get_video_download_link(video_url)
                    if download_link:
                        # Edit the video number message to "Please wait..."
                        await message.edit_text("Please wait...")

                        # Download the video
                        response = requests.get(download_link)
                        response.raise_for_status()
                        video_data = BytesIO(response.content)
                        video_data.name = f"{selected_number}.mp4"

                        # Download the thumbnail
                        thumbnail_data = None
                        if thumbnail_url:
                            thumb_response = requests.get(thumbnail_url)
                            if thumb_response.status_code == 200:
                                thumbnail_data = BytesIO(thumb_response.content)
                                thumbnail_data.name = "thumbnail.jpg"

                        # Upload the video to Telegram
                        await client.send_video(
                            chat_id=message.chat.id,
                            video=video_data,
                            thumb=thumbnail_data,
                            caption=result.get('title', '')  # Use the video title as the caption
                        )

                        # Delete the "Please wait..." message after sending the video
                        await message.delete()
                    else:
                        await message.reply_text("Failed to get the download link.")
                else:
                    await message.reply_text("Invalid video number.")
    
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

modules_help["xnxx"] = {
    "xnxx [search query]": "Searches and downloads videos",
    "xnvid [search query]": "Searches and downloads videos",
}
