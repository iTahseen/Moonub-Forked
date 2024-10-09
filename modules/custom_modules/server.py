import os
import shutil
import tempfile
import psutil
import platform
import sys
import subprocess
from pyrogram import Client, filters, enums
from pyrogram.types import Message
from utils.misc import modules_help, prefix

# Function to clean up temporary files and cache
def cleanup_temp_files():
    try:
        # Define common directories for temporary files and cache
        temp_dirs = [tempfile.gettempdir(), "/tmp", "/var/tmp"]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                os.makedirs(temp_dir, exist_ok=True)

        # Additional cleanup for cache (Example: system-specific paths)
        # Cache directories can vary based on system and applications
        cache_dirs = ["/var/cache", "/home/username/.cache"]  # Adjust as needed
        for cache_dir in cache_dirs:
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir, ignore_errors=True)
                os.makedirs(cache_dir, exist_ok=True)

        return "Temporary files and cache have been cleaned up successfully."

    except Exception as e:
        return f"An error occurred during cleanup: {str(e)}"

@Client.on_message(filters.command("server", prefix) & filters.me)
async def server_info(client: Client, message: Message):
    # Edit the command message to show "Please wait..."
    edit_message = await message.edit("Fetching server information, please wait...")

    # Gather server information
    memory_info = psutil.virtual_memory()
    disk_info = psutil.disk_usage('/')
    cpu_info = psutil.cpu_percent(interval=1)  # Take a 1-second interval for a more accurate CPU usage
    network_info = psutil.net_io_counters()
    uptime_seconds = int(psutil.time.time() - psutil.boot_time())
    uptime = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {(uptime_seconds % 60)}s"
    
    # Temperature Sensors (if available)
    temp_info = psutil.sensors_temperatures()
    cpu_temp = temp_info.get('coretemp', [])[0].current if 'coretemp' in temp_info else "N/A"
    
    # System Load Average
    load_avg = os.getloadavg()
    
    # Top Processes
    top_processes = sorted(
        [(p.info['pid'], p.info['name'], p.info['cpu_percent'], p.info['memory_info'].rss)
         for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info'])],
        key=lambda x: x[2], reverse=True
    )[:5]

    # Python Environment Information
    python_version = platform.python_version()
    
    # Get installed packages
    def get_installed_packages():
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=subprocess.PIPE, text=True)
            return result.stdout.strip().split('\n')
        except Exception as e:
            return [str(e)]
    
    python_libs = get_installed_packages()
    
    # System Users
    users = psutil.users()
    
    # Format information
    info = (
        f"**Server Information**\n\n"
        f"**Memory Usage:**\n"
        f"  - Total: {memory_info.total / (1024 ** 3):.2f} GB\n"
        f"  - Available: {memory_info.available / (1024 ** 3):.2f} GB\n"
        f"  - Used: {memory_info.used / (1024 ** 3):.2f} GB\n"
        f"  - Percent Used: {memory_info.percent}%\n\n"
        
        f"**Disk Usage:**\n"
        f"  - Total: {disk_info.total / (1024 ** 3):.2f} GB\n"
        f"  - Used: {disk_info.used / (1024 ** 3):.2f} GB\n"
        f"  - Free: {disk_info.free / (1024 ** 3):.2f} GB\n"
        f"  - Percent Used: {disk_info.percent}%\n\n"
        
        f"**CPU Usage:**\n"
        f"  - Current: {cpu_info}%\n"
        f"  - Temperature: {cpu_temp} °C\n\n"
        
        f"**Network Statistics:**\n"
        f"  - Bytes Sent: {network_info.bytes_sent / (1024 ** 2):.2f} MB\n"
        f"  - Bytes Received: {network_info.bytes_recv / (1024 ** 2):.2f} MB\n\n"
        
        f"**System Load Average:**\n"
        f"  - 1 Minute: {load_avg[0]}\n"
        f"  - 5 Minutes: {load_avg[1]}\n"
        f"  - 15 Minutes: {load_avg[2]}\n\n"
        
        f"**Top Processes by CPU Usage:**\n"
        + "\n".join([f"  - PID: {p[0]}, Name: {p[1]}, CPU: {p[2]}%, Memory: {p[3] / (1024 ** 2):.2f} MB" for p in top_processes]) + "\n\n"
        
        f"**Python Environment:**\n"
        f"  - Version: {python_version}\n"
        f"  - Libraries:\n" + "\n".join([f"    - {lib}" for lib in python_libs]) + "\n\n"
        
        f"**System Users:**\n"
        + "\n".join([f"  - User: {user.name}, Terminal: {user.terminal}, Host: {user.host}" for user in users]) + "\n\n"
        
        f"**Uptime:**\n"
        f"  - {uptime}"
    )

    # Edit the command message with the final information
    await edit_message.edit(info, parse_mode=enums.ParseMode.MARKDOWN)

@Client.on_message(filters.command("cleanup", prefix) & filters.me)
async def cleanup(client: Client, message: Message):
    # Edit the command message to show "Cleaning up, please wait..."
    edit_message = await message.edit("Cleaning up temporary files and cache, please wait...")

    result = cleanup_temp_files()
    
    # Edit the command message with the cleanup status
    await edit_message.edit(result)

modules_help["server_info"] = {
    "server": "Get detailed server information.",
    "cleanup": "Clean up temporary files and cache.",
}
