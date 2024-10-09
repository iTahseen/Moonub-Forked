import asyncio
import requests
from urllib.parse import parse_qs, urlparse

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_module_help, format_exc


def get_song_name(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    song_name = query_params.get("n", [""])[0].replace("%20", " ")
    return song_name


@Client.on_message(filters.command(["spdl"], prefix) & filters.me)
async def sdl(_, message: Message):
    try:
        if not len(message.command) > 1 and not message.reply_to_message:
            await message.edit(
                format_module_help("sdl"),
                parse_mode=enums.ParseMode.HTML,
            )
            return

        spoti_query = (
            message.text.split(maxsplit=1)[1]
            if len(message.command) > 1
            else message.reply_to_message.text.split("\n")[0]
        )

        m = await message.edit("<b>Downloading...</b>", parse_mode=enums.ParseMode.HTML)

        url = "https://spotify-mp3-downloader.vercel.app/get_download_link?search="
        search_query = spoti_query.replace(" ", "%20")
        response = requests.get(url + search_query)
        if response.status_code == 200:
            download_link = response.json()["download_link"]
            song_name = get_song_name(download_link)
            await message.reply_audio(download_link, caption=f"<b>{song_name}</b>")
            await asyncio.sleep(0.5)
            await m.delete()
        else:
            await m.edit("API request was unsuccessful.")
    except Exception as e:
        await m.edit(f"<b>Spotify-Download error:</b>\n{format_exc(e)}")


modules_help["spotify_dl"] = {
    "spdl [query]*": "Download Spotify music through API",
}
