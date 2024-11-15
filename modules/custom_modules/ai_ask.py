import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix

# API URLs
URL = "https://deliriussapi-oficial.vercel.app/ia"
GEMINIIMG_URL = "https://bk9.fun/ai/geminiimg"
COPILOT_URL = "https://itzpire.com/ai/bing-ai?model=Precise&q="
NEW_GEMINI_URL = "http://api-samirxz.onrender.com/Gemini-apu?text={query}&cookies=g.a000pgh-Mrk9f_o_PmDDsd5jqe48F2tjbUfXAY8kLdMsy0BGH3_b_6N4EaP-L7niFTV6Y1RmTwACgYKAZkSARISFQHGX2Mi_JfXzcVDskOHkOr_h50tRRoVAUF8yKrr6eIQN9_Bo8S_t8Z5e7yr0076"

async def fetch_response(url: str, query: str, message: Message, response_key: str, reply=False):
    """Fetch the response from the API and send it back to the user."""
    response_msg = await message.reply("Thinking...") if reply else await message.edit("Thinking...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        response_text = data.get(response_key, "No answer found.")
        
        response_content = f"**Question:**\n{query}\n**Answer:**\n{response_text}"
        
        if reply:
            await response_msg.edit_text(response_content, parse_mode=enums.ParseMode.MARKDOWN)
        else:
            await message.edit(response_content, parse_mode=enums.ParseMode.MARKDOWN)

    except requests.exceptions.RequestException:
        await response_msg.edit_text("An error occurred, please try again later.") if reply else await message.edit("An error occurred, please try again later.")

@Client.on_message(filters.command(["gpt", "chatgpt"], prefix))
async def gptweb(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `gpt <query>`")
        return
    query = " ".join(message.command[1:])
    url = f"{URL}/gptweb?text={query}"
    await fetch_response(url, query, message, 'gpt', reply=not message.from_user.is_self)

@Client.on_message(filters.command(["gemini"], prefix))
async def gemini(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `gemini <query>`")
        return
    query = " ".join(message.command[1:])
    url = f"{URL}/gemini?query={query}"
    await fetch_response(url, query, message, 'message', reply=not message.from_user.is_self)

@Client.on_message(filters.command(["describe"], prefix))
async def describe_image(client, message: Message):
    # Check if the message is a valid reply to an image
    if not (message.reply_to_message and message.reply_to_message.photo):
        response_text = "Reply to an image and provide a prompt. Usage: `describe <prompt>`"
        # Edit the bot's own message or send a reply based on the user
        if message.from_user.is_self:
            await message.edit(response_text)
        else:
            await message.reply(response_text)
        return

    # Extract the prompt or default to "what is it"
    prompt = " ".join(message.command[1:]).strip() or "Get details of given image, be as accurate as possible."

    # Inform about the image downloading process
    download_message = await (message.edit("<code>Umm, lemme analyze...</code>") if message.from_user.is_self else message.reply("Downloading image..."))
    
    # Download the image
    photo_path = await client.download_media(message.reply_to_message.photo.file_id)

    try:
        # Upload the image to x0.at
        upload_response = requests.post("https://x0.at", files={"file": open(photo_path, "rb")})
        upload_response.raise_for_status()
        image_url = upload_response.text.strip()

        # Request the description from the Gemini image description API
        url = f"{GEMINIIMG_URL}?url={image_url}&q={prompt}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        description = data.get("BK9", "No description found.")
        response_content = f"**Prompt:** {prompt}\n**Description:** {description}"

        # Edit the appropriate message with the result
        await download_message.edit(response_content, parse_mode=enums.ParseMode.MARKDOWN)

    except requests.exceptions.RequestException:
        await download_message.edit("Failed to process the image. Please try again later.")
    except ValueError:
        await download_message.edit("Invalid response received from the API.")
    finally:
        os.remove(photo_path)  # Clean up the downloaded image file


@Client.on_message(filters.command(["copilot"], prefix))
async def copilot(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `copilot <query>`")
        return
    query = " ".join(message.command[1:])
    url = f"{COPILOT_URL}{query}"
    await fetch_response(url, query, message, 'result', reply=not message.from_user.is_self)

@Client.on_message(filters.command(["ai", "gm"], prefix))
async def gemini_image(client, message: Message):
    if len(message.command) < 2:
        await message.reply("Usage: `ai <query>`")
        return
    query = " ".join(message.command[1:])
    url = NEW_GEMINI_URL.format(query=query)
    response_msg = await message.reply("<code>Umm, lemme think...</code>") if not message.from_user.is_self else await message.edit("<code>Umm, lemme think...</code>")

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        response_text = data.get("text", "No answer found.")
        images = data.get("images", [])

        response_content = f"**Question:**\n{query}\n**Answer:**\n{response_text}"
        
        if not message.from_user.is_self:
            await response_msg.edit_text(response_content, parse_mode=enums.ParseMode.MARKDOWN)
            if images and images[0]:
                await message.reply_photo(images[0], caption=f"Prompt: {query}")
        else:
            await message.edit(response_content, parse_mode=enums.ParseMode.MARKDOWN)
            if images and images[0]:
                await message.reply_photo(images[0], caption=f"<b>Prompt:</b> <code>{query}</code>")

    except requests.exceptions.RequestException:
        await response_msg.edit_text("Error: Unable to retrieve data. Please try again later.") if not message.from_user.is_self else await message.edit("Error: Unable to retrieve data. Please try again later.")
    except ValueError:
        await response_msg.edit_text("Error: Received an invalid response format.") if not message.from_user.is_self else await message.edit("Error: Received an invalid response format.")

modules_help["ask"] = {
    "gpt [query]*": "Ask anything to GPT-Web",
    "chatgpt [query]*": "Ask anything to GPT-Web",
    "gemini [query]*": "Ask anything to Gemini",
    "describe [image_url] [query]*": "Describe an image with a query",
    "copilot [query]*": "Ask anything to Copilot AI",
    "ai [query]*": "Ask anything to Gemini web",
    }
