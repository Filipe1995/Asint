import json
import builds
import os.path

class Savelocal:
	def __init__(self):
		if(os.path.isfile('location')):
			self.data={}
		else:
    			f = open('location', 'a+')
			self.data=[]
			json.dump(self.data,f)

	def Addlocal(self,UserID,lat,long):
		data={'ID':UserID,'Lat': lat, 'Long':long}
		with open('location', 'r') as feedjson:
				feed=json.load(feedjson)
		with open('location', 'w') as feedjson2:
				feed.append(data)
        			json.dump(feed, feedjson2)
