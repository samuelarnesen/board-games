import sys
import torch
from connect_four_engine import ConnectFourEngine
from connect_four_agent import Agent


engine = ConnectFourEngine()

if len(sys.argv) > 1:
	version_num = sys.argv[1]
	opponent = Agent()
	opponent.load_state_dict(torch.load("agentA{}.pt".format(version_num)))


if len(sys.argv) > 2:
	if sys.argv[2] == "X":
		engine.play_game(participants=[None, opponent], train=False)	
	else:
		engine.play_game(participants=[opponent, None], train=False)
else:
	engine.play_game(participants=[opponent, None], train=False)

