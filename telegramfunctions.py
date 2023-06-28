import dbfunctions

from datetime import datetime
from telegram.ext import CallbackContext

def isUserAuthorised(update):
	authenticated = dbfunctions.getData('chatid', f'WHERE id = \"{update.message.chat_id}\"', returnType='single')[3]
	if authenticated == 'YES':
		return True
	return False

def isUserBanned(update):
	authenticated = dbfunctions.getData('chatid', f'WHERE id = \"{update.message.chat_id}\"', returnType='single')[3]
	if authenticated == 'BANNISHED':
		return True
	return False

def delete_message_job(context: CallbackContext):
	job = context.job
	chat_id = job.context['chat_id']
	message_ids = job.context['message_id']

	if type(message_ids) is str:
		message_id = message_ids
		context.bot.delete_message(chat_id=chat_id, message_id=message_id)
	
	elif type(message_ids) is list:
		for message_id in message_ids:
			context.bot.delete_message(chat_id=chat_id, message_id=message_id)

def beginTelegramFunction(update):
	chat_id = update.message.chat_id
	
	now = int(datetime.now().strftime("%Y%m%d%H%M%S"))
	
	dbfunctions.chData('chatid', chat_id, 'lastuse', now)

	user = update.message.from_user
	if user['username']:
		name = user['username']
	elif user['first_name'] and user['last_name']:
		name = user['first_name'] + ' ' + user['last_name']
	else:
		name = user['first_name']

	if dbfunctions.getData('chatid', f'WHERE id = \"{chat_id}\"', returnType='single')[0] != name:
		dbfunctions.chData('chatid', chat_id, 'name', name)

	dbfunctions.chData('chatid', chat_id, 'lastuse', now)

	authenticated = dbfunctions.getData('chatid', f'WHERE id = \"{update.message.chat_id}\"', returnType='single')[3]
	if authenticated == 'BANNISHED':
		return True
	return False