import json
import os
from pathlib import Path
import re
import subprocess
import sys
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from info import Config, Txt

# Define the config path
config_path = Path("config.json")

@Client.on_message(filters.private & filters.chat(Config.SUDO) & filters.command('make_config'))
async def make_config(bot: Client, msg: Message):
    try:
        if config_path.exists():
            return await msg.reply_text(
                text="**You have already made a config. First delete it then you'll be able to make a new config.**\n\n Use /del_config",
                reply_to_message_id=msg.id
            )

        while True:
            try:
                n = await bot.ask(text=Txt.SEND_NUMBERS_MSG, chat_id=msg.chat.id, filters=filters.text, timeout=60)
            except Exception:
                await bot.send_message(msg.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /make_config", reply_to_message_id=msg.id)
                return

            try:
                target = await bot.ask(text=Txt.SEND_TARGET_CHANNEL, chat_id=msg.chat.id, filters=filters.text, timeout=60)
            except Exception:
                await bot.send_message(msg.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /make_config", reply_to_message_id=msg.id)
                return

            if str(n.text).isnumeric():
                if not re.match(r'^[\w.-]+$', target.text):
                    break
                else:
                    await msg.reply_text(text="⚠️ **Please send a valid target channel link or username!**", reply_to_message_id=target.id)
                    continue
            else:
                await msg.reply_text(text="⚠️ **Please send an integer number, not a string!**", reply_to_message_id=n.id)
                continue

        group_target_id = target.text
        gi = re.sub("(@)|(https://)|(http://)|(t.me/)", "", group_target_id)

        try:
            await bot.get_chat(gi)
        except Exception as e:
            return await msg.reply_text(text=f"{e} \n\nError!", reply_to_message_id=target.id)

        config = {
            "Target": gi,
            "accounts": []
        }

        for _ in range(int(n.text)):
            try:
                session = await bot.ask(text=Txt.SEND_SESSION_MSG, chat_id=msg.chat.id, filters=filters.text, timeout=60)
            except Exception:
                await bot.send_message(msg.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /make_config", reply_to_message_id=msg.id)
                return

            if config_path.exists():
                for account in config['accounts']:
                    if account['Session_String'] == session.text:
                        return await msg.reply_text(text=f"**{account['OwnerName']} account already exists in config. You can't add the same account multiple times 🤡**\n\n Error!")

            try:
                process = subprocess.Popen(
                    ["python", "login.py", gi, session.text],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.communicate()
                return_code = process.wait()

                if return_code == 0:
                    output_string = stdout.decode('utf-8').replace('\r\n', '\n')
                    AccountHolder = json.loads(output_string)
                else:
                    return await msg.reply_text('**Something went wrong. Kindly check your inputs to ensure they are filled out correctly!**')
            except Exception as err:
                await bot.send_message(msg.chat.id, text=f"<b>ERROR :</b>\n<pre>{err}</pre>")
                return

            new_account = {
                "Session_String": session.text,
                "OwnerUid": AccountHolder['id'],
                "OwnerName": AccountHolder['first _name']
            }
            config["accounts"].append(new_account)

            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=4)

        acocunt_btn = [
            [InlineKeyboardButton(text='Accounts You Added', callback_data='account_config')]
        ]
        await msg.reply_text(text=Txt.MAKE_CONFIG_DONE_MSG.format(n.text), reply_to_message_id=n.id, reply_markup=InlineKeyboardMarkup(acocunt_btn))

    except Exception as e:
        print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)


@Client.on_message(filters.private & filters.chat(Config.SUDO) & filters.command('see_accounts'))
async def see_account(bot: Client, msg: Message):
    try:
        config = json.load(open("config.json"))['accounts']
        acocunt_btn = [
            [InlineKeyboardButton(text='Accounts You Added', callback_data='account_config')]
        ]
        await msg.reply_text(text=Txt.ADDED_ACCOUNT.format(len(config)), reply_to_message_id=msg.id, reply_markup=InlineKeyboardMarkup(acocunt_btn))

    except Exception:
        return await msg.reply_text(text="**You don't have any added accounts 0️⃣**\n\nUse /make_config to add accounts 👥", reply_to_message_id=msg.id)