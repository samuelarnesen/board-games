from connect_four_agent import Agent
from connect_four_engine import ConnectFourEngine
import torch
import torch.nn as nn
import torch.optim as optim
import pickle, random, sys, os, re


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

# loads data
xbig_log = []
if "xboards.p" in os.listdir():
	with open("xboards.p", "rb") as f:
		xbig_log = pickle.load(f)

xends = []
if "xends.p" in os.listdir():
	with open("xends.p", "rb") as f:
		xends = pickle.load(f)

xnears = []
if "xnear_ends.p" in os.listdir():
	with open("xnear_ends.p", "rb") as f:
		xnears = pickle.load(f)

obig_log = []
if "oboards.p" in os.listdir():
	with open("oboards.p", "rb") as f:
		obig_log = pickle.load(f)

oends = []
if "oends.p" in os.listdir():
	with open("oends.p", "rb") as f:
		oends = pickle.load(f)

onears = []
if "onear_ends.p" in os.listdir():
	with open("onear_ends.p", "rb") as f:
		onears = pickle.load(f)


while True:
	if len(xbig_log) > 100000:
		xbig_log = xbig_log[-100000:]
	if len(xends) > 25000:
		xends = xends[-25000:]
	if len(xnears) > 25000:
		xnears = xnears[-25000:]
	if len(obig_log) > 100000:
		obig_log = obig_log[-100000:]
	if len(oends) > 25000:
		oends = oends[-25000:]
	if len(onears) > 25000:
		onears = onears[-25000:]

	# loads models
	eligible = []
	for filename in os.listdir():
		if re.match("agent\d+.pt", filename) != None:
			version_number = int(re.match("agent(\d+).pt", filename).group(1))
			eligible.append((version_number, filename))
	eligible = sorted(eligible, key=lambda x: int(x[0]), reverse=True)

	#if len(eligible) > 20:
	#	eligible = eligible[0:20]

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
		xend_losses = []
		xnear_losses = []
		onormal_losses = []
		oend_losses = []
		onear_losses = []

		for i in range(500):

			if len(xbig_log) > 64:
				xnormal_losses.append(predict(xbig_log, "X").item())

			if len(obig_log) > 64:
				onormal_losses.append(predict(obig_log, "O").item())

			if i % 5 == 0:
				if len(xends) > 64:
					xend_losses.append(predict(xends, "X").item())

				if len(xnears) > 64:
					xnear_losses.append(predict(xnears, "X").item())

				if len(oends) > 64:
					oend_losses.append(predict(oends, "O").item())

				if len(xnears) > 64:
					onear_losses.append(predict(oends, "O").item())


		for loss_list in [xnormal_losses, xend_losses, xnear_losses, onormal_losses, oend_losses, onear_losses]:
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
			for i in range(100):
				board_log, winner = engine.play_game(participant_list, display=False, train=True)
				if winner != ".":

					for (board, turn) in board_log:
						if turn == "X":
							xbig_log.append((board, turn, 1 if ("X" == winner) else 0))
						else:
							obig_log.append((board, turn, 1 if ("X" == winner) else 0))

					if winner == "X":
						assert(board_log[-1][1] == "X")
						assert(board_log[-2][1] == "O")
						xends.append((board_log[-1][0], board_log[-1][1], 1 if ("X" == winner) else 0))
						onears.append((board_log[-2][0], board_log[-2][1], 1 if ("X" == winner) else 0))
					else:
						assert(board_log[-1][1] == "O")
						assert(board_log[-2][1] == "X")
						oends.append((board_log[-1][0], board_log[-1][1], 1 if ("X" == winner) else 0))
						xnears.append((board_log[-2][0], board_log[-2][1], 1 if ("X" == winner) else 0))

				engine.reset()
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
	torch.save(main.state_dict(), "agent{}.pt".format(main_num))
	with open("xboards.p", "wb") as f:
		pickle.dump(xbig_log, f)
	with open("xends.p", "wb") as f:
		pickle.dump(xends, f)
	with open("xnear_ends.p", "wb") as f:
		pickle.dump(xnears, f)
	with open("oboards.p", "wb") as f:
		pickle.dump(obig_log, f)
	with open("oends.p", "wb") as f:
		pickle.dump(oends, f)
	with open("onear_ends.p", "wb") as f:
		pickle.dump(onears, f)