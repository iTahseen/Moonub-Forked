import json
import requests
import time
import os

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import progress

@Client.on_message(filters.command(["spotify", "sp"], prefix) & filters.me)
async def spotify_search(client: Client, message: Message):
    chat_id = message.chat.id
    if len(message.command) > 1:
        query = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        query = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}spotify [song name to search & download|upload]</code>"
        )
        return
    
    ms = await message.edit_text(f"<code>Searching for {query} on Spotify...</code>")
    search_url = f"https://deliriusapi-official.vercel.app/search/spotify?q={query}"
    response = requests.get(search_url)
    
    if response.status_code != 200:
        await ms.edit_text(f"<code>Failed to search for {query} on Spotify.</code>")
        return
    
    result = response.json()
    
    if result['status'] and result['data']:
        # Get the first song result
        song_details = result['data'][0]
        song_name = song_details['title']
        song_url = song_details['url']
        song_image = song_details['image']
        
        await ms.edit_text(f"<code>Found: {song_name} </code>\nDownloading...")

        # Download song using the new Spotify downloader API
        download_url = f"https://deliriusapi-official.vercel.app/download/spotifydl?url={song_url}"
        download_response = requests.get(download_url)
        
        if download_response.status_code != 200:
            await ms.edit_text(f"<code>Failed to download {song_name} from Spotify.</code>")
            return
        
        download_data = download_response.json()
        
        if download_data['status']:
            song_download_url = download_data['data']['url']
            song_author = download_data['data']['author']
            song_image = download_data['data']['image']
            song_cover = download_data['data']['cover']
            
            # Download song thumbnail
            with open(f"{song_name}.jpg", "wb") as f:
                f.write(requests.get(song_image).content)
            
            # Download song
            song = requests.get(song_download_url)
            with open(f"{song_name}.mp3", "wb") as f:
                f.write(song.content)
            
            await ms.edit_text(f"<code>Uploading {song_name}... </code>")
            c_time = time.time()
            
            # Upload the song with details
            await client.send_audio(
                chat_id, 
                f"{song_name}.mp3", 
                caption=f"<b>Song Name:</b> {song_name}\n<b>Artist:</b> {song_author}", 
                progress=progress, 
                progress_args=(ms, c_time, f'`Uploading {song_name}...`'), 
                thumb=f"{song_name}.jpg"
            )
            await ms.delete()
            
            # Clean up local files
            if os.path.exists(f"{song_name}.jpg"):
                os.remove(f"{song_name}.jpg")
            if os.path.exists(f"{song_name}.mp3"):
                os.remove(f"{song_name}.mp3")
        else:
            await ms.edit_text(f"<code>Failed to download {song_name}.</code>")
    else:
        await ms.edit_text(f"<code>No results found for {query} on Spotify.</code>")

modules_help["spotify"] = {
    "spotify [song name]": "Search, download, and upload songs from Spotify."
}
