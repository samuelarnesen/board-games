import sys, math, copy, random
import numpy as np

class ConnectFourEngine():

	def __init__(self):
		self.board = np.zeros([6, 7])
		self.turn = 1
		self.previous_moves = []
		self.first_empty = [0 for i in range(7)]
		self.combo_map, self.combo_sums = self.__create_winning_map()

	def reset(self):
		self.board = np.zeros([6, 7])
		self.turn = 1
		self.previous_moves = []
		self.first_empty = [0 for i in range(7)]
		self.combo_sums = np.zeros(len(self.combo_sums))

	def get_game_state(self):
		return self.board, self.turn

	def get_board(self):
		return self.board

	def move_to_next_turn(self):
		self.turn *= -1

	def undo(self):
		if len(self.previous_moves) > 0:
			row, column = self.previous_moves[-1]
			removed_num = self.board[row][column]
			self.board[row, column] = 0
			self.first_empty[column] -= 1
			assert(self.first_empty[column] == row)
			self.previous_moves.pop()
			for combo_id in self.combo_map[row][column]:
				self.combo_sums[combo_id] -= removed_num

	def place_piece(self, column):
		try:
			column_num = int(column)
			if self.first_empty[column_num] >= 6:
				return False, None
			row = self.first_empty[column_num]
			self.board[row, column_num] = self.turn
			self.first_empty[column_num] += 1
			self.previous_moves.append((row, column_num))
			winner = None
			for combo_id in self.combo_map[row][column_num]:
				self.combo_sums[combo_id] += self.turn
				if abs(self.combo_sums[combo_id]) >= 4:
					winner = "X" if self.combo_sums[combo_id] == 4 else "O"

			if winner == None:
				return True, None if len(self.previous_moves) < 42 else "."
			else:
				return True, winner
		except:
			print("uh oh, column {} did not work".format(column_num))
			return False, None

	def __create_winning_map(self):

		winning_combos = []

		# gets the verticals and horizontals
		for i in range(7):
			for j in range(4):
				current_one = []
				current_two = []
				for k in range(4):
					if i < 6:
						current_one.append((i, j + k))
					if j + k < 6:
						current_two.append((j + k, i))
				if len(current_one) == 4:
					winning_combos.append(current_one)
				if len(current_two) == 4:
					winning_combos.append(current_two)

		# gets the diagonals
		for i in range(3):
			for j in range(4):
				current_one = []
				current_two = []
				for k in range(4):
					current_one.append((i + k, j + k))
					current_two.append((i + k, 6 - j - k))
				winning_combos.append(current_one)
				winning_combos.append(current_two)

		# reverses
		reverse_grid = [[[] for i in range(7)] for j in range(6)]
		for i, combo in enumerate(winning_combos):
			for row, column in combo:
				reverse_grid[row][column].append(i)

		sums = np.zeros(len(winning_combos))

		return reverse_grid, sums


	def find_winner(self):

		max_score = np.max(self.combo_sums)
		min_score = np.min(self.combo_sums)
		if max_score == 4:
			return "X"
		elif min_score == -4:
			return "O"
		elif np.sum(np.abs(self.board)) == 42:
			return "."
		return None

	def display_board(self):
		for i in range(6):
			print(5-i, end="\t")
			for j in range(7):
				if self.board[5-i, j] == 1:
					print("X", end="\t")
				elif self.board[5-i, j] == -1:
					print("O", end="\t")
				else:
					print(".", end="\t")
			print(5-i)
		print("\n", end="\t")
		for i in range(7):
			print(i, end="\t")
		print()

	def get_turn(self):
		return "X" if self.turn == 1 else "O"

	def play_game(self, participants=None, display=True, train=False, reset=True):
		if participants == None:
			participants = []
		while len(participants) < 2:
			participants.append(None)

		if reset:
			for participant in filter(lambda x: x != None, participants):
				participant.reset()

		participants = list(reversed(participants))

		if train:
			board_log = []

		winner = None
		while winner == None:
			if display:
				self.display_board()
				print("{}'s turn".format(self.get_turn()))

			successful_entry = False
			failed_before = False
			while not successful_entry:
				participant = participants[int(self.turn + 1 / 2)]
				entry = input() if participant == None else participant.poll(self.get_game_state(), training=train, failed_before=failed_before)
				successful_entry, winner = self.place_piece(entry)
				if successful_entry:
					for player in participants:
						if player != None:
							player.update(entry)
				else:
					failed_before = True

			if train:
				board_log.append((copy.deepcopy(self.board), "X" if self.turn == 1 else "O"))

			self.move_to_next_turn()

		#winner = self.find_winner()
		if display and winner != None:
			self.display_board()
			print("{} wins!".format(winner))

		if train:
			return board_log, winner

		return winner

	def set_board(self, board):
		self.reset()
		for i in range(6):
			for j in range(7):
				if abs(board[i, j]) > 0.5:
					if (board[i, j] == 1 and self.get_turn() == "O") or (board[i, j] == -1 and self.get_turn() == "X"):
						self.move_to_next_turn()
					self.place_piece(j)

		self.board = board

	def set_state(self, board, turn):
		self.reset()
		self.set_board(copy.deepcopy(board))
		if self.get_turn_number() != turn:
			self.move_to_next_turn()

		occupied_board = np.abs(self.get_board())
		first_empty = list(np.sum(occupied_board, axis=0))
		for i, empty_idx in enumerate(first_empty):
			self.first_empty[i] = int(empty_idx)

	def get_length_of_game(self):
		return len(self.previous_moves)

	def get_turn_number(self):
		return self.turn


