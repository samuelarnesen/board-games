from piece_center import Piece_Center
from constraint_center import Constraint_Center
from participant_center import Participant_Center
from input_center import Input_Center

import functools, copy

class GameEngine:

	def __init__(self):

		self.__piece_center = Piece_Center()
		self.__participant_center = Participant_Center()
		self.__constraint_center = Constraint_Center()
		self.__input_center = Input_Center()

	def get_participants(self):

		""" returns a list of all the participants """

		return self.__participant_center.get_participants()

	def get_participant_by_name(self, name):

		""" returns the single participant that has that name"""

		return self.__participant_center.get_participant_by_name(name)

	def get_pieces(self):

		""" gets a list of all the pieces """

		return self.__piece_center.get_pieces()


	def get_pieces_by_filter(self, attributes: dict):

		""" returns all the pieces that match all the specified attributes """

		return self.__piece_center.get_pieces_by_filter(attributes)

	def sort_pieces_by_attribute(self, sorting_attribute, attributes, reverse=False):

		""" sorts the pieces that match the filter by the sorting attribute """

		return self.__piece_center.sort_pieces_by_attribute(sorting_attribute, attributes, reverse)

	def sort_participants_by_attribute(self, sorting_attribute, reverse=False):

		""" sorts participants by the specified attribute """

		return self.participant_center.sort_pieces_by_attribute(sorting_attribute, reverse)


	def add_participant(self, participant):

		""" adds a participant (player in the game) """

		self.__participant_center.add_participant(participant)

	def add_participant_from_json(self, json_filepath: str):

		""" reads json file of all the participants and converts them into Participant objects """

		self.__participant_center.load_pieces_from_json(json_filepath)

	def add_piece(self, piece):

		""" adds a piece to the list of pieces """

		self.__piece_center.add_piece(piece)

	def add_piece_type(self, added_type):

		""" allow a piece type to be recognized by the game engine for loading from a config file """

		self.__piece_center.add_piece_type(added_type)

	def load_pieces_from_json(self, json_filepath: str):

		""" reads json file of all the pieces and converts them into Piece objects """

		self.__piece_center.load_pieces_from_json(json_filepath)

	def apply_constraint_to_pieces(self, attributes, constrained_attribute=None, min_value=-1, max_value=float("inf")):

		""" adds a constraint to the game state """

		self.__constraint_center.add_constraint(attributes, constrained_attribute, min_value, max_value)

	def apply_constraint_to_participants(self, constrained_attribute, min_value=-1, max_value=float("inf")):

		""" applying constraints on pieces owned by each participant -- None means the value of the group is what's constrained"""

		attributes = {"type name": "Participant"}
		self.apply_constraint_to_pieces(attributes, constrained_attribute, min_value, max_value)

	def remove_constraint_from_pieces(self, attributes, constrained_attribute=None):

		""" removes constraint from the pieces """

		self.__constraint_center.remove_constraint(attributes, constrained_attribute)

	def remove_constraint_from_participants(self, constrained_attribute):

		""" removes constraints from pieces owned by a participant """

		attributes = {"type name": "Participant"}
		self.remove_constraint_from_pieces(attributes, constrained_attribute)

	def add_input_response(self, label, trigger_func, func):

		""" maps an identifying function to a function to be executed when that condition is met -- label identifies the pair"""

		self.__input_center.add_input_response(label, trigger_func, func)

	def add_unknown_input_response(self, func, *argv):

		""" registers the function to be called when an inputted command is not recognized """

		self.__input_center.add_unknown_input_response(func, argv)

	def listen(self, labels, end_label="", max_commands=float("inf"), inputer=None):

		""" listens for the specified inputs and executes their associated commands """

		self.__input_center.listen(labels, end_label, max_commands, inputer)

	def get_individual_piece(self, attributes: dict):

		""" gets an individual piece """

		return self.__piece_center.get_individual_piece(attributes)

	def commit_pieces_by_filter(self, attributes: dict):

		""" commits the attribute changes on all the pieces that match the filter """

		self.__piece_center.commit_pieces_by_filter(attributes)

	def rollback_pieces_by_filter(self, attributes: dict):

		""" rolls back the attribute changes on all the pieces that match the filter """

		self.__piece_center.rollback_pieces_by_filter(attributes)

	def commit_all_pieces(self):

		""" commits the attribute changes on all the pieces """

		self.__piece_center.commit_all_pieces()

	def rollback_all_pieces(self):

		""" rolls back the attribute changes on all the pieces """

		self.__piece_center.rollback_all_pieces()

	def commit_attribute_on_pieces_by_filter(self, attributes, attribute):

		""" commits a specific attribute on all the pieces that match a filter """
		
		self.__piece_center.commit_attribute_on_pieces_by_filter(attributes, attribute)

	def rollback_attribute_on_pieces_by_filter(self, attributes, attribute):

		""" rolls back a specific attribute on all the pieces that match a filter """

		self.__piece_center.rollback_attribute_on_pieces_by_filter(attributes, attribute)

	def check_all_constraints(self, commit=False, rollback=False):

		""" checks if the constraints on the game state are met -- commits if all good (if marked True), else rolls back (if marked True)"""
		satisfied = self.__constraint_center.all_constraints_satisfied(self.__piece_center) and \
				self.__constraint_center.all_constraints_satisfied(self.__participant_center)
		if commit and satisfied:
			self.commit_all_pieces()
		elif rollback and not satisfied:
			self.rollback_all_pieces()
		return satisfied

	def two_phase_commit(func):

		""" decorator that rolls back all changes if constraints fail, otherwise commits """

		@functools.wraps(func)
		def run_then_check(self, *args, **kwargs):
			function_result = func(self, *args, **kwargs)
			self.check_all_constraints(commit=True, rollback=True)
			return function_result
		return run_then_check

	def no_fail(execution_mode=False):

		""" simple try-except decorator """

		def decorator_try_except(func):

			@functools.wraps(func)
			def try_except(*args, **kwargs):
				try:
					function_result = func(*args, **kwargs)
					return function_result
				except:
					if execution_mode:
						print("Error! Execution failed")
						return None, False
					else:
						return False
			return try_except

		return decorator_try_except


	def shuffle_pieces(self, attributes):

		""" gets pieces by attributes and shuffles """

		return self.__piece_center.shuffle_pieces(attributes)

	def shuffle_participants(self):

		""" gets participants in a random order """

		return self.__participant_center.shuffle_participants()
