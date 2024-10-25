import json
from pathlib import Path
import subprocess
import sys
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from info import Config, Txt

config_path = Path("config.json")

async def load_config() -> dict:
    """Load the configuration from the JSON file."""
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        raise FileNotFoundError("Config file not found. Please create one using /make_config.")

async def save_config(new_config: dict):
    """Save the updated configuration to the JSON file."""
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(new_config, file, indent=4)

@Client.on_message(filters.private & filters.user(Config.SUDO) & filters.command('add_account'))
async def add_account(bot: Client, cmd: Message):
    try:
        config = await load_config()

        try:
            session = await bot.ask(text=Txt.SEND_SESSION_MSG, chat_id=cmd.chat.id, filters=filters.text, timeout=60)
        except Exception:
            await bot.send_message(cmd.from_user.id, "Error!!\n\nRequest timed out. Restart by using /make_config", reply_to_message_id=cmd.id)
            return

        ms = await cmd.reply_text('**Please Wait...**', reply_to_message_id=cmd.id)

        if any(account['Session_String'] == session.text for account in config['accounts']):
            return await ms.edit(text=f"**{account['OwnerName']} account already exists in config. You can't add the same account multiple times 🤡**")

        # Run a shell command and capture its output
        process = subprocess.Popen(
            ["python", "login.py", config['Target'], session.text],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()
        return_code = process.wait()

        if return_code == 0:
            output_string = stdout.decode('utf-8').replace('\r\n', '\n')
            AccountHolder = json.loads(output_string)
        else:
            error_message = stderr.decode('utf-8')
            print(f"Command failed with error: {error_message}")
            return await ms.edit('**Something went wrong. Kindly check your inputs!**')

        new_account = {
            "Session_String": session.text,
            "OwnerUid": AccountHolder['id'],
            "OwnerName": AccountHolder['first_name']
        }

        config['accounts'].append(new_account)
        await save_config(config)

        await ms.edit(text="**Account Added Successfully**\n\nClick the button below to view all the accounts you have added 👇.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Accounts You Added', callback_data='account_config')]]))

    except FileNotFoundError as e:
        await cmd.reply_text(str(e), reply_to_message_id=cmd.id)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

@Client.on_message(filters.private & filters.user(Config.SUDO) & filters.command('target'))
async def target(bot: Client, cmd: Message):
    try:
        config = await load_config()
        Info = await bot.get_chat(config['Target'])

        btn = [[InlineKeyboardButton(text='Change Target', callback_data='chgtarget')]]
        text = f"Channel Name: <code>{Info.title}</code>\nChannel Username: <code>@{Info.username}</code>\nChannel Chat Id: <code>{Info.id}</code>"

        await cmd.reply_text(text=text, reply_to_message_id=cmd.id, reply_markup=InlineKeyboardMarkup(btn))
    except FileNotFoundError as e:
        await cmd.reply_text(str(e), reply_to_message_id=cmd.id)
    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)

@Client.on_message(filters.private & filters.user(Config.SUDO) & filters.command('del_config'))
async def delete_config(bot: Client, cmd: Message):
    btn = [
        [InlineKeyboardButton(text='Yes', callback_data='delconfig-yes')],
        [InlineKeyboardButton(text='No', callback_data='delconfig-no')]
    ]

    await cmd.reply_text(text="**⚠️ Are you Sure?**\n\nYou want to delete the Config.", reply_to_message_id=cmd.id, reply_markup=InlineKeyboardMarkup(btn))