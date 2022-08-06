from enum import Enum

class Side(Enum):
	GOOD = "good"
	BAD = "bad"
	DEFAULT = "default"

class Role(Enum):
	KNIGHT = "knight"
	MINION = "minion"
	PERCIVAL = "percival"
	MORGANA = "morgana"
	ASSASSIN = "assassin"
	MERLIN = "merlin"
	DEFAULT = "default"

	@staticmethod
	def get_side_from_role(role):

		assert type(role) == Role

		if role == Role.DEFAULT:
			return Side.DEFAULT
		elif role in [Role.KNIGHT, Role.PERCIVAL, Role.MERLIN]:
			return Side.GOOD
		else:
			return Side.BAD

	@staticmethod
	def is_special(role):

		assert type(role) == Role

		return role in [Role.PERCIVAL, Role.MERLIN, Role.MORGANA, Role.MINION, Role.ASSASSIN]

