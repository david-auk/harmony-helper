import logging
import time
import secret
import telegramfunctions
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

# Define password variable
password = secret.telegram['credentials']['userpass']

# Define handlers for each command
def start(update, context):
	"""Send a message when the command /start is issued."""
	update.message.reply_text('Welcome to the *Telegram Command Interface*\n\nAuthenticate: /passwd\nUse: /help', parse_mode='MarkdownV2')
	user = update.message.from_user
	chat_id = update.message.from_user.id
	name = f"@{user.username}"
	if name == '@':
		name = user.first_name

	#userExists = False
	#for x in functions.getData('chatid', f'WHERE id=\"{chat_id}\"'):
	#	userExists = True

	#if userExists:
	#	functions.chData('chatid', chat_id, 'name', name)
	#else:
	#	functions.addChatIdData(name, chat_id, 'N/A', 'N/A')

def helpMenu(update, context):
	"""Send a message when the command /help is issued."""
	update.message.reply_text('The following commands are available:\n\n'
							  'Aurhorise using: /passwd\n\n'
							  'Send me a link!\n'
							  'I\'ll download the link or add a channel to backup\n\n'
							  'View the latest videos with: /latest \n'
							  '/info - Get info about a link\n'
							  '/send VIDID to view the content')

def check_password(update, context):
	"""Check the user's password."""
	# Get the chat ID
	chat_id = update.message.chat_id
	userMessageId = update.message.message_id

	if telegramfunctions.isUserAuthorised(update, context):
		message = context.bot.send_message(chat_id=chat_id, text="Already authorized ✅")
		#time.sleep(1.5)
		#context.bot.delete_message(chat_id=chat_id, message_id=userMessageId)
		#context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
		return

	# Send a message to the user asking for their password
	message = context.bot.send_message(chat_id=chat_id, text="Please enter your password:")

	# Set the next handler to wait for the user's password
	context.user_data["passwdinfo"] = {'user_message_id': userMessageId, 'bot_message_id': message.message_id}
	context.user_data["next_handler"] = "check_password"

def buttonResolver(update, context):
	"""Handle the button press."""
	#chat_id = update.message.chat_id
	query = update.callback_query
	query.answer()
	buttonHandler = context.user_data["next_handler"]

	#context.user_data["next_handler"] = ''

	if buttonHandler == 'example':
		pass

def handleDocument(update, context):

	if telegramfunctions.isUserAuthorised(update, context) is False:
		message = context.bot.send_message(chat_id=update.message.chat_id, text="You are not authorized for this option.")
		return

	document: Document = update.message.document
	# Process the document here
	# You can access the file ID, file name, MIME type, file size, etc.
	# using the properties of the `document` object

	# Example: Reply to the user
	update.message.reply_text(f"You sent a document: {document.file_name}")

def userTextMessage(update, context):
	"""Handle links sent by the user."""

	# Get the message text and chat ID
	message_text = update.message.text
	userMessageId = update.message.message_id
	chat_id = update.message.chat_id

	# Check if the user's input is the correct password (if the previous handler was check_password)
	if context.user_data.get("next_handler") == "check_password":
		passwdInfo = context.user_data.get("passwdinfo")
		initialUserMessageId = passwdInfo['user_message_id']
		initialBotRespondMessageId = passwdInfo['bot_message_id']
		passwordMessageId = userMessageId
		if message_text == password:
			message = context.bot.send_message(chat_id=chat_id, text="Correct password ✅")
			finalBotResponceMessageId = message.message_id

			user = update.message.from_user
			name = f"@{user.username}"
			if name == '@':
				name = user.first_name

			userExists = False
			hasPriorityValue = False
			for (name, chatId, priority, authenticated) in functions.getData('chatid', f'WHERE id=\"{chat_id}\"'):
				userExists = True
				if priority == 'N/A':
					hasPriorityValue = True

			if userExists:
				dbfunctions.chData('chatid', chat_id, 'authenticated', '1')
				if hasPriorityValue:
					dbfunctions.chData('chatid', chat_id, 'priority', '3')
			else:
				functions.addChatIdData(name, chat_id, '3', '1')
			if priority != '1':
				functions.msgHost(f"The user {name} just got added to the Database", False)

			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=initialBotRespondMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=passwordMessageId)
			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=finalBotResponceMessageId)
		else:
			message = context.bot.send_message(chat_id=chat_id, text="Sorry, that's not the correct password.")
			finalBotResponceMessageId = message.message_id
			time.sleep(1.5)
			context.bot.delete_message(chat_id=chat_id, message_id=initialUserMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=initialBotRespondMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=passwordMessageId)
			context.bot.delete_message(chat_id=chat_id, message_id=finalBotResponceMessageId)

		context.user_data["next_handler"] = ""
		return


def error(update, context):
	"""Echo the user message."""
	update.message.reply_text(f"Unknown command: {update.message.text}")


def main():
	# Set up the Telegram bot
	updater = Updater(secret.telegram['credentials']['token'], use_context=True)

	# Get the dispatcher to register handlers
	dp = updater.dispatcher

	# Add handlers for different commands
	dp.add_handler(CommandHandler("start", start))
	dp.add_handler(CommandHandler("help", helpMenu))
	dp.add_handler(CommandHandler("passwd", check_password))
	dp.add_handler(CallbackQueryHandler(buttonResolver))
	dp.add_handler(MessageHandler(Filters.document, handleDocument))
	dp.add_handler(MessageHandler(Filters.text & (~Filters.command), userTextMessage))
	dp.add_handler(MessageHandler(Filters.text & Filters.command, error))

	# Start the bot
	updater.start_polling()

	# Run the bot until you press Ctrl-C or the process is stopped
	updater.idle()

if __name__ == '__main__':
	main()