import random, multiprocessing, queue, time
from concurrent.futures import as_completed, ThreadPoolExecutor
from tqdm import tqdm

NUM_GAMES = 1000
TIMEOUT = 3

TICK = 0.0001
PICKUP_TIME = 2
EVALUATE_TIME = 1
DISCARD_TIME = 1
SWAP_TIME = 1
DECK_PICKUP_TIME = 2

NUM_PLAYERS = 8
HAND_LENGTH = 4
NUM_CARDS_PER_SUIT = 13
DECK_LENGTH = 52

def is_done(hand):
	for card in hand:
		if card[0] != hand[0][0]:
			return False
	return True

def decide_on_card(card, player_counts, hand):
	if player_counts[card[0]] == 0:
		return False, card

	new_player_count = player_counts[card[0]] + 1

	for i, existing_card in enumerate(hand):
		if player_counts[existing_card[0]] < new_player_count and existing_card[0] != card[0]:
			player_counts[existing_card[0]] -= 1
			player_counts[card[0]] += 1
			hand[i] = card
			return True, existing_card
	return False, card

def get_time_length(val):
	return max(round(random.gauss(val, val / 4), 1), 0.1) * TICK

def play(player_num, hand, player_counts, input_queue, output_queue, victory_queue):
	won = False
	#print("Player {} is starting".format(player_num))
	while victory_queue.empty():
		#print("Player {} is waiting for a card".format(player_num))
		card = input_queue.get(block=True, timeout=TIMEOUT)
		time.sleep(get_time_length(PICKUP_TIME if player_num > 0 else DECK_PICKUP_TIME))
		time.sleep(get_time_length(EVALUATE_TIME))
		swapped, card_to_pass_on = decide_on_card(card, player_counts, hand)
		#print("Player {} is calculating if done".format(player_num))
		if is_done(hand):
			try:
				victory_queue.put(player_num, block=False)
				#print("{} won!".format(player_num))
				won = True
			except:
				pass
				#print("{} lost a race".format(player_num))
		time.sleep(get_time_length(DISCARD_TIME + SWAP_TIME if swapped else DISCARD_TIME))
		#print("Player {} is discarding a card".format(player_num))
		output_queue.put(card_to_pass_on)
	return won


results = {}
for player in range(NUM_PLAYERS):
	results[player] = 0

timeouts = {}
for player in range(NUM_PLAYERS):
	timeouts[player] = 0

for game in tqdm(range(NUM_GAMES)):

	suits = ["S", "C", "H", "D"]
	deck = []
	for suit in suits:
		for num in range(0, NUM_CARDS_PER_SUIT):
			deck.append((num, suit))

	random.shuffle(deck)

	deck_idx = 0
	player_hands = {}
	for player in range(NUM_PLAYERS):
		player_hands[player] = [deck[idx] for idx in range(deck_idx, deck_idx + HAND_LENGTH)]
		deck_idx += HAND_LENGTH

	player_counts = {}
	for player in range(NUM_PLAYERS):
		player_counts[player] = {}
		for num in range(0, NUM_CARDS_PER_SUIT):
			player_counts[player][num] = 0

	for player in range(NUM_PLAYERS):
		for card in player_hands[player]:
			player_counts[player][card[0]] += 1

	next_action_time = {}
	for player in range(NUM_PLAYERS):
		next_action_time[player] = 0

	previous_queue = queue.LifoQueue()
	player_queues = {}
	for player in range(NUM_PLAYERS):
		new_queue = queue.LifoQueue()
		player_queues[player] = (previous_queue, new_queue)
		previous_queue = new_queue

	victory_queue = queue.Queue(1)

	for card in deck[deck_idx:]:
		player_queues[0][0].put(card)


	with ThreadPoolExecutor(max_workers=NUM_PLAYERS) as executor:
		winner_count = 0
		futures = []
		for i in range(NUM_PLAYERS):
			future = executor.submit(play, i, player_hands[i], player_counts[i], player_queues[i][0], player_queues[i][1], victory_queue)
			futures.append(future)
		for i, future in enumerate(futures):
			try:
				if future.result(timeout=TIMEOUT):
					results[i] += 1
			except:
				timeouts[player] += 1
				#print("Player {} timed out in game {}".format(i, game))



print("Final results:")
for player in range(NUM_PLAYERS):
	print("Player {}: {} wins".format(player, results[player]))

print()
print("Timeouts:")
for player in range(NUM_PLAYERS):
	print("Player {}: {} timeouts".format(player, timeouts[player]))

