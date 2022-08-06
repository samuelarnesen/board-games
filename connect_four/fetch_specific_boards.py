from connect_four_agent import Agent
from connect_four_engine import ConnectFourEngine
import pickle, random, sys, os, re


big_log = []
with open("boards.p", "rb") as f:
	big_log = pickle.load(f)

engine = ConnectFourEngine()

relevant = []
for i, (board, turn, label) in enumerate(big_log):
	engine.set_board(board)
	if engine.find_winner() != None and i > 0:
		relevant.append(big_log[i])

print(len(relevant))
print(relevant[-1])
with open("ends.p", "wb") as f:
	pickle.dump(relevant, f)
