 
from pyrogram import Client, filters, enums
from pyrogram.types import Message
import aiohttp
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+ required

from utils.misc import modules_help, prefix

# GeoNames API credentials
GEO_API_USERNAME = "tahseen"
# OpenWeatherMap API credentials
WEATHER_API_KEY = "3ec738bcb912c44a805858054ead1efd"
# Default city
DEFAULT_CITY = "Los Angeles"

async def fetch_json(url: str, params: dict) -> dict:
    """Fetch JSON data from a URL with provided parameters."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, params=params) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            return {"error": str(e)}

async def get_coordinates(city_name: str):
    """Get the coordinates (latitude, longitude) for a given city name."""
    search_url = "http://api.geonames.org/searchJSON"
    params = {
        'q': city_name,
        'username': GEO_API_USERNAME,
        'maxRows': 1
    }
    data = await fetch_json(search_url, params)
    if 'geonames' in data and data['geonames']:
        return data['geonames'][0]['lat'], data['geonames'][0]['lng']
    return None, None

async def get_city_time(city_name: str = DEFAULT_CITY) -> str:
    """Get the current time for a given city."""
    lat, lng = await get_coordinates(city_name)
    if not lat or not lng:
        return "<b>Error:</b> <i>City not found or invalid city name.</i>"

    time_url = "http://api.geonames.org/timezoneJSON"
    params = {'username': GEO_API_USERNAME, 'lat': lat, 'lng': lng}
    data = await fetch_json(time_url, params)
    
    if 'timezoneId' in data:
        timezone = ZoneInfo(data['timezoneId'])
        city_time = datetime.now(timezone)
        local_time = city_time.strftime('%Y-%m-%d %H:%M:%S')
        weekday = city_time.strftime('%A')
        return (
            f"<b>Current Time in {city_name}:</b>\n"
            f"<i>Local Time:</i> {local_time}\n"
            f"<i>Weekday:</i> {weekday}\n"
            f"<i>Time Zone:</i> {data['timezoneId']}"
        )
    return "<b>Error:</b> <i>Unable to get time for the specified coordinates.</i>"

async def get_weather(city_name: str = DEFAULT_CITY) -> str:
    """Get the current weather for a given city."""
    weather_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': city_name, 'appid': WEATHER_API_KEY, 'units': 'metric'}
    data = await fetch_json(weather_url, params)
    
    if 'weather' in data and 'main' in data:
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description']
        wind_speed = data['wind']['speed']
        return (
            f"<b>Weather in {city_name}:</b>\n"
            f"<i>Temperature:</i> {temp}°C\n"
            f"<i>Feels Like:</i> {feels_like}°C\n"
            f"<i>Humidity:</i> {humidity}%\n"
            f"<i>Description:</i> {description.capitalize()}\n"
            f"<i>Wind Speed:</i> {wind_speed} m/s"
        )
    return "<b>Error:</b> <i>Unable to get weather for the specified city.</i>"

@Client.on_message(filters.command("time", prefix))
async def time_command(client: Client, message: Message):
    """Handle the time command to show the current time for a city."""
    city_name = message.reply_to_message.text if message.reply_to_message else None
    if not city_name:
        args = message.text.split(maxsplit=1)
        city_name = args[1] if len(args) > 1 else DEFAULT_CITY

    result = await get_city_time(city_name)
    
    if message.from_user.is_self:
        await message.edit(result, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply(result, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command("weather", prefix))
async def weather_command(client: Client, message: Message):
    """Handle the weather command to show the current weather for a city."""
    city_name = message.reply_to_message.text if message.reply_to_message else None
    if not city_name:
        args = message.text.split(maxsplit=1)
        city_name = args[1] if len(args) > 1 else DEFAULT_CITY

    result = await get_weather(city_name)
    
    if message.from_user.is_self:
        await message.edit(result, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply(result, parse_mode=enums.ParseMode.HTML)

# Module help descriptions
modules_help["time"] = {
    "time [city_name]": "Shows the current time.",
    "weather [city_name]": "Shows the current weather detail."
}