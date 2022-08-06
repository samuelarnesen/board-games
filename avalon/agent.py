from roles import Side, Role
import random

class Agent:

	def __init__(self, role=None, id_num=-1):
		
		self.__role = role if role != None else Role.DEFAULT
		self.__side = Role.get_side_from_role(self.get_role())
		self.__id_num = id_num

		self.__known_bad_guys = None
		self.__merlins_or_morgana = None

	def set_role(self, role):

		assert type(role) == Role

		self.__role = role
		self.__side = Role.get_side_from_role(role)

	def get_side(self):

		return self.__side

	def get_role(self):

		return self.__role

	def set_id_num(self):

		return self.__id_num

	def get_id_num(self):

		return self.__id_num

	def select_mission_to_go_forward(self, number_of_people_on_mission, previous_state=None):

		return random.sample(range(7), k=number_of_people_on_mission)

	def vote_on_mission_going_forward(self, proposal, previous_state=None):

		return True if random.random() > 0.5 else False

	def vote_on_mission_success(self, people_on_mission, previous_state=None):

		return self.__side == Side.GOOD

	def identify_merlin(self, previous_state=None):

		assert self.get_role() == Role.ASSASSIN

		return random.randint(0, 7)

	def reveal_bad_guys(self, bad_guy_idxs):

		assert self.get_role() in [Role.ASSASSIN, Role.MINION, Role.MORGANA, Role.MERLIN]

		self.__known_bad_guys = [idx for idx in bad_guy_idxs]

	def reveal_merlin_or_morgana(self, possible_idxs):

		assert self.get_role() == Role.PERCIVAL

		self.__merlins_or_morgana = [idx for idx in possible_idxs]






