from contract_game_engine import ContractGameEngine
from game_pieces import Contract_Card, City_Card, Unit
import simpleaudio as sa
import random, re, time, sys, argparse

@ContractGameEngine.no_fail(execution_mode=False)
def is_a_buyable_unit(unit_id, *args, **kwargs):
	for unit in engine.get_units_on_the_board():
		if unit.get_attribute("Unit ID") == int(unit_id):
			return True
	return False
 
@ContractGameEngine.no_fail(execution_mode=True)
def purchase_unit(unit_id, purchaser, *args, **kwargs):
	unit = engine.get_unit_on_the_board_by_unit_id(int(unit_id))
	unit.set_attribute("owner", purchaser.get_attribute("name"))
	unit.set_attribute("Display", False)
	purchaser.set_attribute("Budget", purchaser.get_attribute("Budget") - unit.get_attribute("Price"))
	print("\nDone! {} now owns unit {}\n".format(unit.get_attribute("owner"), unit.get_attribute("Unit ID")))
	return unit, True

@ContractGameEngine.no_fail(execution_mode=False)
def is_a_budget_command(command, *args, **kwargs):
	split_command = command.split(": ")
	relevant_participant = engine.get_participant_by_name(split_command[0])
	if relevant_participant != None:
		return split_command[1] in ["b", "budget", "display budget"]
	return False

@ContractGameEngine.no_fail(execution_mode=True)
def print_budget(command, inputer, *args, **kwargs):
	split_command = command.split(": ")
	asking_participant = engine.get_participant_by_name(split_command[0])
	print("{}'s budget is ${}\n".format(asking_participant, asking_participant.get_attribute("Budget")))
	return None, True

@ContractGameEngine.no_fail(execution_mode=False)
def is_an_auction_response(command, *args, **kwargs):
	marked = {}
	for participant in engine.get_participants():
		marked[participant.get_attribute("name")] = False

	for part in command.split(", "):
		split_part = part.split(": ")
		name = split_part[0]
		bet = split_part[1]
		if name not in marked:
			return False
		if marked[name] == True:
			return False
		if re.match("\d+", bet) == None:
			return False
		marked[name] = True

	for name in marked:
		if not marked[name]:
			return False

	return True

@ContractGameEngine.no_fail(execution_mode=True)
def process_auction(command, inputer, *args, **kwargs):
	bets = {}
	for part in command.split(", "):
		split_part = part.split(": ")
		bets[split_part[0]] = int(split_part[1])

	if current_contract_card.get_attribute("Auction Type") == "Cournot":
		quantity_supplied = sum([bets[bettor] for bettor in bets])
		price = current_contract_card.get_attribute("Base Price") - (current_contract_card.get_attribute("Multiplier") * quantity_supplied)
		print("{} units are being supplied at a base price of ${}".format(quantity_supplied, price))
		for participant in engine.get_participants():
			name = participant.get_attribute("name")
			production_cost = engine.calculate_production_cost(name, bets[name], current_contract_card.get_attribute("Commodity"), current_city_card.get_attribute("City"))
			profit = (bets[name] * price) - production_cost
			participant.set_attribute("Budget", participant.get_attribute("Budget") + profit)
			print("{} is providing {} units at a total cost of ${}, with a net profit of {}".format(name, bets[name], production_cost, profit))
			if profit > 100:
				play_obj = sa.WaveObject.from_wave_file("cash.wav").play()
				play_obj.wait_done()
	else:
		lowest_bid = min([bets[bettor] for bettor in bets])
		lowest_bidders = [bidder for bidder in filter(lambda x: bets[x] == lowest_bid, bets)]
		print("The units are being supplied by {} at a price of ${}".format(" and ".join(lowest_bidders), lowest_bid))
		for bidder in lowest_bidders:
			participant = engine.get_participant_by_name(bidder)
			quantity = int(current_contract_card.get_attribute("Quantity") / len(lowest_bidders))
			production_cost = engine.calculate_production_cost(bidder, quantity, current_contract_card.get_attribute("Commodity"),\
				current_city_card.get_attribute("City"))
			profit = (bets[bidder] * quantity) - production_cost
			participant.set_attribute("Budget", participant.get_attribute("Budget") + profit)
			print("{} is providing {} units at a total cost of ${}, with a net profit of ${}".format(bidder, quantity, production_cost, profit))
			if profit > 100:
				play_obj = sa.WaveObject.from_wave_file("cash.wav").play()
				play_obj.wait_done()

	print()
	return None, True

@ContractGameEngine.no_fail(execution_mode=True)
def process_unit_sale(command, inputer, *args, **kwargs):
	bids = {}
	for part in command.split(", "):
		split_part = part.split(": ")
		bids[split_part[0]] = int(split_part[1])

	second_price = sorted([bids[bidder] for bidder in bids], reverse=True)[1]
	top_bidder = sorted([bidder for bidder in bids], key=lambda x: bids[x] + (random.random() / 100), reverse=True)[0]
	unit_for_sale.set_attribute("owner", top_bidder)

	purchaser = engine.get_participant_by_name(top_bidder)
	purchaser.set_attribute("Budget", purchaser.get_attribute("Budget") - second_price)
	print("\n{} now owns unit {} after paying ${}\n".format(unit_for_sale.get_attribute("owner"), unit_for_sale.get_attribute("Unit ID"), second_price))
	return unit_for_sale, True

@ContractGameEngine.no_fail(execution_mode=False)
def is_a_summary_command(command, *args, **kwargs):
	split_command = command.split(": ")
	relevant_participant = engine.get_participant_by_name(split_command[0])
	if relevant_participant != None:
		return split_command[1] in ["s", "summary", "display summary"]
	return False

@ContractGameEngine.no_fail(execution_mode=True)
def display_summary(command, inputer, *args, **kwargs):
	split_command = command.split(": ")
	asking_participant = engine.get_participant_by_name(split_command[0])
	relevant_units = engine.get_pieces_by_filter({"type name": "Unit", "owner": split_command[0]})
	for commodity in ["Agriculture", "Animals", "Energy", "Metals"]:
		amount = sum([unit.get_attribute(commodity) for unit in relevant_units])
		print("{}: {}".format(commodity, amount))
	print()
	return None, True

def display_all_budgets():
	for participant in engine.get_participants():
		budget_command = "{}: {}".format(participant.get_attribute("name"), "b")
		print_budget(budget_command, None)
	print()

def display_all_summaries():
	for participant in engine.get_participants():
		summary_command = "{}: {}".format(participant.get_attribute("name"), "s")
		print("{}:".format(participant.get_attribute("name")))
		display_summary(summary_command, None)
	print()

	
# initializes the game engine
parser = argparse.ArgumentParser()
parser.add_argument("--version", default="usa", type=str)
parser.add_argument("--all_auction", default=False, action="store_true")
args = parser.parse_args()

engine = ContractGameEngine(["Sam", "Will", "Daniel"], args.version, args.all_auction)

# adds input responses
engine.add_input_response("unit_selection", is_a_buyable_unit, purchase_unit)
engine.add_input_response("budget", is_a_budget_command, print_budget)
engine.add_input_response("summary", is_a_summary_command, display_summary)
engine.add_input_response("auction", is_an_auction_response, process_auction)
engine.add_input_response("unit sale", is_an_auction_response, process_unit_sale)

# generate starting order
participant_order = [participant for participant in engine.shuffle_participants()]
reverse_participant_order = [participant_order[(-1 * i) - 1] for i in range(len(participant_order))]
overall_order = participant_order + reverse_participant_order

# initial card selection
if not args.all_auction:
	for participant in overall_order:
		engine.display_units_to_buy(display_price=False)
		print("{}'s selection:".format(participant))
		engine.listen(["unit_selection"], end_label="pass", max_commands=1, inputer=participant)

order = reverse_participant_order
turn = 0
while len(engine.get_pieces_by_filter({"type name": "City Card", "Drawn": False})) > 1:

	# generates the board
	if args.all_auction:
		display_all_summaries()
		display_all_budgets()
		unit_for_sale = engine.draw_top_unit_card()
		print("Unit for Sale")
		print(unit_for_sale, "\n")
		engine.listen(["unit sale"], end_label="pass", max_commands=1, inputer=None)
		time.sleep(3)
	else:
		# displays units for purchase
		engine.generate_units_on_the_board()
		if len(engine.get_units_on_the_board()) == 0:
			break
		engine.display_units_to_buy(display_price=True)

		# accepts input
		relevant_participant = order[turn % len(order)]
		print("{}'s turn: ".format(relevant_participant))
		engine.listen(["unit_selection", "budget", "summary"], end_label="pass", inputer=relevant_participant)

	# prints what people have
	display_all_summaries()

	# generates contract card
	current_city_card, current_contract_card = engine.generate_contract(display=True)

	engine.listen(["auction"], end_label="pass", max_commands=1, inputer=None)
	time.sleep(3)

	# updates turn info
	turn += 1
	units_left = len(engine.get_pieces_by_filter({"type name": "Unit", "Discarded": False, "owner": None})) - 1
	if units_left > 0:
		print("Turn #{}, {} buyable units left".format(turn + 1, units_left))
		engine.score()

	# apply interest
	engine.apply_interest_to_debtors()

# score
print("The game is over...")
time.sleep(2)
print("The final scores are...")
time.sleep(2)
engine.score()






