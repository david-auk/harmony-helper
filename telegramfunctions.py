import dbfunctions

def isUserAuthorised(update, context):
	chat_id = update.message.chat_id
	for (name, dbChatId, priority, authenticated) in dbfunctions.getData('chatid', f'WHERE id = \"{chat_id}\"'):
		if authenticated == 'YES':
			return True

	return False