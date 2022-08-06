import random, copy

class Piece:

	def __init__(self, type_name="Generic_Piece", uid=None, name=None, owner=None, attributes=None):

		self.__attributes = attributes if attributes != None else {}
		self.__attributes["uid"] = uid if uid != None else self.__generate_uid()
		self.__attributes["name"] = name
		self.__attributes["owner"] = owner
		self.__attributes["type name"] = type_name

		self.__rollback_attributes = {}

	def __str__(self):

		if self.get_attribute("name") != None:
			return self.get_attribute("name")

		string_rep = ""
		for attribute in self.get_attributes():
			string_rep += "{}: {}\n".format(str(attribute), str(self.get_attribute(attribute)))

		return string_rep

	def __generate_uid(self):
		return random.randrange(1e10)

	def contains_attribute(self, attribute):

		""" returns whether or not the piece has a specific attribute """

		return attribute in self.__attributes

	def get_attributes(self):

		""" returns a list of all the attributes the piece contains (but not their values) """

		return [attribute for attribute in self.__attributes]

	def get_attribute(self, attribute):

		""" returns the value associated with the particular attribute (returns None if inputted attribute is not a piece attribute) """

		if not self.contains_attribute(attribute):
			return None

		return self.__attributes[attribute]

	def set_attribute(self, attribute, value, tentative=False):

		""" updates an attribute value """

		if tentative and attribute not in self.__rollback_attributes:
			self.__rollback_attributes[attribute] = self.get_attribute(attribute)

		self.__attributes[attribute] = value

	def rollback_attribute(self, attribute):

		""" rolls back an attribute to last committed value """

		if attribute in self.__rollback_attributes:
			self.set_attribute(attribute, self.__rollback_attributes[attribute], tentative=False)
			del self.__rollback_attributes[attribute]

	def rollback_all_attributes(self):

		""" rolls back all the attributes of the piece to their last committed values """

		for attribute in self.get_attributes():
			self.rollback_attribute(attribute)

	def commit_attribute(self, attribute):

		""" marks a changed attribute as committed """

		if attribute not in self.__attributes:
			raise KeyError("{} is not an attribute of this piece".format(attribute))

		if attribute in self.__rollback_attributes:
			del self.__rollback_attributes[attribute]

	def commit_all_attributes(self):

		""" commits all the attributes of the piece """

		for attribute in self.get_attributes():
			self.commit_attribute(attribute)

	def is_tentative(self, attribute):

		""" checks if an attribute is tentative or committed"""

		if attribute not in self.__attributes:
			raise KeyError("{} is not an attribute of this piece".format(attribute))

		return attribute in self.__rollback_attributes

	def clone(self, new_id=True):

		cloned_copy = copy.deepcopy(self)
		cloned_copy.set_attribute("uid", self.__generate_uid())
		return cloned_copy






