from telegram import InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler
from time import sleep

from bot import download_dict, dispatcher, download_dict_lock, QB_SEED, SUDO_USERS, OWNER_ID
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper.message_utils import sendMessage, sendMarkup
from bot.helper.ext_utils.bot_utils import getDownloadByGid, MirrorStatus, getAllDownload
from bot.helper.telegram_helper import button_build


def cancel_mirror(update, context):
    args = update.message.text.split(" ", maxsplit=1)
    user_id = update.message.from_user.id
    if len(args) > 1:
        gid = args[1]
        dl = getDownloadByGid(gid)
        if not dl:
            return sendMessage(f"GID: <code>{gid}</code> ɴᴏᴛ ꜰᴏᴜɴᴅ.", context.bot, update.message)
    elif update.message.reply_to_message:
        mirror_message = update.message.reply_to_message
        with download_dict_lock:
            keys = list(download_dict.keys())
            try:
                dl = download_dict[mirror_message.message_id]
            except:
                dl = None
        if not dl:
            return sendMessage("ᴛʜɪꜱ ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴄᴛɪᴠᴇ ᴛᴀꜱᴋ!", context.bot, update.message)
    elif len(args) == 1:
        msg = f"ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ᴀᴄᴛɪᴠᴇ <code>/{BotCommands.MirrorCommand}</code> ᴍᴇꜱꜱᴀɢᴇ ᴡʜɪᴄʜ ᴡᴀꜱ ᴜꜱᴇᴅ ᴛᴏ ꜱᴛᴀʀᴛ ᴛʜᴇ ᴅᴏᴡɴʟᴏᴀᴅ ᴏʀ ꜱᴇɴᴅ <code>/{BotCommands.CancelMirror} GID</code> ᴛᴏ ᴄᴀɴᴄᴇʟ ɪᴛ!"
        return sendMessage(msg, context.bot, update.message)

    if OWNER_ID != user_id and dl.message.from_user.id != user_id and user_id not in SUDO_USERS:
        return sendMessage("ᴛʜɪꜱ ᴛᴀꜱᴋ ɪꜱ ɴᴏᴛ ꜰᴏʀ ʏᴏᴜ!", context.bot, update.message)

    if dl.status() == MirrorStatus.STATUS_ARCHIVING:
        sendMessage("ᴀʀᴄʜɪᴠᴀʟ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴄᴀɴᴄᴇʟ ɪᴛ.", context.bot, update.message)
    elif dl.status() == MirrorStatus.STATUS_EXTRACTING:
        sendMessage("ᴇxᴛʀᴀᴄᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴄᴀɴᴄᴇʟ ɪᴛ.", context.bot, update.message)
    elif dl.status() == MirrorStatus.STATUS_SPLITTING:
        sendMessage("ꜱᴘʟɪᴛ ɪɴ ᴘʀᴏɢʀᴇꜱꜱ, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴄᴀɴᴄᴇʟ ɪᴛ", context.bot, update.message)
    else:
        dl.download().cancel_download()

def cancel_all(status):
    gid = ''
    while True:
        dl = getAllDownload(status)
        if dl:
            if dl.gid() != gid:
                gid = dl.gid()
                dl.download().cancel_download()
                sleep(1)
        else:
            break

def cancell_all_buttons(update, context):
    buttons = button_build.ButtonMaker()
    buttons.sbutton("ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ", "ᴄᴀɴᴀʟʟ ᴅᴏᴡɴ")
    buttons.sbutton("ᴜᴘʟᴏᴀᴅɪɴɢ", "ᴄᴀɴᴀʟʟ ᴜᴘ")
    if QB_SEED:
        buttons.sbutton("ꜱᴇᴇᴅɪɴɢ", "ᴄᴀɴᴀʟʟ ꜱᴇᴇᴅ")
    buttons.sbutton("ᴄʟᴏɴɪɴɢ", "ᴄᴀɴᴀʟʟ ᴄʟᴏɴᴇ")
    buttons.sbutton("ᴀʟʟ", "ᴄᴀɴᴀʟʟ ᴀʟʟ")
    button = InlineKeyboardMarkup(buttons.build_menu(2))
    sendMarkup('ᴄʜᴏᴏꜱᴇ ᴛᴀꜱᴋꜱ ᴛᴏ ᴄᴀɴᴄᴇʟ.', context.bot, update.message, button)

def cancel_all_update(update, context):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    data = data.split(" ")
    if CustomFilters._owner_query(user_id):
        query.answer()
        query.message.delete()
        cancel_all(data[1])
    else:
        query.answer(text="ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜᴇꜱᴇ ʙᴜᴛᴛᴏɴꜱ!", show_alert=True)



cancel_mirror_handler = CommandHandler(BotCommands.CancelMirror, cancel_mirror,
                                       filters=(CustomFilters.authorized_chat | CustomFilters.authorized_user), run_async=True)

cancel_all_handler = CommandHandler(BotCommands.CancelAllCommand, cancell_all_buttons,
                                    filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)

cancel_all_buttons_handler = CallbackQueryHandler(cancel_all_update, pattern="ᴄᴀɴᴀʟʟ", run_async=True)

dispatcher.add_handler(cancel_all_handler)
dispatcher.add_handler(cancel_mirror_handler)
dispatcher.add_handler(cancel_all_buttons_handler)
