import sys, math
sys.path.insert(1, "/Users/samuelarnesen/Desktop/projects/bgfw")
from game_engine import GameEngine
from game_pieces import Contract_Card, City_Card, Unit

class ContractGameEngine(GameEngine):

	def __init__(self, participant_names, version="usa", all_auction=False):
		super().__init__()

		# adds pieces
		self.add_piece_type(Contract_Card())
		self.add_piece_type(City_Card())
		self.add_piece_type(Unit())
		self.load_pieces_from_json(version + "/cards.json")
		self.load_pieces_from_json(version + "/units.json")

		# adds participants
		for participant_name in participant_names:
			self.add_participant(participant_name)

		# begins the budget with $200 and sets minimum constraint of $0
		for participant in self.get_participants():
			participant.set_attribute("Budget", 200)

		# generates unit card order
		for i, piece in enumerate(self.shuffle_pieces({"type name": "Unit"})):
			piece.set_attribute("Display", i < (((2 *len(participant_names)) + 1)) and not all_auction)
			piece.set_attribute("Display Order", i)
			piece.set_attribute("Price", 0)
			piece.set_attribute("Discarded", False)

		# generates city card order
		for i, card in enumerate(self.shuffle_pieces({"type name": "City Card"})):
			card.set_attribute("Display Order", i)
			card.set_attribute("Drawn", False)

		# generates contract card order
		for i, card in enumerate(self.shuffle_pieces({"type name": "Contract Card"})):
			card.set_attribute("Display Order", i)
			card.set_attribute("Drawn", False)

	def get_units_on_the_board(self):

		return self.sort_pieces_by_attribute("Display Order", {"type name": "Unit", "owner": None, "Display": True, "Discarded": False})

	def get_unit_on_the_board_by_unit_id(self, unit_id):
		
		for unit in self.get_units_on_the_board():
			if unit.get_attribute("Unit ID") == unit_id:
				return unit
		return None

	def generate_contract(self, display=True):

		def draw_top_card(card_type):
			available = self.sort_pieces_by_attribute("Display Order", {"type name": card_type, "Drawn": False})
			available[0].set_attribute("Drawn", True)
			return available[0]

		city_card = draw_top_card("City Card")
		contract_card = draw_top_card("Contract Card")
		if display:
			print("Contract")
			print(city_card)
			print(contract_card)
		return city_card, contract_card

	def display_units_to_buy(self, display_price=True):
		for i, unit in enumerate(self.get_units_on_the_board()):
			if display_price:
				print("${}".format(unit.get_attribute("Price")))
			print(unit)

	def generate_units_on_the_board(self):
		on_the_board = len(self.get_units_on_the_board())
		if on_the_board > 0:
			cheapest = self.get_units_on_the_board()[0]
			cheapest.set_attribute("Display", False)
			cheapest.set_attribute("Discarded", True)

		on_the_board = max(0, on_the_board - 1)
		while on_the_board < 5:
			candidates = self.sort_pieces_by_attribute("Display Order", {"type name": "Unit", "owner": None, "Display": False, "Discarded": False})
			if len(candidates) == 0:
				break
			else:
				candidates[0].set_attribute("Display", True)
			on_the_board = len(self.get_units_on_the_board())

		prices = [100, 200, 300, 400, 500]
		for i, unit in enumerate(self.get_units_on_the_board()):
			unit.set_attribute("Price", prices[i])

	def draw_top_unit_card(self):
		unit_cards = self.sort_pieces_by_attribute("Display Order", {"owner": None, "type name": "Unit"})
		if len(unit_cards) > 0:
			return unit_cards[0]

	def calculate_production_cost(self, participant_name, units_to_supply, commodity_name, target_city):

		# calculate the distance from target city to every unit
		processed = {}
		on_deck = []
		number_of_units = len(self.get_pieces_by_filter({"type name": "Unit"}))
		
		for unit in self.get_pieces_by_filter({"type name": "Unit"}):
			if target_city in unit.get_attribute("Adjacent Cities"):
				distance = 1 if unit.get_attribute("owner") == None else (0 if unit.get_attribute("owner") == participant_name else 2)
				on_deck.append((unit, distance))

		while len(processed) < number_of_units:
			on_deck = sorted(on_deck, key=lambda x: x[1])
			current_unit, current_distance = on_deck[0]
			processed[current_unit.get_attribute("Unit ID")] = current_distance

			for unit_id in current_unit.get_attribute("Adjacent Units"):
				unit = self.get_individual_piece({"type name": "Unit", "Unit ID": unit_id})
				distance = 1 if unit.get_attribute("owner") == None else (0 if unit.get_attribute("owner") == participant_name else 2)
				on_deck.append((unit, distance + current_distance))

			on_deck = list(filter(lambda x: x[0].get_attribute("Unit ID") not in processed, on_deck))

		# sort units that produce the correct resource by distance
		owned_units = self.get_pieces_by_filter({"type name": "Unit", "owner": participant_name})
		relevant_owned_units = list(filter(lambda x: x.get_attribute(commodity_name) > 0, owned_units))
		relevant_owned_units = sorted(relevant_owned_units, key=lambda x: processed[x.get_attribute("Unit ID")])

		# supply according to cheapest first
		currently_supplied = 0
		current_idx = 0
		current_cost = 0
		while currently_supplied < units_to_supply and current_idx < len(relevant_owned_units):
			current_unit = relevant_owned_units[current_idx]
			unit_supply =  min(current_unit.get_attribute(commodity_name), units_to_supply - currently_supplied)
			currently_supplied += unit_supply

			current_cost += (processed[current_unit.get_attribute("Unit ID")] * unit_supply)
			current_idx += 1

		if currently_supplied < units_to_supply:
			current_cost += (20 * (units_to_supply - currently_supplied))

		return current_cost

	def score(self):

		# gets all the regions and their number of territories
		regions = {}
		for unit in self.get_pieces_by_filter({"type name": "Unit"}):
			region = unit.get_attribute("Region")
			if region not in regions:
				regions[region] = 0
			regions[region] += 1

		for participant in self.get_participants():

			name = participant.get_attribute("name")
			points = 0

			# scores their number of territories
			points += len(self.get_pieces_by_filter({"type name": "Unit", "owner": name}))

			# scores the number of regions they control
			for region in regions:
				number_of_owned_units_in_that_region = self.get_pieces_by_filter({"type name": "Unit", "owner": name, "Region": region})
				if len(number_of_owned_units_in_that_region) == regions[region]:
					points += 2
				if len(number_of_owned_units_in_that_region) > (regions[region] / 2):
					points += 1

			# gets points for their bank account
			budget = participant.get_attribute("Budget")
			if budget > 0:
				points += math.floor(budget / 200)
			else:
				debt = (budget * -1)
				points -= math.ceil(debt / 50)


			print("{} has {} point(s)".format(name, points))
		print()

	def apply_interest_to_debtors(self):

		for participant in self.get_participants():
			budget = participant.get_attribute("Budget")
			if budget < 0:
				budget *= 1.10
				participant.set_attribute("Budget", round(budget))

	def calculate_marginal_supply_curve(self, participant_name, commodity_name, target_city):

		marginal_cost_curve = [0]
		current_cost = 0
		units_to_supply = 1
		while marginal_cost_curve[-1] < 20:
			next_cost = self.calculate_production_cost(participant_name, units_to_supply, commodity_name, target_city)
			marginal_cost_curve.append(next_cost - current_cost)
			current_cost = next_cost
			units_to_supply += 1

		return marginal_cost_curve















