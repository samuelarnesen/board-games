import copy

class Constraint:

	def __init__(self, attributes, constrained_attribute=None, min_value=-1, max_value=float("inf")):

		self.__attributes = copy.deepcopy(attributes)
		self.__constrained_attribute = constrained_attribute
		self.__min_value = min_value
		self.__max_value = max_value

	def get_attributes(self):

		""" gets the maximum value allowed on the subgroup """

		return self.__attributes

	def get_min_value(self):

		""" gets the maximum value allowed on the subgroup """

		return self.__min_value

	def get_max_value(self):

		""" gets the maximum value allowed on the subgroup """

		return self.__max_value

	def get_constrained_attribute(self):

		""" gets the attribute that the constraint is applied on """

		return self.__constrained_attribute

	def meets_constraints(self, subgroup):

		""" checks if a given subgroup matches the criteria set by the constraint """

		for item in subgroup:
			if self.get_constrained_attribute() not in item.get_attributes():
				raise KeyError("Constraint does not apply to specified subgroup. At least 1 member is missing the {} attribute".format(self.get_constrained_attribute()))
			for attribute in self.get_attributes():
				if attribute not in item.get_attributes():
					raise KeyError("Constraint does not apply to specified subgroup. At least 1 member is missing the {} attribute".format(attribute))

		if self.get_constrained_attribute() == None:
			return len(subgroup) >= self.get_min_value() and len(subgroup) <= self.get_max_value()

		for item in subgroup:
			if item.get_attribute(self.get_constrained_attribute()) < self.get_min_value() or item.get_attribute(self.get_constrained_attribute()) > self.get_max_value():
				return False

		return True

	def refers_to_same_group(self, other, constrained_attribute=None):

		""" checks if two constraints are applied on the same subgroup -- other can be a dictionary of attributes or a constraint"""

		other_attribute_group = other.get_attributes() if isinstance(other, Constraint) else other

		for attribute in other_attribute_group:
			if attribute not in self.get_attributes():
				return False

		return other.get_constrained_attribute() == self.get_constrained_attribute()

