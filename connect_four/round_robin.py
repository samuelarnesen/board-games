import torch
from connect_four_engine import ConnectFourEngine
from connect_four_agent import Agent
import sys

competitors = []
for i in range(220, 230):
	competitors.append({"Agent": Agent(), "Wins": 0, "Losses": 0})
	competitors[-1]["Agent"].load_state_dict(torch.load("old_agents/agent{}.pt".format(i)))

engine = ConnectFourEngine()
count = 0
for i in range(10):
	for j in filter(lambda x: x != i, range(10)):
		participants = [competitors[i], competitors[j]]
		for participant in participants:
			participant["Agent"].reset()
		for match in range(2):
			winner = engine.play_game([x["Agent"] for x in participants], display=False, train=False)
			print(count, winner)
			count += 1
			if winner == "X":
				participants[0]["Wins"] += 1
				participants[1]["Losses"] += 1
			elif winner == "O":
				participants[1]["Wins"] += 1
				participants[0]["Losses"] += 1
			participants = list(reversed(participants))
			engine.reset()


for i, competitor in enumerate(competitors):
	print("{}: {}-{}".format(i, competitor["Wins"], competitor["Losses"]))
