import DB_Linker
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/AddNewUser', methods = ['POST'])
def _addNewUser():
	print('addNewUser')
	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	user_name = myjson['user_name']
	DB_Linker.AddNewUser(user_name)
	return 'okay'

@app.route('/LookUpUsers', methods = ['POST','GET'])
def _lookUpUsers():
	print('lookUpUsers')

	result = DB_Linker.LookUpUsers()
	print(result)
	return json.dumps(result,ensure_ascii=False)

@app.route('/DescribeTable', methods = ['POST'])
def _describeTable():
	print('describeTable')

	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	table_name = myjson['table_name']

	result = DB_Linker.DescribeTable(table_name)
	print(result)
	return json.dumps(result,ensure_ascii=False)

@app.route('/InsertDataToTable', methods = ['POST','GET'])
def _insertDataToTable():
	print('insertDataToTable')

	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	table_name = myjson['table_name']
	data_list = myjson['data_list']

	DB_Linker.InsertDataToTable(table_name,data_list)
	
	return 'okay'

@app.route('/LookUpTables', methods = ['POST'])
def _lookUpTables():
	print('LookUpTables')

	result = DB_Linker.LookUpTables()
	print(result)
	return json.dumps(result,ensure_ascii=False)

@app.route('/GetUtteranceByUser', methods = ['POST'])
def _getUtteranceByUser():
	print('GetUtteranceByUser')

	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	user_name = myjson['user_name']

	result = DB_Linker.GetUtteranceByUser(user_name)
	def func(x):
		if 'date_time' in x:
			x['date_time']=str(x['date_time'])
		return x
	result = list(map(func,result))
	print(result)
	return json.dumps(result,ensure_ascii=False)

@app.route('/QueryToDatabase', methods = ['POST'])
def _queryToDatabase():
	print('QueryToDatabase')

	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	query = myjson['query']

	result = DB_Linker.QueryToDatabase(query)
	def func(x):
		if 'date_time' in x:
			x['date_time']=str(x['date_time'])
		return x
	result = list(map(func,result))
	print(result)
	return json.dumps(result,ensure_ascii=False)


@app.route('/CreateNewTable', methods = ['POST'])
def _createNewTable():
	print('CreateNewTable')
	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	table_name = myjson['table_name']
	column_list = myjson['column_list']

	DB_Linker.CreateNewTable(table_name,column_list)
	return 'okay'

@app.route('/QueryToUserKB', methods = ['POST'])
def _queryToUserKB():
	print('QueryToUserKB')

	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	query = myjson['query']

	result = DB_Linker.QueryToUserKB(query)
	print(result)
	return result


@app.route('/QueryToMasterKB', methods = ['POST'])
def _queryToMasterKB():
	print('QueryToMasterKB')

	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	query = myjson['query']

	result = DB_Linker.QueryToMasterKB(query)
	print(result)
	return result

@app.route('/InsertKnowledgeToUserKB', methods = ['POST'])
def _insertKnowledgeToUserKB():
	print('InsertKnowledgeToUserKB')

	data = request.data.decode('utf-8')
	myjson = json.loads(data)
	user_name = myjson['user_name']
	triple = myjson['triple']
	print(triple)
	result = DB_Linker.InsertKnowledgeToUserKB(user_name,triple)
	
	return 'okay'

if __name__ == "__main__":
	app.run(port=8291,host='143.248.135.146')
