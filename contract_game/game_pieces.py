import sys
sys.path.insert(1, "/Users/samuelarnesen/Desktop/projects/bgfw")
from piece import Piece

class Contract_Card(Piece):

	def __init__(self):
		super().__init__(type_name="Contract Card")

	def __str__(self):
		
		if self.get_attribute("Auction Type") == "Cournot":
			rep = "Type: Cournot\nCommodity: {}\nPrice: {}-{}q\n".format(self.get_attribute("Commodity"), self.get_attribute("Base Price"), 
				self.get_attribute("Multiplier"))

		else:
			rep = "Type: Exclusive\nCommodity: {}\nQuantity: {}\n".format(self.get_attribute("Commodity"), self.get_attribute("Quantity"))

		return rep

class City_Card(Piece):

	def __init__(self):
		super().__init__(type_name="City Card")

	def __str__(self):

		return "City: {}".format(self.get_attribute("City"))


class Unit(Piece):

	def __init__(self):
		super().__init__(type_name="Unit")

	def __str__(self):

		rep = "Name: {} ({})\nRegion: {}\nAgriculture: {}\nAnimals: {}\nEnergy: {}\nMetals: {}\n".format(self.get_attribute("name"), 
			self.get_attribute("Unit ID"), self.get_attribute("Region"),  self.get_attribute("Agriculture"), self.get_attribute("Animals"), 
			self.get_attribute("Energy"), self.get_attribute("Metals"))

		rep += "Adjacent Cities: " + ", ".join(self.get_attribute("Adjacent Cities")) + "\n"

		return rep