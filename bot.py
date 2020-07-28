import os
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from bot.exceptions import ExchangeException
from bot.exchange import Exchange


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


exchange = Exchange(cache_size=2)


def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi! I'm a currency convertor Bot.")


def convert(update, context):
    """Convert one currency to another."""
    data = [p.strip().upper() for p in update.message.text.split()]
    logger.info(data)
    if len(data) != 3:
        update.message.reply_text('3 params required')
    else:
        try:
            result, meta = exchange.make_deal(*data)
            caption = f'{data[0]} {data[1]} = {result:.3f} {data[2]}'
            update.message.reply_photo(open(meta[2], 'rb'), caption=caption)
        except ExchangeException as error:
            update.message.reply_text(str(error))
        except Exception as error:
            update.message.reply_text(f'Something went wrong: {error}')


def main():
    """Start the bot."""
    token = os.environ.get("BOT_API_TOKEN")
    token = "1397508856:AAFdwf3jC6njilYwSgFFZwl3-J-Mr9o3sA0"
    assert token is not None
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, convert))

    # Start the Bot
    updater.start_polling()

    logging.info('Bot is ready')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
