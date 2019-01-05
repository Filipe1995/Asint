# coding=utf-8
from flask import Flask
from flask import render_template
from flask import request
import json
import time
import Buildings
import users
import fenixedu
import urllib2
import random
from urllib2 import Request, urlopen
import mysql.connector
from math import sin, cos, sqrt, atan2, radians
#from google.appengine.ext import ndb

app = Flask(__name__)
aux=Buildings.SaveBuilds()
aux2=users.SaveUsers()
#global Lists dará probs com o ndb?
usersList = {} #persistido
msgQueue={} #memchached
log_msg={} #persistido
#log_pos={} #persistido +-
users_sys={} #persistido
build_userslist={} #persistido (alterar para memchached)
builds={} #persistido
pendingBots = {} #memchached
acceptedBots={} #memchached
building={}

class Database:
	def __init__(self):
		self.mydb = mysql.connector.connect(
		  host="db.tecnico.ulisboa.pt",
		  user="ist178685",
		  passwd="swkr1720",
		  database="ist178685"
		)
		self.cursor = self.mydb.cursor()
		return
	def query(self, query, params):
        	self.cursor.execute(query, params)
		self.mydb.commit()
		return ""

	def query_sel(self, query):
        	self.cursor.execute(query)
		myresult = self.cursor.fetchall()
		return myresult
	def builds(self):
        	self.cursor.execute("Select*from builds")
		myresult = self.cursor.fetchall()
		aux={}
		for row in myresult:
		    packet={'name': row[2],'lat':  float(row[0]), 'lon': float(row[1])}
		    aux[int(row[3])]=packet
		return aux
	def users(self):
		self.cursor.execute("Select*from user_loc")
		myresult = self.cursor.fetchall()
		aux={}
		for row in myresult:
		    packet={'lat': float(row[1]),'lon': float(row[2]), 'local': row[3]}
		    aux[row[0]]=packet
		return aux
	def u_in_b(self):
		self.cursor.execute("Select*from userbuild")
		myresult = self.cursor.fetchall()
		aux={}

		for row in myresult:
			pacote={'id': row[1]}
			if int(row[0]) in aux:
				aux[int(row[0])].append(pacote)
			else:
		    		aux[int(row[0])]=[pacote]
		return aux
	def pos(self):
		self.cursor.execute("Select*from pos")
		myresult = self.cursor.fetchall()
		aux={}
		for row in myresult:
			if row[3]==1:
				pacote= {'Entrou': row[1], 'timestamp': row[2]}
			elif row[3]==0:
				pacote= {'Saiu': row[1], 'timestamp': row[2]}
		    #packet={'lat': row[1],'lon': row[2], 'local': row[3]}
			if row[0] in aux:
				aux[row[0]].append(pacote)
			else:
		    		aux[row[0]]=[pacote]
		return aux
	def msg(self):
		self.cursor.execute("Select*from msg")
		myresult = self.cursor.fetchall()
		log={}
		#pack = {'sender': sender, 'message': message, 'build': user_location, 'timestamp': time.time()}
		for row in myresult:
			pack = {'sender': row[3], 'message': row[4], 'build': row[1], 'timestamp': row[2]}
		    #packet={'lat': row[1],'lon': row[2], 'local': row[3]}
			if row[0] in log:
				log[row[0]].append(pack)
			else:
		    		log[row[0]]=[pack]
		return log
	def msg_queue(self):
		self.cursor.execute("Select*from msgfila")
		myresult = self.cursor.fetchall()
		log={}
		#pack = {'sender': sender, 'message': message, 'build': user_location, 'timestamp': time.time()}
		for row in myresult:
			pack = {'sender': row[3], 'message': row[4], 'build': row[1], 'timestamp': row[2]}
		    #packet={'lat': row[1],'lon': row[2], 'local': row[3]}
			if row[0] in log:
				log[row[0]].append(pack)
			else:
		    		log[row[0]]=[pack]
		return log



#global funcions dará probs com o ndb?
def calculateNearbyUsers(userID, radius):
	userlista={}
	def db_get():
		list={}
		db=Database()
		list=db.users()
		return list

	userlista=db_get()
	print(userlista)
	print("se+aradpr")
	print(usersList)
	nearbyUsersList = []
	userLat = radians(usersList[userID]['lat'])
	userLon = radians(usersList[userID]['lon'])
	userLoc = userlista[userID]['local']
	print("Local:",userLoc)
	R = 6373.0
	print( usersList[userID])
	print(userLat , '    ', userLon)
	for key, value in userlista.iteritems():
		if key == userID:
			continue
		dlon = radians(userlista[key]['lon']) - userLon
		dlat = radians(userlista[key]['lat']) - userLat
		n_uloc = userlista[key]['local']

		a = sin(dlat / 2)**2 + cos(userLat) * cos(userlista[key]['lat']) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))

		distance = (R * c)*1000
		print(distance)
		if (userLoc != "Fora de Edificios definidos") and (n_uloc != "Fora de Edificios definidos"):
			if (distance <=radius) and (userLoc==n_uloc):
				nearbyUsersList.append(key)
		#print('Distance between user ', userID, ' and ', key, 'is: ', distance)

	return nearbyUsersList # [user1, user2]

def whichbuilding(userID):
	edifs={}
	u_in_b={}
	def db_ins(sql,val):
        	db = Database()
        	db.query(sql,val)
	def db_query():
        	db = Database()
		list=db.builds()
		return list
	userlista={}
	def db_query4():
        	db = Database()
		list=db.u_in_b()
		return list
	def db_get():
		list={}
		db=Database()
		list=db.users()
		return list
	userlista=db_get()
	edifs=db_query()
	u_in_b=db_query4()
	print(u_in_b)
	print("sep777")
	print(build_userslist)
	userLat = radians(userlista[userID]['lat'])
	userLon = radians(userlista[userID]['lon'])
	packet={'id': userID}
	R = 6373.0
	for key, value in edifs.iteritems():
		dlon = radians(edifs[key]['lon']) - userLon
		dlat = radians(edifs[key]['lat']) - userLat
		a = sin(dlat / 2)**2 + cos(userLat) * cos(edifs[key]['lat']) * sin(dlon / 2)**2
		c = 2 * atan2(sqrt(a), sqrt(1 - a))
		distance = (R * c)*1000
		print("dist",distance)
		if distance<40:
			if not key in u_in_b:
				u_in_b[key]=[packet]
				sql = "INSERT INTO userbuild (bID, uID) VALUES (%s, %s)"
				val = (key,userID)
				db_ins(sql,val)
			else:
				if not packet in u_in_b[key]:
					u_in_b[key].append(packet)
					sql = "INSERT INTO userbuild (bID, uID) VALUES (%s, %s)"
					val = (key,userID)
					db_ins(sql,val)
	return u_in_b

def getbuildingID():
	buildlist=[]
	edifs={}
	def db_query():
        	db = Database()
		list=db.builds()
		return list
	edifs=db_query()
	for key, value in edifs.iteritems():
		buildlist.append(key)
	return buildlist
def getUsersindabuilding(buildID):
	def db_query4():
        	db = Database()
		list=db.u_in_b()
	u_in_b=db_query4()
	aux=[]
	for key,value in u_in_b.iteritems():
		if buildID == key:
			aux1=u_in_b[key]
			i=0
			while i < len(aux1) :
				aux2=aux1[i].get('id')
				aux.append(aux2)
				i+=1
			return aux
		else:
			print("Erro")
#Classes
"""
class build:
	def __init__(self,buildingID,buildingname,buildinglat,buildinglong):
		buildingID =self.buildingID
		buildingname =self.buildingname
		buildinglat =self.buildinglat
		buildinglong =self.buildinglong
class User:
	def __init__(self,UserID,Username):
		UserID =self.UserID
		Username =self.Username
class log_pos:

class log_msg:

"""
@app.route('/')
def home():
    return render_template("home.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/admin/define', methods=['POST', 'GET'])
def define():
	b={}
	def db_query():
		list={}
		db=Database()
		list=db.builds()
		return list
	def db_query2(sql,val):
        	db = Database()
        	db.query(sql,val)
	if request.method == "POST":
		buildinglat=str(request.form.get('buildinglat'))
		buildinglong=str(request.form.get('buildinglong'))
		buildingID=str(request.form.get('buildingID'))
		buildingname=str(request.form.get('buildingname'))
		packet={'name': buildingname,'lat':  float(buildinglat), 'lon': float(buildinglong)}
		buildID=int(buildingID)
		builds[buildID]=packet
		b=db_query()
		# Inserir na base de dados
		if not buildingID in b:
			sql = "INSERT INTO builds (latitude, longitude,ID, name) VALUES (%s, %s,%s,%s)"
			val = (buildinglat,buildinglong,buildingID, buildingname)
			db_query2(sql,val)
		print(builds)
		aux.AddBuilding(buildingID,buildingname,buildinglat,buildinglong)
		indexbuildings = getbuildingID()
		print(indexbuildings)
	return render_template("define.html")

@app.route('/admin/occupancy', methods=['POST', 'GET'])
def searchUsers():
	#print("upa")
	edifs={}
	u={}
	def db_query():
		list={}
        	db = Database()
		list=db.builds()
		return list
	def db_query2():
		list={}
        	db = Database()
		list=db.users()
		return list
	if request.method == "GET":
		u=db_query2()
		print(u)
		print("separador")
		print(users_sys)
		return json.dumps(users_sys)
	if request.method == "POST":
		edifs=db_query()
		print(builds)
		Builds_nomes={}
		for key, value in edifs.iteritems():
			Builds_nomes[key]=edifs[key]['name']
		print(Builds_nomes)
		if Builds_nomes != None:
			return json.dumps(Builds_nomes)
		else:
			return json.dumps("")
	return json.dumps("")

@app.route('/admin/occup/indabuild', methods=['GET'])
def indabuildings():
	#packet={'id': UserID}
	#buildings=whichbuilding(UserID)
	edifs={}
	def db_query():
        	db = Database()
		list=db.builds()
		return list
	def db_query4():
        	db = Database()
		list=db.u_in_b()
	u_in_b=db_query4()
	edifs=db_query()
	building=u_in_b
	print("aqui está")
	print(u_in_b)
	for build in building:
		print(building[build])
		auxiliar={}
		print(build)
		print(edifs[build]['name'])
		nome=edifs[build]['name']
		if not nome in auxiliar:
			auxiliar[nome]=building[build]
		else:
			if not building[build] in auxiliar[nome]:
				auxiliar[nome].append(building[build])
		print(auxiliar)
		return json.dumps(auxiliar)
	else:
		return json.dumps("")

@app.route('/admin/campus')
def listCampus():
	URL = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/'
	data = urllib2.urlopen(URL).read()
	return data	#JSON file is parsed later, through javascript

@app.route('/admin/campus/<spaceID>')
def listSpaces(spaceID):
	URL = 'https://fenix.tecnico.ulisboa.pt/api/fenix/v1/spaces/' + spaceID
	data = urllib2.urlopen(URL).read()
	return data	#JSON file is parsed later, through javascript

@app.route('/admin/log', methods=['POST','GET'])
def Log():
	pos={}
	mensagem={}
	def db_get():
		db = Database()
		list=db.msg()
		return list
	mensagem=db_get()
	def db_get():
		list={}
		db=Database()
		list=db.pos()
		return list
	pos=db_get()
	if request.method == 'POST':
		query_params = json.loads(request.data)
		user = query_params['user']
		type = query_params['type']
		print("type", type)
		if type ==0:
			if user in mensagem:
				return json.dumps(mensagem[user]);
			else:
				return json.dumps("");
		if type==1:
			log={}
			aux={}
			print("here")
			for key in mensagem:
				print("here")
				print(mensagem)
				i=0
				while i<len(mensagem[key]):
					print(user)
					print("upa")
					print(mensagem[key][i]['build'])
					print(mensagem[key][i])
					if user == mensagem[key][i]['build']:
						if log == {}:
							log[0]=[mensagem[key][i]]
							print("logo", log)
						else:
							aux=log
							for k in log.keys():
								if not mensagem[key][i] in log[k]:
									#if not key in log:
									#	aux[key]=[log_msg[key][i]]
									#else:
									aux[0].append(mensagem[key][i])
							print(aux)
							log=aux
					i+=1
			print(log)
			return json.dumps(log)
		if type==2:

			print("here1")
			if user in pos:
				print(pos[user])
				return json.dumps(pos[user]);
			else:
				return json.dumps("");
		if type==3:
			log={}
			print("here")
			for key in pos:
				print(pos[key])
				i=0
				while i<len(pos[key]):
					print(user)
					print("upa")

					if 'Entrou' in pos[key][i]:
						print(pos[key][i]['Entrou'])
						if user == pos[key][i]['Entrou']:
							if not key in log:
								log[key]=pos[key][i]
							else:
								log[key].append(pos[key][i])
							print("logo", log)
						 	#return json.dumps(log)
					if 'Saiu' in pos[key][i]:
						print(pos[key][i]['Saiu'])
						if user==pos[key][i]['Saiu']:
							if not key in log:
								log[key]=pos[key][i]
							else:
								log[key].append(pos[key][i])

							print("logo", log)
						 	#return json.dumps(log)
					i+=1
			return json.dumps(log)

@app.route('/login')
def login():
	config = fenixedu.FenixEduConfiguration('288540197912648', 'http://127.0.0.1:5000/user', 'pLVnCmMd0XL72gufsbkG76bMX+wF33C49X9FqkkPw/QE+mCyXUzLARSbpcmFqCUmEIycTfjkDtSYhe2nO1a+9w==', 'https://fenix.tecnico.ulisboa.pt/')
	client = fenixedu.FenixEduClient(config)
	url = client.get_authentication_url()
	return url

@app.route('/user')
def user_t():
	code = request.args.get('code')
	print(code)
	config = fenixedu.FenixEduConfiguration('288540197912648', 'http://127.0.0.1:5000/user', 'pLVnCmMd0XL72gufsbkG76bMX+wF33C49X9FqkkPw/QE+mCyXUzLARSbpcmFqCUmEIycTfjkDtSYhe2nO1a+9w==', 'https://fenix.tecnico.ulisboa.pt/')
	client = fenixedu.FenixEduClient(config)

	user = client.get_user_by_code(code)
	person = client.get_person(user)

	#print(user.access_token)
	print(person['username'])
	print(person['name'])
	#session['access_token'] = user.access_token
	#session['username'] = data['username']

	#return redirect(url_for('index'))
	#if not person['username']) in users_sys:

	#return render_template("user1.html", UserID=person['username'])
	#userID = person['username'], Username = person['name'])
	#Secundário atribuidor de ID Ajudante
	if(1):
		for x in range(1):
			aux=random.randint(1,101)
    	return render_template("user1.html", UserID=aux)

@app.route('/checkedin/<UserID>')
def checkin(UserID):
	def db_query(sql,val):
        	db = Database()
        	db.query(sql,val)
	####Adicionar verificação
	print(UserID)
	sql = "INSERT INTO user (ID, username) VALUES (%s,%s)"
	val = (UserID,str(UserID))
	db_query(sql,val)
	users_sys[UserID]={'id': UserID, 'username': 'user'+str(UserID)}
	print(users_sys)
	aux2.Adduser(UserID)
	return "Added"

#Not yet used
@app.route('/checkout/<UserID>')
def checkout(UserID):
	print(UserID)
	del users_sys[UserID]
	# delete de usersList
	# fazer o user sair do Edificío de onde esta
	#delete de mais algo? ver em ultimo lugar
	print(users_sys)
	return "deleted"

#TODO
#@app.route('/Bot/GetPendingBots')
#@app.route('/Bot/AcceptBot/<BotKey>')  pendingBots.delete(keyBot)


@app.route('/Bot/PendingBots', methods=['GET'])
def List_Bot():
	x={}
	y={}
	print(pendingBots)
	print(acceptedBots)
	x=acceptedBots.copy()
	y=pendingBots.copy()
	x.update(y)
	print(x)
	return json.dumps(pendingBots)

@app.route('/Bot/registry', methods=['POST','GET'])
def Registry_Bot():
	edifs={}
	def db_query():
        	db = Database()
		list=db.builds()
		return list
	if request.method == 'POST':
		query_params = json.loads(request.data)
		b_name = query_params['Build_name']
		edifs=db_query()
		print(edifs)
		build_id="O Edificio escolhido não existe"
		for key, value in edifs.iteritems():
			if b_name ==edifs[key]['name']:
				build_id=key
		hash_id = query_params['Botkey']
		print(build_id)
		pack ={'Build_ID':build_id, 'B_name':b_name}
		if build_id !="O Edificio escolhido não existe":
			pendingBots[hash_id]=pack
		print("aqui")
		print(pendingBots)
		print(hash_id)
		print(b_name)
		#pack ={'Bot':bot}
		if build_id=="O Edificio escolhido não existe":
			return json.dumps(build_id)
		else:
			return json.dumps("O Edificio escolhido existe")
	if request.method == 'GET':
		print("enviado")
		if pendingBots== {}:
			return json.dumps("Não existem Bots em fila de espera")
		else:
			return json.dumps(pendingBots)

@app.route('/Bot/AcceptBot', methods=['POST','GET'])
def Bind():
	if request.method == 'POST':
		query_params = json.loads(request.data)
		hash_id = int(query_params['Botkey'])
		print(hash_id)
		print(pendingBots[hash_id])
		acceptedBots[hash_id]=pendingBots[hash_id]
		del pendingBots[hash_id]
		print(pendingBots)
		print(acceptedBots)
		return json.dumps("")
	if request.method == 'GET':
		return json.dumps(acceptedBots)

@app.route('/Bot/message', methods=['POST'])
def Message_Bot():
	if request.method == 'POST':
		query_params = json.loads(request.data)
		sender = int(query_params['BotID'])
		message = query_params['message']
		b_id = int(query_params['build_id'])
		user_location = query_params['user_loc']
		pack = {'sender': "BOT"+str(sender), 'message': message, 'build': user_location, 'timestamp': time.time()}
		print('BOT:', str(query_params['BotID']), 'sent message: ', str(query_params['message']))
		indexbuildings = getbuildingID();
		print(indexbuildings)
		aux=getUsersindabuilding(b_id)
		# propósitos de debug
		print("aux:")
		print(aux)
		if b_id in indexbuildings:
			print("BOT disse isto:")
			print(message)
		else:
			print("Erro")
		#Mensagem proveniente de Bots
		if aux != None:
			for b_id in indexbuildings:
				for receiver in aux:
					print(receiver)
					if not receiver in msgQueue:
							msgQueue[receiver]=[pack]
					else:
							msgQueue[receiver].append(pack)
		print(msgQueue)
	return ''

@app.route('/user/message', methods=['POST'])
def Message():
	queue={}
	def db_getfila():
		db = Database()
		list=db.msg_queue()
		return list
	def db_query(sql,val):
        	db = Database()
        	db.query(sql,val)
	def db_get():
		db = Database()
		list=db.msg()
		return list
	mensagem=db_get()
	print(mensagem)
	print("verificar")
	print(log_msg)
	queue=db_getfila()
	if request.method == 'POST':
		query_params = json.loads(request.data)
		sender = query_params['user_id']
		message = query_params['message']
		user_location = query_params['user_loc']
		radius= int(query_params['range'])
		pack = {'sender': sender, 'message': message, 'build': user_location, 'timestamp': time.time()}
		print('User:', str(query_params['user_id']), 'sent message: ', str(query_params['message']))
		nearbyUsers = calculateNearbyUsers(sender, radius)
		print(nearbyUsers)
		#Guardar mensagens enviadas
		#Adicionar localização e aglomerar todo o grupo de mensagens
		#if not sender in mensagem:
		if pack !=None:
			#log_msg[sender]=[pack]
			sql = "INSERT INTO msg (ID,build,instante,Remetente,mensagem) VALUES (%s,%s,%s,%s,%s)"
			val = (sender,user_location,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),sender,message)
			db_query(sql,val)
		print("logmsg")
		print(log_msg)
		#else:
		#		if pack !=None:
		#			log_msg[sender].append(pack)
		#			sql = "INSERT INTO msg (ID,build,instante,Remetente,mensagem) VALUES (%s,%s,%s,%s,%s)"
		#			val = (sender,user_location,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),sender,message)
		#			db_query(sql,val)
		#		print("logmsg")
		#		print(log_msg)
		#Mensagem proveniente de Utilizadores por perto
	 	for nearbyUser in nearbyUsers:
				msgQueue[nearbyUser]=[pack]
				if not nearbyUser in queue:
					sql = "INSERT INTO msgfila (ID,build,instante,Remetente,mensagem) VALUES (%s,%s,%s,%s,%s)"
					val = (nearbyUser,pack['build'],time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(pack['timestamp'])),pack['sender'],message)
					db_query(sql,val)
				#fila de espera msgs
					msgQueue[nearbyUser].append(pack)
				elif nearbyUser in queue:
					sql ="UPDATE msgfila SET build = %s, mensagem=%s, instante=%s, Remetente=%s WHERE ID =%s"
					val = (user_location,pack['message'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(pack['timestamp'])),pack['sender'],nearbyUser)
					db_query(sql,val)
				#fila de espera msgs
		print(msgQueue)
	return ''


@app.route('/user/getMessages', methods=['POST'])
def userMessage():
	mensagem={}
	queue={}
	def db_query(sql,val):
        	db = Database()
        	db.query(sql,val)
	def db_get():
		db = Database()
		list=db.msg()
		return list
	def db_getfila():
		db = Database()
		list=db.msg_queue()
		return list
	queue=db_getfila()
	mensagem=db_get()
	print(queue)
	print("verificar")
	print(msgQueue)
	if request.method == 'POST':
		query_params = json.loads(request.data)
		user_id = query_params['user_id']
		user_location = query_params['user_loc']
		msg = []
		if user_id in queue:
			msg = queue[user_id]
			print("fila")
			print(msgQueue)
			print(msg)
			if msg:
				i=0
				#if not user_id in mensagem:
				while i < len(msg):
					#Adicionar a localização {sender:'',message:'', building:''}
					#fazer um post do lado do javascript com o Build(name)
					if msg[i] !=None:
						log_msg[user_id]=[msg[i]]
						sql = "INSERT INTO msg (ID,build,instante,Remetente,mensagem) VALUES (%s,%s,%s,%s,%s)"
						val = (user_id,user_location,msg[i]['timestamp'],msg[i]['sender'],msg[i]['message'])
						db_query(sql,val)
					print("log1")
					print(log_msg)
					i+=1
				#else:
				#	while i<len(msg):
				#		pack=msg[i]
				#		print(msg[i])
				#		print("log1")
				#		if msg[i] !=None:
				#			log_msg[user_id].append(msg[i])
				#			sql = "INSERT INTO msg (ID,build,instante,Remetente,mensagem) VALUES (%s,%s,%s,%s,%s)"
				#			val = (user_id,user_location,msg[i]['timestamp'],msg[i]['sender'],msg[i]['message'])
				#			db_query(sql,val)
				#		print(log_msg)
				#		i+=1
			msgQueue[user_id] = []
			print(user_id)
			sql ="DELETE from msgfila WHERE ID = %s"
			val = (user_id,)
			db_query(sql,val)
			#fazer delete da memchached

	return json.dumps(msg)

@app.route('/user/nearby', methods=['POST'])
def nearbyUsers():
	if request.method == 'POST':
		query_params = json.loads(request.data)
		radius= int(query_params['range'])
		print(radius)
		print('Get users nearby User: ' + str(query_params['user_id']))
		nearby = calculateNearbyUsers(query_params['user_id'], radius)
		jsonUsers = {}
		for userID in nearby:
			jsonUsers[userID] = {'id': userID, 'username': 'user'+str(userID)}
		#return ','.join(nearby)
		return json.dumps(jsonUsers)
	return 'error'

@app.route('/user/location', methods=['POST'])
def selflocation():
	user={}
	log_pos={}
	def db_query(sql,val):
        	db = Database()
        	db.query(sql,val)
	def db_query2():
        	db = Database()
		list=db.users()
		return list
	def db_get():
		list={}
		db=Database()
		list=db.pos()
		return list
	def updateUser(userID, lon,lat, local):
		#global usersList
		user=db_query2()
		#print(user)
		if not userID in user:
			sql = "INSERT INTO user_loc (ID,latitude, longitude,local) VALUES (%s,%s,%s,%s)"
			val = (userID,lat,lon,local)
			db_query(sql,val)
		else:
			sql ="UPDATE user_loc SET latitude = %s, longitude=%s, local=%s WHERE ID =%s"
			val = (lat,lon,local, userID)
			db_query(sql,val)
		usersList[userID] = {'lat' : lat , 'lon' : lon, 'local': local}
	if request.method == 'POST':
		query_params = json.loads(request.data)
		uid=query_params['user_id']
		user_location = query_params['user_loc']
		print('User: ' + str(query_params['user_id']))
		#print('Lon: ' + str(query_params['lon']))
		#print('Lat: ' + str(query_params['lat']))
		pos=db_get()
		init= {'Entrou': user_location, 'timestamp': time.time()}
		pacote= {'Entrou': user_location, 'timestamp': time.time()}
		print(pos)
		print("São iguais")
		print(log_pos)
		# É preciso Focus na tab
		if user_location=="Fora de Edificios definidos":
			if not uid in pos:
				#log_pos[uid]=[init]
				sql = "INSERT INTO pos (ID,local,instante,type) VALUES (%s,%s,%s,%s)"
				val = (uid,user_location,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),1)
				db_query(sql,val)
		else:
			if pacote['Entrou'] !="":
				if not uid in pos:
					#log_pos[uid]=[pacote]
					sql = "INSERT INTO pos (ID,local,instante,type) VALUES (%s,%s,%s,%s)"
					val = (uid,user_location,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),1)
					db_query(sql,val)
				else:
					#propósitos de debug
					print("helper")
					if 'Entrou' in pos[uid][len(pos[uid])-1]:
						if pos[uid][len(pos[uid])-1]['Entrou'] =="Fora de Edificios definidos":
							print("aqui")
							pacoteout= {'Saiu':pos[uid][len(pos[uid])-1]['Entrou'], 'timestamp': time.time()}
							sql = "INSERT INTO pos (ID,local,instante,type) VALUES (%s,%s,%s,%s)"
							val = (uid,pos[uid][len(pos[uid])-1]['Entrou'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),0)
							#log_pos[uid].append(pacoteout)
							db_query(sql,val)

						elif (user_location != pos[uid][len(pos[uid])-1]['Entrou']) and (user_location!="Fora de Edificios definidos") :
							pacoteout= {'Saiu':pos[uid][len(pos[uid])-1]['Entrou'], 'timestamp': time.time()}
							sql = "INSERT INTO pos (ID,local,instante,type) VALUES (%s,%s,%s,%s)"
							val = (uid,pos[uid][len(pos[uid])-1]['Entrou'],time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),0)
							db_query(sql,val)
							#log_pos[uid].append(pacoteout)
							print(pos[uid][len(pos[uid])-1])
							#fazer um delete do u_in_b
							sql="DELETE FROM userbuild WHERE uID = %s"
							val=(uid)
							db_query(sql,val)
					if ('Saiu' in pos[uid][len(pos[uid])-1]) and user_location !="Fora de Edificios definidos":
						print("saiu")
						#log_pos[uid].append(pacote)
						sql = "INSERT INTO pos (ID,local,instante,type) VALUES (%s,%s,%s,%s)"
						val = (uid,user_location,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),1)
						db_query(sql,val)

		print("log2")
		print(log_pos)
		updateUser(query_params['user_id'], query_params['lon'], query_params['lat'], query_params['user_loc'])
	return "Added"

@app.route('/user/building/<UserID>', methods=['GET'])
def inbuild(UserID):
	edifs={}
	def db_query():
        	db = Database()
		list=db.builds()
		return list
	edifs=db_query()
	packet={'id': UserID}
	buildings=whichbuilding(UserID)
	building=buildings
	print(buildings)
	for build in buildings:
		print(buildings[build])
		if packet in buildings[build]:
			auxiliar={}
			print(build)
			print(edifs[build]['name'])
			nome=edifs[build]['name']
			if not nome in auxiliar:
				auxiliar[nome]=buildings[build]
			else:
				if not buildings[build] in auxiliar[nome]:
					auxiliar[nome].append(buildings[build])
			print(auxiliar)
			return json.dumps(edifs[build]['name'])
		else:
			return json.dumps("")
	return json.dumps("")

if __name__ == '__main__':
    app.run(debug=True)
