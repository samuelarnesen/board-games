import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
from connect_four_engine import ConnectFourEngine

import sys, random, copy

class Agent(nn.Module):

	def __init__(self):

		super().__init__()

		self.internal_engine = ConnectFourEngine()

		self.first = nn.Conv2d(1, 32, 4)
		self.second = nn.Conv2d(32, 64, 3)
		self.third = nn.Conv2d(64, 128, (1, 2))

		self.scorer_one = nn.Linear(128, 16)
		self.scorer_twoX = nn.Linear(16, 1)
		self.scorer_twoO = nn.Linear(16, 1)

	def forward(self, board, turn, training=False):
		if training:
			board = torch.tensor(board, dtype=torch.float).unsqueeze(1)
		else:
			board = torch.tensor(board, dtype=torch.float).unsqueeze(0).unsqueeze(0)

		temp_one = F.relu(self.first(board))
		temp_two = F.relu(self.second(temp_one))
		temp_three = F.relu(self.third(temp_two))
		penultimate = F.relu(self.scorer_one(temp_three.squeeze()))
		score = self.scorer_twoX(penultimate) if turn == "X" else self.scorer_twoO(penultimate)

		probability = torch.sigmoid(score)
		return probability

	def poll(self, game_state, training=True, failed_before=False):

		real_board, real_turn = game_state
		own_board, own_turn = self.internal_engine.get_game_state()
		turn_letter = "X" if real_turn == 1 else "O"

		if real_turn != own_turn:
			print("ERROR: turns out of match, {} - {}".format(real_turn, own_turn))
			print(real_board)
			print(own_board)
			sys.exit()

		if not np.allclose(real_board, own_board):
			print("\nERROR\n")
			print("\nINTERNAL BOARD\n")
			self.internal_engine.display_board()
			print(real_board)
			print(self.internal_engine.board)
			sys.exit()

		if int(np.sum(real_board)) == 1:
			if turn_letter != "O":
				print("real turn is {}, sum is {}, turn letter is {}".format(real_turn, np.sum(real_board), turn_letter))
				self.internal_engine.display_board()
				sys.exit()
		else:
			if turn_letter != "X":
				print("real turn is {}, sum is {}, turn letter is {}".format(real_turn, np.sum(real_board), turn_letter))
				self.internal_engine.display_board()
				sys.exit()

		if failed_before:
			success = False
			while not success:
				move = random.randrange(7)
				success, _ = self.internal_engine.place_piece(move)
			return move

		probs, investigated = self.lookahead(max_depth=1 if training else 4, beam_size=7 if training else 7)
		probs = [(probs[i] if i in investigated else 0) for i in range(7)]

		if sum(probs) <= 0:
			if not training:
				print("acting randomly")
			return random.randrange(7)

		options = sorted(list(range(7)), key=lambda x: probs[x], reverse=True)
		selection = options[0]
		if not training:
			print(max([(prob.item() if type(prob) == torch.tensor else prob) for prob in probs]))

		if training and self.internal_engine.get_length_of_game() < 15:
			selection_weights = [(prob - min(probs))**2 for prob in probs]
			selection = torch.multinomial(torch.tensor(selection_weights, dtype=torch.float), 1).item()



		success, _ = self.internal_engine.place_piece(selection)
		count = 0
		if not success:
			print("FAILED", selection)
		while not success:
			selection = random.randrange(7)
			success, _  = self.internal_engine.place_piece(selection)
			count += 1
			if count > 10 and not success:
				print("UH OH")
				smallest_empty = min(self.internal_engine.first_empty)
				for i in range(self.internal_engine.first_empty):
					if self.internal_engine.first_empty == smallest_empty:
						print(i)
						return i
		self.internal_engine.undo()
		print(selection)

				
		return selection

	def lookahead(self, max_depth=4, beam_size=2):
		original_turn_letter = self.internal_engine.get_turn()

		probs = self.find_short_term_success_probs(original_turn_letter)

		if max(probs) == 1 or max(probs) == 0 or max_depth == 1:
			return probs, list(range(7))

		options = sorted(list(range(7)), key=lambda x: probs[x], reverse=True)

		for i in range(beam_size):

			if self.internal_engine.get_turn() != original_turn_letter:
				self.internal_engine.move_to_next_turn()

			success, winner = self.internal_engine.place_piece(options[i])

			if winner == None:
				probs[options[i]] = self.lookahead_helper(original_turn_letter, depth=1, max_depth=max_depth, beam_size=beam_size)
			else:
				probs[options[i]] = 1 if winner == original_turn_letter else 0
			if success:
				self.internal_engine.undo()

		if self.internal_engine.get_turn() != original_turn_letter:
			self.internal_engine.move_to_next_turn()

		return probs, [options[i] for i in range(beam_size)]


	def lookahead_helper(self, original_turn, depth, max_depth=5, beam_size=2):

		turn_letter = original_turn if depth % 2 == 0 else ("X" if original_turn == "O" else "O")
		if self.internal_engine.get_turn() != turn_letter:
			self.internal_engine.move_to_next_turn()

		if depth == max_depth:
			previous_turn = "X" if turn_letter == "O" else "O"
			original_score = self(self.internal_engine.get_board(), previous_turn).item()
			score = original_score if previous_turn == original_turn else 1 - original_score # is this right?
			return score

		# score options at this depth level
		probs = self.find_short_term_success_probs(turn_letter)
		options = sorted(list(range(7)), key=lambda x: probs[x], reverse=True)

		# go to next depth level
		values = []
		for i in range(beam_size):

			if self.internal_engine.get_turn() != turn_letter:
				self.internal_engine.move_to_next_turn()

			success, winner = self.internal_engine.place_piece(options[i])


			if winner == None:
				if depth >= max_depth - 1:
					value = probs[options[i]] if turn_letter == original_turn else 1 - probs[options[i]] # is the = sign right
				else:
					value = self.lookahead_helper(original_turn, depth + 1, max_depth, beam_size)
				values.append(value)
			else:
				values.append(1 if turn_letter == original_turn else 0)

			if success:
				self.internal_engine.undo()

		if len(values) > 0:
			return max(values) if turn_letter == original_turn else min(values)
		return 0

	def find_short_term_success_probs(self, turn_letter):

		if self.internal_engine.get_turn() != turn_letter:
			self.internal_engine.move_to_next_turn()

		probs = []
		for i in range(0, 7):
			prob = 0
			success, winner = self.internal_engine.place_piece(i)
			if success:
				if winner != None:
					prob = 1
				else:
					board, _ = self.internal_engine.get_game_state()
					prob = self(board, turn_letter)
					prob = prob if turn_letter == "X" else 1 - prob
				self.internal_engine.undo()
			probs.append(prob.item() if type(prob) != int else prob)
		return probs


	def update(self, move):
		self.internal_engine.place_piece(move)
		self.internal_engine.move_to_next_turn()

	def reset(self):
		self.internal_engine.reset()

	def set_state(self, board, turn):
		self.internal_engine.set_state(board, turn)
			


