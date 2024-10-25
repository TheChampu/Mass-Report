from pyrogram import Client, filters
import os
from info import Config

# Function to add a SUDO user
@Client.on_message(filters.command("add_sudo") & filters.user(Config.OWNER))  # Only allow the owner to add SUDO users
def add_sudo(client, message):
    # Check if a user ID was provided
    if len(message.command) < 2:
        message.reply("Please provide a user ID to add as SUDO.")
        return

    user_id = message.command[1]
    
    try:
        user_id = int(user_id)  # Convert to integer
    except ValueError:
        message.reply("Invalid user ID. Please provide a valid integer user ID.")
        return

    # Update the SUDO list
    if user_id not in Config.SUDO:
        Config.SUDO.append(user_id)
        
        # Optionally, update the environment variable or save to a config file
        os.environ["SUDO"] = " ".join(map(str, Config.SUDO))  # Update the environment variable
        
        message.reply(f"User  ID {user_id} has been added to SUDO users.")
    else:
        message.reply(f"User  ID {user_id} is already a SUDO user.")