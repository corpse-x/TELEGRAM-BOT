import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import threading
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store admin user IDs
admin_ids = {int(os.environ.get('OWNER_ID'))}

# Dictionary to store the current auction details
current_auction = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to the Auction Bot! Tag an item to start bidding.")

def promote_admin(update: Update, context: CallbackContext):
    if update.effective_user.id in admin_ids:
        try:
            new_admin_id = int(context.args[0])
            admin_ids.add(new_admin_id)
            update.message.reply_text(f"User {new_admin_id} promoted to admin.")
        except (IndexError, ValueError):
            update.message.reply_text("Usage: /auc_promote <user_id>")
    else:
        update.message.reply_text("Only the bot owner can promote admins.")

def handle_bids(update: Update, context: CallbackContext):
    if update.message.reply_to_message:
        original_message = update.message.reply_to_message
        if original_message.message_id == current_auction.get('item_message_id'):
            try:
                bid_amount = int(update.message.text.split()[1])
                current_auction['highest_bid'] = bid_amount
                current_auction['highest_bidder'] = update.effective_user.username
                current_auction['bid_message_id'] = update.message.message_id
                loading_message = context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Loading...",
                    reply_to_message_id=update.message.message_id
                )
                current_auction['loading_message_id'] = loading_message.message_id

                # Schedule the final message after 1 minute
                threading.Thread(target=finalize_auction, args=(context.bot, update.effective_chat.id)).start()
            except (IndexError, ValueError):
                update.message.reply_text("Usage: @<item_message> oy <amount>")

def finalize_auction(bot, chat_id):
    time.sleep(60)
    if 'loading_message_id' in current_auction:
        loading_message_id = current_auction['loading_message_id']
        highest_bidder = current_auction['highest_bidder']
        highest_bid = current_auction['highest_bid']

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Sell it", callback_data='sell')]
        ])

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=loading_message_id,
            text=f"Selling this item to {highest_bidder} for {highest_bid}",
            reply_markup=reply_markup
        )

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == 'sell':
        if user_id in admin_ids:
            query.answer()
            query.edit_message_text(text="Item sold!")
        else:
            query.answer(text="Soja", show_alert=True)

def welcome_message(update: Update, context: CallbackContext):
    if update.message.chat.type == 'private':
        user_name = update.effective_user.username
        welcome_text = f"Hey {user_name}!\n\nThis is a Zeta Auction Bot.\n\nDeveloped by @corpsealone.\n\nFor any query, join @paradoxdump!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=welcome_text)

def main():
    updater = Updater(os.environ.get('TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    # Register commands and handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("auc_promote", promote_admin, pass_args=True))
    dispatcher.add_handler(MessageHandler(Filters.reply & Filters.text & Filters.regex(r'^oy \d+$'), handle_bids))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    
    # Add welcome message for private messages
    dispatcher.add_handler(MessageHandler(Filters.private, welcome_message))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()