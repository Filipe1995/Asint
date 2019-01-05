import json
import builds
import os.path

class SaveBuilds:
	def __init__(self):
		if(os.path.isfile('Buildings')):
			self.data={}
		else:
    			f = open('Buildings', 'a+')
			self.data=[]
			json.dump(self.data,f)

	def AddBuilding(self,buildingID,buildingname,buildinglat,buildinglong):
		data={'ID': buildingID, 'Nome': buildingname, 'Latitude': buildingID,'Longitude': buildinglong}
		with open('Buildings', 'r') as feedjson:
				feed=json.load(feedjson)
		with open('Buildings', 'w') as feedjson2:
				feed.append(data)
        			json.dump(feed, feedjson2)
