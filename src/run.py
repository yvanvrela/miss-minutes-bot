"""
Simple Bot to  tracks the hours worked.
First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import datetime
from datetime import timedelta

from telegram import __version__ as TG_VER
from telegram.ext import ConversationHandler, filters
from database.repositories.trackeds_repository import TrackedsRepository
from database.repositories.users_repository import UsersRepository
from database.schemas.trackeds_schema import TrackedSchema
from database.schemas.users_schema import UserSchema
from database.config.db import engine
import re
from util import util
from clickup.api import time_entries
from clickup.api import tasks

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import os

TOKEN = os.getenv('TOKEN')
# Const task conversation
TASK = 1

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_reference = UsersRepository(engine).get_user_by_telegram_id(user.id)

    if user_reference is None:
        user_db = UserSchema(
            id_telegram=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            full_name=user.full_name,
            is_bot=False,
        )

        UsersRepository(engine).add_user(user_db)

    await update.message.reply_html(
        rf"Buenas: {user.mention_html()} 🧐🍷",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


# async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Echo the user message."""
#     await update.message.reply_text(update.message.text)

# ----------------- Traking task ----------------------
async def wait_task_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        '¿Nombre de la tarea?'
    )

    return TASK


async def work(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    last_stop_time = TrackedsRepository(engine).get_last_stop_time(user.id)

    if last_stop_time is None:
        last_task = TrackedsRepository(engine).get_last_task_name(user.id)
        await update.message.reply_text(
            f'Disculpe la molestia, pero, encuentro que usted todavía no ha terminado la tarea anterior. \n📝:{last_task}'
        )
        await update.message.reply_text('Si desea terminarla puede enviar el comando /stop muchas gracias.')
    else:

        new_task = update.message.text
        task_id = None
        task_name = new_task

        pattern = "\/t/(.+)"
        url_task_id_reference = re.findall(pattern, task_name)

        if len(url_task_id_reference) > 0:
            task_id = url_task_id_reference[0]

            # First check task reference in DB
            task_reference_db = TrackedsRepository(
                engine).get_task_by_clickup_task_id(user_id=user.id, task_id=task_id)

            if task_reference_db is None:
                # Get task information from API
                task_reference = tasks.get_task(task_id=task_id)

                if "err" not in task_reference:
                    task_name = task_reference["name"]

                    await update.message.reply_text(f'Ok, la tarea es:\n{task_name}')
                else:
                    await update.message.reply_text('No pude encontrar la tarea.')
            else:
                task_name = task_reference_db.task_name
                await update.message.reply_text(f'Ok, la tarea es:\n{task_name}')

        elif ',' in new_task:
            new_task = new_task.split(',')
            task_id = new_task[0]
            task_name = new_task[1]

        tracked = TrackedSchema(
            start_time=datetime.datetime.now(),
            stop_time=None,
            time_worked=None,
            task_id=task_id,
            task_name=task_name,
            date=datetime.datetime.now().date(),
            user_id=user.id,
        )

        TrackedsRepository(engine).add_track_time(tracked)

        await update.message.reply_text('Tarea agregada 🧐🍷')


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    last_stop_time = TrackedsRepository(engine).get_last_stop_time(user.id)

    if last_stop_time is None:
        # Get task name
        task_name = TrackedsRepository(engine).get_last_task_name(user.id)

        # Get start time
        start_time = TrackedsRepository(engine).get_last_start_time(user.id)
        stop_time = datetime.datetime.now()

        time_worked = stop_time - start_time

        hours_to_seconds = util.hour_to_seconds(time_worked)

        tracked = TrackedSchema(
            stop_time=stop_time,
            time_worked=hours_to_seconds,
            task_name=task_name,
            user_id=user.id,
        )

        seconds_to_hour = str(datetime.timedelta(seconds=hours_to_seconds))

        # Update stop time
        TrackedsRepository(engine).update_track_time(tracked)

        # Add time entry to ClickUp
        task_id = TrackedsRepository(
            engine).get_last_clickup_task_id(user.id)

        if user.id == 789892786 and task_id is not None:

            time_entry = time_entries.add_time_entry(
                task_id=task_id,
                description='QuickTimerBot',
                start_time=util.date_to_epoch(start_time),
                duration=util.hour_to_microseconds(time_worked)
            )

        await update.message.reply_text(f'Usted ha trabajado en \n📝: {task_name} \n\n⏰: {seconds_to_hour} h')

        if user.id == 789892786 and task_id is not None:
            await update.message.reply_text(f'También ya agregué las horas al ClickUp.')

        await update.message.reply_text(f'Lo aguardo en la siguiente tarea. 🧐🍷')
    else:
        await update.message.reply_text(f'Disculpe usted, pero, no encuentro ninguna tarea iniciada con antelación.')


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await stop(update, context)

    return ConversationHandler.END

# ---------------------------------------


# -- Get hours --

async def get_today_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    tasks_today = TrackedsRepository(engine).get_tasks_by_date(
        user.id, datetime.datetime.now().date())

    if len(tasks_today) > 0:
        tasks_msg = ''
        total_hours_worked = 0
        for task in tasks_today:
            tasks_msg += f'{task.task_name}\n{str(datetime.timedelta(seconds=task.time_worked))} h\n\n'
            total_hours_worked += task.time_worked

        await update.message.reply_text('Hoy trabajaste en:')
        await update.message.reply_text(tasks_msg)
        await update.message.reply_text(f'En total trabajaste: {str(datetime.timedelta(seconds=total_hours_worked))} h')
    else:
        await update.message.reply_text('No encuentro ninguna tarea con fecha de hoy')


async def get_yesterday_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    yesterday_date = datetime.datetime.now().date() - timedelta(days=1)

    yesterday_tasks = TrackedsRepository(engine).get_tasks_by_date(
        user.id, yesterday_date)

    if len(yesterday_tasks) > 0:
        tasks_msg = ''
        total_hours_worked = 0
        for task in yesterday_tasks:
            tasks_msg += f'{task.task_name}\n{str(datetime.timedelta(seconds=task.time_worked))} h\n\n'
            total_hours_worked += task.time_worked

        await update.message.reply_text('Ayer trabajaste en:')
        await update.message.reply_text(tasks_msg)
        await update.message.reply_text(f'En total trabajaste: {str(datetime.timedelta(seconds=total_hours_worked))} h')
    else:
        await update.message.reply_text('No encuentro ninguna tarea con fecha de ayer')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Task conversation
    task_handler = ConversationHandler(
        entry_points=[CommandHandler("work", wait_task_name)],
        states={
            TASK: [
                MessageHandler(filters.Regex("^\w.+"), work)
            ],
        },
        fallbacks=[CommandHandler("stop", cancel)],
    )

    application.add_handler(task_handler)

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("work", work))
    application.add_handler(CommandHandler("todaytasks", get_today_tasks))
    application.add_handler(CommandHandler(
        "yesterdaytasks", get_yesterday_tasks))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(
    #     filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
