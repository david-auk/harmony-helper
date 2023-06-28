import logging
import time
import secret
import dbfunctions
import telegramfunctions
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
from telegram.ext.jobqueue import Job
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ChatAction


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

# Define password variable
password = secret.telegram['credentials']['userpass']

# Define handlers for each command
def start(update, context):
	"""Send a message when the command /start is issued."""

	# BANNED TEXT HERE

	chat_id = update.message.from_user.id

	if not dbfunctions.getData('chatid', f'WHERE id = \"{chat_id}\"', returnType='single'): # If the user doesnt exist (yet..)

		update.message.reply_text('Welcome to the *Telegram Command Interface*\n\nAuthenticate: /passwd\nUse: /help', parse_mode='MarkdownV2')
		user = update.message.from_user

		if user['username']:
			name = user['username']
		elif user['first_name'] and user['last_name']:
			name = user['first_name'] + ' ' + user['last_name']
		else:
			name = user['first_name']

		dbfunctions.addData('chatid', (name, chat_id, 90, 'N/A', 0, int(telegramfunctions.datetime.now().strftime("%Y%m%d%H%M%S"))))
	else:
		isBanned = telegramfunctions.beginTelegramFunction(update)
		if isBanned:
			update.message.reply_text('You are *BANNED*\nYou are not allowed to use this bot, Goodbye', parse_mode='MarkdownV2')
		else:
			update.message.reply_text('Welcome to the *Telegram Command Interface*\n\nAuthenticate: /passwd\nUse: /help', parse_mode='MarkdownV2')

def helpMenu(update, context):
	"""Send a message when the command /help is issued."""

	isBanned = telegramfunctions.beginTelegramFunction(update)
	if isBanned:
		update.message.reply_text('You are *BANNED*\nYou are not allowed to use this bot, Goodbye', parse_mode='MarkdownV2')
		return

	update.message.reply_text('The following commands are available:\n\n'
							  'Aurhorise using: /passwd\n\n'
							  'Send me a link!\n'
							  'I\'ll download the link or add a channel to backup\n\n'
							  'View the latest videos with: /latest \n'
							  '/info - Get info about a link\n'
							  '/send VIDID to view the content')

def check_password(update, context):
	"""Check the user's password."""

	isBanned = telegramfunctions.beginTelegramFunction(update)
	if isBanned:
		update.message.reply_text('You are *BANNED*\nYou are not allowed to use this bot, Goodbye', parse_mode='MarkdownV2')
		return

	# Get the chat ID
	chat_id = update.message.chat_id
	userMessageId = update.message.message_id

	if telegramfunctions.isUserAuthorised(update):
		message = context.bot.send_message(chat_id=chat_id, text="Already authorized ✅")
		context.job_queue.run_once(
			telegramfunctions.delete_message_job,
			1.5,  # Delay in seconds
			context={'chat_id': chat_id, 'message_id': [userMessageId, message.message_id]}
		)
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

	isBanned = telegramfunctions.beginTelegramFunction(update)
	if isBanned:
		update.message.reply_text('You are *BANNED*\nYou are not allowed to use this bot, Goodbye', parse_mode='MarkdownV2')
		return

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
		context.bot.delete_message(chat_id=chat_id, message_id=passwordMessageId)
		if message_text == password:
			message = context.bot.send_message(chat_id=chat_id, text="Correct password ✅")
			finalBotResponceMessageId = message.message_id

			user = update.message.from_user

			if dbfunctions.getData('chatid', f'WHERE id = \"{chat_id}\"', returnType='single')[2] == 90:
				dbfunctions.chData('chatid', chat_id, 'priority', '3')

			dbfunctions.chData('chatid', chat_id, 'authorised', 'YES')
			
			for (userName, prioOneChatId, prio, authorised, loginTries, lastuse) in dbfunctions.getData('chatid', f'WHERE id = \"{chat_id}\"'):
				newUserName = dbfunctions.getData('chatid', f'WHERE id = \"{chat_id}\"', returnType='single')[0]

				context.bot.send_message(chat_id=prioOneChatId, text=f"The user {newUserName} just got authenticated")

			# Schedule the deletion job after a delay
			job_queue = context.job_queue
			context.job_queue.run_once(
				telegramfunctions.delete_message_job,
				1.5,  # Delay in seconds
				context={'chat_id': chat_id, 'message_id': [initialUserMessageId, initialBotRespondMessageId]}
			)

			job_queue = context.job_queue
			context.job_queue.run_once(
				telegramfunctions.delete_message_job,
				3,  # Delay in seconds
				context={'chat_id': chat_id, 'message_id': [finalBotResponceMessageId]}
			)
		else:

			# The password is incorrect

			newLoginTries = dbfunctions.getData('chatid', f'WHERE id = \"{chat_id}\"', returnType='single')[4] + 1
			dbfunctions.chData('chatid', chat_id, 'logintries', newLoginTries)

			message = context.bot.send_message(chat_id=chat_id, text=f"Sorry, that's not the correct password.\nTry {newLoginTries}/{secret.telegram['settings']['maxPasswordTries']}")

			if newLoginTries == secret.telegram['settings']['maxPasswordTries']:
				dbfunctions.chData('chatid', chat_id, 'authorised', 'BANNISHED')

			finalBotResponceMessageId = message.message_id
			
			# Schedule the deletion job after a delay
			job_queue = context.job_queue
			context.job_queue.run_once(
				telegramfunctions.delete_message_job,
				2.5,  # Delay in seconds
				context={'chat_id': chat_id, 'message_id': [initialUserMessageId, initialBotRespondMessageId, finalBotResponceMessageId]}
			)

		context.user_data["next_handler"] = ""
		return


def error(update, context):
	"""Echo the user message."""

	isBanned = telegramfunctions.beginTelegramFunction(update)
	if isBanned:
		update.message.reply_text('You are *BANNED*\nYou are not allowed to use this bot, Goodbye', parse_mode='MarkdownV2')
		return

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