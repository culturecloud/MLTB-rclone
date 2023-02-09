from signal import signal, SIGTERM
from time import time, localtime, strftime
from bot import Interval, QbInterval, bot, botloop, app, LOGGER
from os import path as ospath, remove as osremove, execl as osexecl
from pyrogram.filters import command
from pyrogram.handlers import MessageHandler
from sys import executable
from subprocess import run as srun
from bot.helper.ext_utils.bot_commands import BotCommands
from bot.helper.ext_utils.filters import CustomFilters
from bot.helper.ext_utils.message_utils import editMessage, sendMarkup, sendMessage
from bot.helper.ext_utils.misc_utils import ButtonMaker, exit_cleanup, start_cleanup
from bot.helper.ext_utils import db_handler
from bot.modules import batch, cancel, botfiles, copy, leech, mirror_leech, myfilesset, owner_settings, cloudselect, search, myfiles, stats, status, clone, storage, cleanup, user_settings, ytdlp, shell, exec, bt_select, sync, bisync, rss

async def start(client, message):
    buttons = ButtonMaker()
    buttons.url_buildbutton("Repo", "https://github.com/culturecloud/mltb-rclone")
    buttons.url_buildbutton("Owner", "https://t.me/pseudokawaii")
    reply_markup = buttons.build_menu(2)
    if CustomFilters.user_filter or CustomFilters.chat_filter:
        msg = f'''
**⚡ Welcome to RCMLTB!**

The all-in-one Telegram bot which utilizes some of the world's most awesome & powerful file transfer tools like Aria2, qBittorrent, YTDLP, Rclone and help you do ✨ <i>stuffs</i> ✨

<i>See /{BotCommands.HelpCommand} for more info on how to use me.</i>
        '''
        await sendMarkup(msg, message, reply_markup)
    else:
        await sendMarkup("Not Authorized user, deploy your own version", message, reply_markup)     
    
async def restart(client, message):
    restart_msg= await sendMessage("Restarting...", message)
    LOGGER.info("Restart command recieved! Restarting the bot...")
    if Interval:
        Interval[0].cancel()
        Interval.clear()
    if QbInterval:
        QbInterval[0].cancel()
        QbInterval.clear()
    exit_cleanup()
    bot.stop()
    if app is not None:
        app.stop()
    srun(["pkill", "-9", "-f", "aria2c|rclone|qbittorrent-nox|ffmpeg"])
    srun(["python3", "update.py"])
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_msg.chat.id}\n{restart_msg.id}\n")
    osexecl(executable, executable, "-m", "bot")
    LOGGER.info("Bot restarted!")

async def ping(client, message):
    start_time = int(round(time() * 1000))
    reply = await sendMessage("`Calculating latency ...`", message)
    end_time = int(round(time() * 1000))
    await editMessage(f'⚡ `{end_time - start_time} ms`', reply)

async def get_log(client, message):
    current_time = strftime("%d%m%y-%H%M%S", localtime())
    await client.send_document(chat_id= message.chat.id , document= "log.txt", file_name=f"log-{current_time}")
    
help_string = f'''
<u>**Mirror**</u>
/{BotCommands.MirrorCommand} - Mirror to selected cloud.
/{BotCommands.MirrorBatchCommand} - Mirror Telegram files and links in batch to cloud.
/{BotCommands.YtdlMirrorCommand} - Mirror ytdlp supported link.
/{BotCommands.ZipMirrorCommand} - Mirror and zip to cloud.
/{BotCommands.UnzipMirrorCommand} - Mirror and extract to cloud.
/{BotCommands.MultiZipMirrorCommand} - Mirror and zip multiple files to cloud.
/{BotCommands.YtdlZipMirrorCommand} - Mirror and zip ytdlp supported link.

<u>**Leech**</u>
/{BotCommands.LeechCommand} - Leech from cloud/link to Telegram.
/{BotCommands.LeechBatchCommand} - Leech Telegram files/links in batch to Telegram.
/{BotCommands.YtdlLeechCommand} - Leech yt-dlp supported link.
/{BotCommands.ZipLeechCommand} - Leech and zip to Telegram.
/{BotCommands.UnzipLeechCommand} - Leech and extract to Telegram.
/{BotCommands.MultiZipLeechCommand} - Leech and zip multiple files to Telegram.
/{BotCommands.YtdlZipLeechCommand} - Leech and zip yt-dlp supported link.

<u>**Google Drive**</u>
/{BotCommands.CloneCommand} - Clone gdrive link file/folder.

<u>**Configuration**</u>
/{BotCommands.CloudSelectCommand} - Select cloud/folder for mirror.
/{BotCommands.UserSetCommand} - User settings.
/{BotCommands.OwnerSetCommand} - Owner settings.
/{BotCommands.BotFilesCommand} - Bot configuration files.

<u>**Rclone**</u>
/{BotCommands.CopyCommand} - Copy from cloud to cloud.
/{BotCommands.SyncCommand} - Sync two clouds.
/{BotCommands.BiSyncCommand} - Sync two clouds bidirectionally.
/{BotCommands.MyFilesCommand} - Rclone File Manager.
/{BotCommands.StorageCommand} - Cloud details.
/{BotCommands.CleanupCommand} - Clean cloud trash.

<u>**Control**</u>
/{BotCommands.LogsCommand} - Send log file.
/{BotCommands.StatusCommand} - Status message of tasks.
/{BotCommands.CancelCommand} - Cancel single task by GID or reply.
/{BotCommands.CancelAllCommand} - Cancel all tasks.
/{BotCommands.RestartCommand} - Restart & update the bot.

<u>**Miscellaneous**</u>
/{BotCommands.RssCommand} - Configure RSS feeds.
/{BotCommands.SearchCommand} - Search for torrents.
/{BotCommands.PingCommand} - Check bot response speed.
/{BotCommands.StatsCommand} - Bot server stats.
/{BotCommands.ShellCommand} - Run commands in shell.
/{BotCommands.ExecCommand} - Execute Python scripts.

<i>Send the command without any query to get detailed help on the specific command.</i>
'''

async def bot_help(client, message):
    await sendMessage(help_string, message)

async def main():
    start_cleanup()
    if ospath.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        try:
            await bot.edit_message_text(chat_id, msg_id, "Restarted successfully!")  
        except:
            pass   
        osremove(".restartmsg")
            
    start_handler = MessageHandler(start, filters= command(BotCommands.StartCommand))
    restart_handler = MessageHandler(restart, filters= command(BotCommands.RestartCommand) & (CustomFilters.owner_filter | CustomFilters.sudo_filter))
    log_handler = MessageHandler(get_log, filters= command(BotCommands.LogsCommand) & (CustomFilters.owner_filter | CustomFilters.sudo_filter))
    ping_handler = MessageHandler(ping, filters= command(BotCommands.PingCommand) & (CustomFilters.user_filter | CustomFilters.chat_filter))
    help_handler = MessageHandler(bot_help, filters= command(BotCommands.HelpCommand) & (CustomFilters.user_filter | CustomFilters.chat_filter))
   
    bot.add_handler(start_handler)
    bot.add_handler(restart_handler)
    bot.add_handler(log_handler)
    bot.add_handler(ping_handler)
    bot.add_handler(help_handler)
    
def graceful_exit():
    LOGGER.info("Stop signal recieved! Stopping gracefully...")
    exit_cleanup()
    bot.stop()
    if app is not None:
        app.stop()
    botloop.close()
    exit()

bot.start()
if app is not None:
    app.start()

botloop.add_signal_handler(SIGTERM, graceful_exit)
botloop.run_until_complete(main())
botloop.run_forever()
