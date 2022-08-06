from piece import Piece
import json, copy, random

class Piece_Center:

	def __init__(self, pieces=None, recognized_piece_types=None):

		if not isinstance(pieces, list) and pieces != None:
			raise TypeError("pieces argument must be of type list, was instead {}".format(type(pieces)))

		self.__pieces = pieces if pieces != None else []
		self.__recognized_piece_types = recognized_piece_types if recognized_piece_types != None else [Piece()]

	def get_pieces(self):

		""" gets a list of all the pieces """

		return self.__pieces

	def add_piece(self, piece):

		""" adds a piece to the list of pieces """

		if self.get_recognized_piece_type(piece) == None:
			raise TypeError("Piece type is not valid")

		self.__pieces.append(piece)

	def get_recognized_types(self):

		""" returns all the piece types that are recognized """

		return self.__recognized_piece_types

	def get_recognized_piece_type(self, piece):

		""" checks if the piece (a string of the type name or an instantiation of a piece) is a recognized type """

		piece_type = piece.get_attribute("type name") if isinstance(piece, Piece) else piece
		for recognized_piece_type in self.get_recognized_types():
			if piece_type == recognized_piece_type.get_attribute("type name"):
				return recognized_piece_type

		return None

	def add_piece_type(self, added_type):

		""" allow a piece type to be recognized by the game engine for loading from a config file """

		if not issubclass(type(added_type), Piece):
			raise TypeError("Added type must be a Piece")
		
		self.__recognized_piece_types.append((added_type))

	def load_pieces_from_json(self, json_filepath: str):

		""" reads json file of all the pieces and converts them into Piece objects """

		with open(json_filepath) as f:
			decoded = json.load(f)

		if type(decoded) != dict:
			raise TypeError("Inputted file was in the wrong format -- should be a dictionary of piece types, instead was a {}".format(type(decoded)))
		
		for piece_type in decoded:

			if type(decoded[piece_type]) != list:
				raise TypeError("Inputted file was in the wrong format -- each piece type should be associated with a list, instead was with a {}".format(type(decoded[piece_type])))

			matched_piece = self.get_recognized_piece_type(piece_type)
			if matched_piece == None:
				matched_piece = Piece()

			for piece in decoded[piece_type]:

				piece_to_create = copy.deepcopy(matched_piece)
				piece_to_create.set_attribute("type name", piece_type)
				for attribute in filter(lambda x: x != "Duplicate", piece):
					piece_to_create.set_attribute(attribute, piece[attribute])

				duplicates = 1 if "Duplicate" not in piece else piece["Duplicate"]
				for i in range(duplicates):
					new_piece = piece_to_create.clone()
					self.__pieces.append(new_piece)

	def sort_pieces_by_attribute(self, sorting_attribute, attributes, reverse=False):

		""" sorts the pieces that match the filter by the sorting attribute """

		eligible_pieces = self.get_pieces_by_filter(attributes)
		for piece in eligible_pieces:
			if not piece.contains_attribute(sorting_attribute):
				raise KeyError("Not all the relevant pieces have attribute {}".format(sorting_attribute))

		eligible_pieces.sort(key=lambda x:x.get_attribute(sorting_attribute), reverse=reverse)
		return eligible_pieces


	def get_pieces_by_filter(self, attributes: dict):

		""" returns all the pieces that match all the specified attributes """

		filtered_pieces = []
		for piece in self.__pieces:
			matches = True
			for attribute in attributes:
				if piece.get_attribute(attribute) != attributes[attribute]:
					matches = False
			if matches:
				filtered_pieces.append(piece)

		return filtered_pieces

	def get_individual_piece(self, attributes: dict):

		""" gets an individual piece """

		filtered_pieces = self.get_pieces_by_filter(attributes)

		if len(filtered_pieces) != 1:
			raise TypeError("Inputted attributes did not match exactly one piece. Instead matched {} pieces".format(len(filtered_pieces)))

		return filtered_pieces[0]

	def commit_pieces_by_filter(self, attributes: dict):

		""" commits the attribute changes on all the pieces that match the filter """

		matching_pieces = self.get_pieces_by_filter(attributes)
		for piece in matching_pieces:
			piece.commit_all_attributes()

	def rollback_pieces_by_filter(self, attributes: dict):

		""" rolls back the attribute changes on all the pieces that match the filter """

		matching_pieces = self.get_pieces_by_filter(attributes)
		for piece in matching_pieces:
			piece.rollback_all_attributes()

	def commit_all_pieces(self):

		""" commits the attribute changes on all the pieces """

		self.commit_pieces_by_filter(attributes={})

	def rollback_all_pieces(self):

		""" rolls back the attribute changes on all the pieces """

		self.rollback_pieces_by_filter(attributes={})

	def commit_attribute_on_pieces_by_filter(self, attributes, attribute):

		""" commits a specific attribute on all the pieces that match a filter """
		
		matching_pieces = self.get_pieces_by_filter(attributes)
		for piece in matching_pieces:
			piece.commit_attribute(attribute)

	def rollback_attribute_on_pieces_by_filter(self, attributes, attribute):

		""" rolls back a specific attribute on all the pieces that match a filter """

		matching_pieces = self.get_pieces_by_filter(attributes)
		for piece in matching_pieces:
			piece.rollback_attribute(attribute)

	def shuffle_pieces(self, attributes):

		""" gets pieces by attributes and shuffles """

		relevant_pieces = self.get_pieces_by_filter(attributes)
		random.shuffle(relevant_pieces)
		return relevant_pieces










