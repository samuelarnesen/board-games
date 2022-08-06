import random

def add_next_to_curve(previous):

	if random.random() > 0.5:
		return min(20, previous + random.randint(0, 5))
	return previous

def find_differential(curve, their_curve, bet, their_bet, contract):
	base_price = contract[0] - (contract[1] * (bet + their_bet))

	their_cost = sum(their_curve[0:their_bet + 1])
	their_profit = (base_price * their_bet) - their_cost

	my_cost = sum(curve[0:bet+1])
	my_profit = (base_price * bet) - my_cost

	return my_profit - their_profit

def find_best_response(curve, their_curve, their_bet, contract):
	best_bet = -1
	best_differential = float("-inf")
	for bet in range(len(curve)):
		differential = find_differential(curve, their_curve, bet, their_bet, contract)
		best_differential = max(best_differential, differential)
		best_bet = bet if best_differential == differential else best_bet
	return best_bet

total = []
for trial in range(15):
	my_curve = [0]
	their_curve = [0]

	for i in range(40):
		my_curve.append(add_next_to_curve(my_curve[-1]))
		their_curve.append(add_next_to_curve(their_curve[-1]))

	contract = random.choice([(40, 1), (50, 1), (60, 2), (80, 2), (100, 3), (120, 3)])

	their_bets = []
	my_bets = []
	for i in range(5):
		my_bet = random.randint(0, 40)
		for j in range(5):
			their_bet = find_best_response(their_curve, my_curve, my_bet, contract)
			my_bet = find_best_response(my_curve, their_curve, their_bet, contract)
		their_bets.append(their_bet)
		my_bets.append(my_bet)

	print("{} - {}q".format(contract[0], contract[1]))
	print("Your curve")
	for i in range(1, 40):
		print("{}: {}".format(i, their_curve[i]), end="\t")
		if their_curve[i] >= 20:
			break
	print()
	print("Their curve")
	for i in range(1, 40):
		print("{}: {}".format(i, my_curve[i]), end="\t")
		if my_curve[i] >= 20:
			break
	print()

	outside_bet = int(input())
	computer_bet = round(sum(my_bets) / len(my_bets))
	differential = find_differential(their_curve, my_curve, outside_bet, computer_bet, contract)

	print("Computer's bet is {}".format(computer_bet))
	print("Differential is {}".format(differential))
	total.append(differential)

print()
print("Average differential was {}".format(sum(total) / len(total)))


