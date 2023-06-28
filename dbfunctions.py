import mysql.connector as database
import secret

#
# chatid, priority 90 == not set
#

# Defining DB configuration
mydb = database.connect(
	host=secret.mariadb['connection']['host'],
	user=secret.mariadb['credentials']['user'],
	password=secret.mariadb['credentials']['password'],
	database=secret.mariadb['connection']['database'],
	converter_class=database.conversion.MySQLConverter
)

def addData(table, values):
	mydb.reconnect()
	addChatIdDataCursor = mydb.cursor(buffered=True)
	try:
		statement = f"INSERT INTO {table} VALUES {values}"
		addChatIdDataCursor.execute(statement)
		mydb.commit()
	except database.Error as e:
		print(f"Error adding entry from {mydb.database}[{table}]: {e}")

def getData(table, inputstatement='ALL', returnType='array'):
	mydb.reconnect()
	getDataCursor = mydb.cursor(buffered=True)
	try:
		if inputstatement == "ALL":
			statement = "SELECT * FROM " + table
		else:
			statement = f"SELECT * FROM {table} {inputstatement}" # WHERE {column} {operator} \"{instanceid}\""
		getDataCursor.execute(statement)
		rows = getDataCursor.fetchall()
		if len(rows) == 1:
			if returnType == 'single':
				return tuple(rows[0])
			elif returnType == 'array':
				return [tuple(row) for row in rows]
		else:
			return [tuple(row) for row in rows]
	except database.Error as e:
		print(f"Error retrieving entry from {mydb.database}[{table}]: {e}")

# Function for changing data of a table
def chData(table, id, column, newData):
	mydb.reconnect()
	chDataCursor = mydb.cursor(buffered=True)
	try:
		statement = "UPDATE " + table + " SET {}=\"{}\" WHERE id=\"{}\"".format(column,mydb.converter.escape(newData),id)
		chDataCursor.execute(statement)
		mydb.commit()
	except database.Error as e:
		print(f"Error manipulating data from {mydb.database}[{table}]: {e}")

# Function for deleting rows in any table using the id variable
def delData(table, instanceid):
	mydb.reconnect()
	delDataCursor = mydb.cursor(buffered=True)
	try:
		statement = "DELETE FROM " + table + " WHERE id=\'{}\'".format(instanceid)
		delDataCursor.execute(statement)
		mydb.commit()
		if delDataCursor.rowcount == 0:
			print("No rows where deleted.")
	except database.Error as e:
		print(f"Error deleting entry from {mydb.database}[{table}]: {e}")