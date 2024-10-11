import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

URL = "https://deliriusapi-official.vercel.app/ia"
GEMINIIMG_URL = "https://bk9.fun/ai/geminiimg"
COPILOT_URL = "https://itzpire.com/ai/bing-ai?model=Precise&q="  # Copilot API URL

def clean_data(data):
    """Clean up the data received from the Blackbox API."""
    parts = data.split("$@$")
    return parts[-1] if len(parts) > 1 else data

async def fetch_response(url: str, query: str, message: Message, response_key: str):
    """Fetch the response from the API and send it back to the user."""
    await message.edit("Thinking...")
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        response_text = data.get(response_key, "No answer found.")
        await message.edit(
            f"**Question:**\n{query}\n**Answer:**\n{response_text}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["gpt", "chatgpt"], prefix) & filters.me)
async def gptweb(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `gpt <query>`")
        return
    
    query = " ".join(message.command[1:])
    url = f"{URL}/gptweb?text={query}"
    await fetch_response(url, query, message, 'gpt')

@Client.on_message(filters.command(["gemini"], prefix) & filters.me)
async def gemini(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `gemini <query>`")
        return
    
    query = " ".join(message.command[1:])
    url = f"{URL}/gemini?query={query}"
    await fetch_response(url, query, message, 'message')

@Client.on_message(filters.command(["describe"], prefix) & filters.me)
async def describe_image(_, message: Message):
    if len(message.command) < 3:
        await message.edit("Usage: `describe <image_url> <query>`")
        return
    
    image_url = message.command[1]
    query = " ".join(message.command[2:])
    url = f"{GEMINIIMG_URL}?url={image_url}&q={query}"
    await fetch_response(url, query, message, 'BK9')

@Client.on_message(filters.command(["copilot"], prefix) & filters.me)
async def copilot(_, message: Message):
    if len(message.command) < 2:
        await message.edit("Usage: `copilot <query>`")
        return
    
    query = " ".join(message.command[1:])
    url = f"{COPILOT_URL}{query}"
    await fetch_response(url, query, message, 'result')

modules_help["sarethai"] = {
    "gpt [query]*": "Ask anything to GPT-Web",
    "chatgpt [query]*": "Ask anything to GPT-Web",
    "gemini [query]*": "Ask anything to Gemini",
    "describe [image_url] [query]*": "Describe an image with a query",
    "copilot [query]*": "Ask anything to Copilot AI",
}
