import json
import requests
import os
import time

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import progress

@Client.on_message(filters.command(["spotify", "sdl"], prefix) & filters.me)
async def spotify_download(client: Client, message: Message):
    chat_id = message.chat.id
    query = (message.text.split(maxsplit=1)[1].strip() 
             if len(message.command) > 1 else message.reply_to_message.text.strip() 
             if message.reply_to_message else None)
    
    if not query:
        await message.edit(f"<b>Usage:</b> <code>{prefix}spotify [song name]</code>")
        return

    status_msg = await message.edit_text(f"<code>Searching for {query} on Spotify...</code>")
    
    try:
        response = requests.get(f"https://api.nyxs.pw/dl/spotify-direct?title={query}")
        response.raise_for_status()
        result = response.json()
        
        if result["status"] and "result" in result:
            song = result["result"]
            song_name = song["title"]
            artist = song["artists"]
            song_url = song["url"]
            thumb_url = song["thumbnail"]
            
            await status_msg.edit_text(f"<code>Found: {song_name} by {artist}</code>\nDownloading...")
            
            thumb_path = f"{song_name}.jpg"
            song_path = f"{song_name}.mp3"

            # Download thumbnail and song
            with open(thumb_path, "wb") as thumb_file:
                thumb_file.write(requests.get(thumb_url).content)
            with open(song_path, "wb") as song_file:
                song_file.write(requests.get(song_url).content)

            await status_msg.edit_text(f"<code>Uploading {song_name}...</code>")
            c_time = time.time()
            caption = f"<b>Song Name:</b> {song_name}\n<b>Artist:</b> {artist}"

            await client.send_audio(chat_id, song_path, caption=caption, progress=progress,
                                    progress_args=(status_msg, c_time, f"`Uploading {song_name}...`"), thumb=thumb_path)
            await status_msg.delete()
            
            # Clean up files
            os.remove(thumb_path)
            os.remove(song_path)
        else:
            await status_msg.edit_text(f"<code>No results found for {query}</code>")

    except requests.RequestException as e:
        await status_msg.edit_text(f"<code>Error: {e}</code>")

modules_help["spotify"] = {
    "spotify": "search, download, and upload songs from Spotify",
    "sdl": "search, download, and upload songs from Spotify",
}
