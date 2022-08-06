import sys
sys.path.insert(1, "/Users/samuelarnesen/Desktop/projects/board_games/connect_four")
from connect_four_agent import Agent
from connect_four_engine import ConnectFourEngine

from django.apps import AppConfig
import torch


class AiConfig(AppConfig):
    name = 'ai'
    aiplayer = Agent()
    aiplayer.load_state_dict(torch.load("/Users/samuelarnesen/Desktop/projects/board_games/connect_four/agentA538.pt"))
    engine = ConnectFourEngine()
