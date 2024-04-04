import serverPicture
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get the bot token from an environment variable
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

if __name__ == "__main__":
    serverPicture.client.run(TOKEN)
