class builds:
	def __init__(self,buildingID,buildingname,buildinglat,buildinglong):
		self.buildingID=buildingID
		self.buildingname=buildingname
		self.buildinglat=buildinglat
		self.buildinglong=buildinglong
	def __str__(self):
		return "%s - %s - %s - %s" % (self.buildingID, self.buildingname, self.buildinglat, self.buildinglong)
