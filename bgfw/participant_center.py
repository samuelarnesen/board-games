from participant import Participant
from piece_center import Piece_Center

import copy

class Participant_Center(Piece_Center):

	def __init__(self):
		
		super().__init__(recognized_piece_types=[Participant("filler")])


	def get_participants(self):

		""" gets a list of all the participants """

		return self.get_pieces()

	def add_participant(self, name):

		""" adds a participant to the participant list """

		self.add_piece(Participant(name=name))

	def get_participant_by_name(self, name):

		""" gets a specific participant by its name """

		return self.get_individual_piece({"name": name})

	def sort_participants_by_attribute(self, sorting_attribute, reverse=False):

		""" sorts participants by the specified attribute """

		return self.sort_pieces_by_attribute(sorting_attribute, {}, reverse)

	def shuffle_participants(self):

		""" gets participants in a random order """

		return self.shuffle_pieces({})



