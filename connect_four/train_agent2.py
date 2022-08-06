from connect_four_agent import Agent
from connect_four_engine import ConnectFourEngine
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import pickle, random, sys, os, re, copy


def predict(data_list, turn):
	full_data = random.choices(data_list, k=64)
	boards = [board for board, _, _ in full_data]
	labels = torch.tensor([label for _, _,label in full_data], dtype=torch.float)
	probs = main(boards, turn, training=True).squeeze()
	loss = loser(probs, labels)
	loss.backward()
	optimizer.step()
	optimizer.zero_grad()

	return loss

def update_logs(new_log, current_log, string_boards, winner):

	def add(board, turn, bs1, bs2):
		string_boards.add(bs1)
		string_boards.add(bs2)
		current_log.append((board, turn, 1 if ("X" == winner) else 0))
		current_log.append((copy.deepcopy(np.flip(board, axis=1)), turn, 1 if ("X" == winner) else 0))

	added = False
	random.shuffle(new_log)
	for (board, turn) in new_log:
		bs1, bs2  = create_board_string(board)
		if bs1 not in string_boards and bs2 not in string_boards:
			add(board, turn, bs1, bs2)
			added = True
			break
	if not added and len(new_log) > 0:
		(board, turn) = random.choice(new_log)
		bs1, bs2  = create_board_string(board)
		if bs1 in string_boards:
			string_boards.remove(bs1)
		if bs2 in string_boards:
			string_boards.remove(bs2)
		add(board, turn, bs1, bs2)

def create_board_string(board):
	bs1 = board.tostring()
	bs2 = copy.deepcopy(np.flip(board, axis=1)).tostring()
	return bs1, bs2

def create_random_board():
	num_turns = random.randint(0, 24)
	for turn in range(num_turns):
		success = False
		while not success:
			entry = random.randint(0, 6)
			success, _ = engine.place_piece(entry)
		engine.move_to_next_turn()

	board, turn = engine.get_game_state()
	return board, turn

# loads data
xbig_log = []
if "xboards.p" in os.listdir():
	with open("xboards.p", "rb") as f:
		xbig_log = pickle.load(f)

obig_log = []
if "oboards.p" in os.listdir():
	with open("oboards.p", "rb") as f:
		obig_log = pickle.load(f)

xboard_strings = set()
if "xboard_strings.p" in os.listdir():
	with open("xboard_strings.p", "rb") as f:
		xboard_strings = pickle.load(f)

oboard_strings = set()
if "oboard_strings.p" in os.listdir():
	with open("oboard_strings.p", "rb") as f:
		oboard_strings = pickle.load(f)

while True:

	# loads models
	eligible = []
	for filename in os.listdir():
		if re.match("agentA\d+.pt", filename) != None:
			version_number = int(re.match("agentA(\d+).pt", filename).group(1))
			eligible.append((version_number, filename))
	eligible = sorted(eligible, key=lambda x: int(x[0]), reverse=True)

	if len(eligible) > 50:
		eligible = eligible[0:20]

	main = Agent()
	secondary = Agent()
	if len(eligible) > 0:
		main_name = eligible[0][1]
		main.load_state_dict(torch.load(main_name))

	loser = nn.MSELoss()
	optimizer = optim.AdamW(main.parameters(), lr=0.001)

	for update in range(10):

		# trains on data
		xnormal_losses = []
		onormal_losses = []

		for i in range(100):

			if len(xbig_log) >= 64:
				xnormal_losses.append(predict(xbig_log, "X").item())

			if len(obig_log) >= 64:
				onormal_losses.append(predict(obig_log, "O").item())

		for loss_list in [xnormal_losses, onormal_losses]:
			if len(loss_list) > 0:
				print(sum(loss_list) / len(loss_list), end="\t")

		print("\n")

		# plays game
		if len(eligible) > 0:
			secondary_name = random.choice(eligible)[1]
			secondary.load_state_dict(torch.load(secondary_name))
			print("{} v {}".format(main_name, secondary_name))

		engine = ConnectFourEngine()
		participant_list = [main, secondary]
		main_starter = True
		main_wins = 0
		main_losses = 0
		main_draws = 0
		with torch.no_grad():
			for i in range(200):

				acceptable = False
				while not acceptable:
					engine.reset()
					initial_board, next_turn = create_random_board()
					acceptable = (engine.find_winner() == None)

				engine.set_state(initial_board, next_turn)
				for participant in participant_list:
					participant.set_state(initial_board, next_turn)

				board_log, winner = engine.play_game(participant_list, display=False, train=True, reset=False)
				if winner != ".":

					update_logs(list(filter(lambda x: x[1] == "X", board_log)), xbig_log, xboard_strings, winner)
					update_logs(list(filter(lambda x: x[1] == "O", board_log)), obig_log, oboard_strings, winner)

				engine.reset()
				for participant in participant_list:
					participant.reset()

				participant_list = list(reversed(participant_list))
				if (main_starter and winner == "X") or (not main_starter and winner == "O"):
					main_wins += 1
				elif winner != ".":
					main_losses += 1
				else:
					main_draws += 1
				main_starter = not main_starter

		print("{} - {} - {}".format(main_wins, main_losses, main_draws))

	# saves data
	main_num = eligible[0][0] + 1 if len(eligible) > 0 else 0
	print("saving")
	torch.save(main.state_dict(), "agentA{}.pt".format(main_num))

	with open("xboards.p", "wb") as f:
		pickle.dump(xbig_log, f)
	with open("xboard_strings.p", "wb") as f:
		pickle.dump(xboard_strings, f)
	with open("oboards.p", "wb") as f:
		pickle.dump(obig_log, f)
	with open("oboard_strings.p", "wb") as f:
		pickle.dump(oboard_strings, f)