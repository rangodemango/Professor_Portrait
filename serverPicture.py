import random
import discord
from discord.ext import commands, tasks
from PIL import Image, ExifTags
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants
IMAGE_DIRECTORY = './img'
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

# Check if the directory is empty, if so, notify the user and exit the application
if not os.listdir(IMAGE_DIRECTORY):
    print("The 'img' directory is empty. Please add image files to continue.")
    exit()  # This line will terminate the script

# Get the bot token from an environment variable
GUILD_ID = int(os.getenv('GUILD_ID'))
CHANNEL_NAME = '🤖┃teacher-of-the-day'
EMOJIS = ['🍎', '🕍', '📚', '🏫', '🎓', '📖', '🛰', '📝', '🤡', '💼', '🧟', '🔩']

# Initialize the bot
intents = discord.Intents.default()
client = commands.Bot(command_prefix='!', intents=intents)

def get_image_list():
    """Get a list of image paths from the specified directory."""
    return [
        os.path.join(IMAGE_DIRECTORY, filename)
        for filename in os.listdir(IMAGE_DIRECTORY)
        if os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS
    ]

def correct_image_orientation(filename):
    """Correct the image orientation using EXIF data."""
    with Image.open(filename) as img:
        exif = img._getexif()
        if exif is not None:
            exif = dict(exif.items())
            orientation = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
            orientation_value = exif.get(orientation)
            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
            img.save(filename)
            img.close()

async def send_announcement_message(guild, teacher_name):
    """Send a message to the specified channel with the teacher's name."""
    channel = discord.utils.get(guild.text_channels, name=CHANNEL_NAME)
    if channel:
        random_emoji = random.choice(EMOJIS)
        await channel.send(f"Today's featured teacher is: {teacher_name} {random_emoji}")

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    change_icon.start()

@tasks.loop(hours=24)
async def change_icon():
    guild = client.get_guild(GUILD_ID)
    if guild:
        image_list = get_image_list()
        if not image_list:  # Check if the image list is empty
            print("No images found in the 'img' directory.")
            return  # Exit the task if there are no images
        image_path = random.choice(image_list)
        correct_image_orientation(image_path)
        with open(image_path, 'rb') as f:
            await guild.edit(icon=f.read())
            print(f"Icon changed for {guild.name}")

            name_parts = os.path.basename(image_path).split('.')[0].split('_')
            if name_parts:
                name_parts[0] = name_parts[0].capitalize()
                name_parts[-1] = name_parts[-1].capitalize()
            teacher_name = ' '.join(name_parts)

            await send_announcement_message(guild, teacher_name)
    else:
        print("Guild not found.")
