from agent import Agent
from roles import Role, Side

import numpy as np
import random, math

class GameEngine:

	def __init__(self):

		roles = [Role.MERLIN, Role.PERCIVAL, Role.KNIGHT, Role.KNIGHT, Role.MORGANA, Role.ASSASSIN, Role.MINION]
		random.shuffle(roles)
		self.__players = [Agent(roles[i], i) for i in range(len(roles))]
		self.__specials = {}
		for player in filter(lambda x: Role.is_special(x.get_role()), self.__players):
			self.__specials[player.get_role()] = player.get_id_num()

		self.__mission_number = 0
		self.__missions_passed = 0
		self.__missions_failed = 0
		self.__number_of_people_on_mission = [2, 3, 3, 4, 4]
		self.__number_of_people_needed_to_fail = [1, 1, 1, 2, 1]
		self.__number_of_people_needed_for_mission_to_go_forward = math.ceil(len(self.__players) / 2)

		self.__chair_index = 0
		self.__number_of_passes = 0
		self.__maximum_number_of_passes = 4

		self.__game_to_date = np.zeros(23)

	def play_game(self):

		self.__notify_specials()

		while self.__game_is_still_ongoing():
			players_on_mission = self.__set_mission()
			mission_succeeds = self.__play_out_mission(players_on_mission)
			#print(f"mission {self.__mission_number + 1} succeeds: {mission_succeeds}")
			if self.__game_is_still_ongoing():
				self.__move_to_next_turn()

		if self.__missions_failed >= 3:
			return False

		merlin_killed = self.__play_post_game()
		return not merlin_killed

	def __notify_specials(self):

		bad_guy_idxs = []
		for player in self.__players:
			if player.get_side() == Side.BAD:
				bad_guy_idxs.append(player.get_id_num())

		for bad_guy_idx in bad_guy_idxs:
			self.__players[bad_guy_idx].reveal_bad_guys(bad_guy_idxs)
		self.__get_special_player_by_role(Role.MERLIN).reveal_bad_guys(bad_guy_idxs)
		
		merlin_or_morgana_idxs = [self.__specials[Role.MERLIN], self.__specials[Role.MORGANA]]
		random.shuffle(merlin_or_morgana_idxs)
		self.__get_special_player_by_role(Role.PERCIVAL).reveal_merlin_or_morgana(merlin_or_morgana_idxs)

	def __set_mission(self):

		number_of_votes_for = 0
		self.__number_of_passes = 0
		while number_of_votes_for < self.__number_of_people_needed_for_mission_to_go_forward and self.__number_of_passes < self.__maximum_number_of_passes:
			nominated_players_idxs = self.__players[self.__chair_index].select_mission_to_go_forward(self.get_number_of_people_on_current_mission(), self.__game_to_date)
			for player in self.__players:
				aye_vote = player.vote_on_mission_going_forward(nominated_players_idxs, self.__game_to_date)
				number_of_votes_for += (1 if aye_vote else 0)
			if number_of_votes_for < self.__number_of_people_needed_for_mission_to_go_forward:
				self.__number_of_passes += 1
				self.__chair_index += 1 
				self.__chair_index %= 7
				number_of_votes_for = 0
		if self.__number_of_passes == self.__maximum_number_of_passes:
			nominated_players_idxs = self.__players[self.__chair_index].select_mission_to_go_forward(self.get_number_of_people_on_current_mission(), self.__game_to_date)

		self.__number_of_passes = 0
		return nominated_players_idxs

	def __play_out_mission(self, nominated_players_idxs):

		successes_count = 0
		for player_idx in nominated_players_idxs:
			success = self.__players[player_idx].vote_on_mission_success(nominated_players_idxs, self.__game_to_date)
			successes_count += (1 if success else 0)

		mission_succeeds = self.__mission_succeeds(successes_count)
		if mission_succeeds:
			self.__missions_passed += 1
		else:
			self.__missions_failed += 1
		return mission_succeeds

	def __play_post_game(self):
		person_to_kill = self.__get_special_player_by_role(Role.ASSASSIN).identify_merlin()
		return person_to_kill == self.__get_special_player_by_role(Role.MERLIN).get_id_num()

	def __move_to_next_turn(self):
		self.__mission_number += 1
		self.__chair_index += 1
		self.__chair_index %= 7

	def __game_is_still_ongoing(self):
		return (self.__missions_passed < 3) and (self.__missions_failed < 3)

	def __mission_succeeds(self, successes_count):

		return successes_count > self.get_number_of_people_on_current_mission() - self.get_number_of_people_needed_to_failed_current_mission()

	def __get_special_player_by_role(self, role):

		idx = self.__specials[role]
		return self.__players[idx]

	def get_number_of_people_on_current_mission(self):

		return self.__number_of_people_on_mission[self.__mission_number]

	def get_number_of_people_needed_to_failed_current_mission(self):

		return self.__number_of_people_needed_to_fail[self.__mission_number]





