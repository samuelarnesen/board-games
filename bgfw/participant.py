from piece import Piece

class Participant(Piece):

	def __init__(self, name):

		super().__init__(name=name, type_name="Participant")

	def poll(self):

		""" TODO: implement this later -- notifies the participant that it has a move to make """

		pass

	def notify(self, text):

		""" TODO: implement this later -- updates the participant that a piece of text has been outputted on the board """

		pass