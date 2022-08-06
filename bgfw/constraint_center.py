from constraint import Constraint

class Constraint_Center:

	def __init__(self):

		self.__constraints = []

	def get_constraints(self):

		""" fetches all the constraints on the game state """

		return self.__constraints

	def get_constraint(self, attributes, constrained_attribute):

		""" gets a constraint that refers to that attribute group (or constraint)"""

		for constraint in self.get_constraints():
			if constraint.refers_to_same_group(attributes, constrained_attribute=None):
				return constraint

		return None

	def all_constraints_satisfied(self, piece_center):

		""" checks the game state to see if all the constraints are met """

		for constraint in self.get_constraints():

			constraint_attributes = constraint.get_attributes()
			subgroup = piece_center.get_pieces_by_filter(constraint_attributes)
			if not constraint.meets_constraints(subgroup):
				return False

		return True

	def matches_existing_constraint(self, testing_constraint, constrained_attribute=None):

		""" checks if a constraint refers to the same subgroup as an existing constraint """

		return self.get_constraint(testing_constraint, constrained_attribute) != None

	def add_constraint(self, attributes, constrained_attribute=None, min_value=-1, max_value=float("inf")):

		""" adds a constraint to the overall list of system constraints """

		constraint = Constraint(attributes, constrained_attribute, min_value, max_value)

		if self.matches_existing_constraint(constraint, constrained_attribute):
			raise ValueError("Constraint duplicates an existing constraint")

		self.__constraints.append(constraint)

	def remove_constraint(self, attributes, constrained_attribute=None):

		""" removes a constraint with the given attributes (can also be a constraint) """

		constraint_to_remove = self.get_constraint(attributes, constrained_attribute)
		if constraint_to_remove == None:
			raise KeyError("No such constraint exists")
		self.__constraints.remove(constraint_to_remove)

