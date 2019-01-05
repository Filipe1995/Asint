import json
import builds
import os.path

class SaveUsers:
	def __init__(self):
		if(os.path.isfile('Users')):
			self.data={}
		else:
    			f = open('Users', 'a+')
			self.data=[]
			json.dump(self.data,f)

	def Adduser(self,UserID):
		data={'ID': UserID}
		with open('Users', 'r') as feedjson:
				feed=json.load(feedjson)
		with open('Users', 'w') as feedjson2:
				feed.append(data)
        			json.dump(feed, feedjson2)
