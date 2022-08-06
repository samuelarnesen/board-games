import random, sys, argparse, time
from tqdm import tqdm
colors = ["R", "O", "Y", "W", "B", "P"]

class Guess:
	def __init__(self, guess, red, white):
		self.guess = guess
		self.red_result = red
		self.white_result = white

def generate_all_possible():
	candidates = []
	for first in colors:
		for second in colors:
			for third in colors:
				for fourth in colors:
					candidates.append(first + second + third + fourth)
	return candidates

def respond_to_guess(correct, guess_string):
	red_result = 0
	white_result = 0

	marked = [False, False, False, False]

	for i in range(len(correct)):
		if correct[i] == guess_string[i]:
			red_result += 1
			marked[i] = True

	for i in range(len(correct)):
		for j in range(len(guess_string)):
			if correct[i] == guess_string[j]:
				if not marked[i]:
					white_result += 1
					marked[i] = True

	return red_result, white_result

def make_guess(correct, guess_string, live, should_print=False):
	assert(len(guess_string) == 4)
	if should_print:
		print("\tguessing " + guess_string)

	if live:
		red = int(input())
		white = int(input())
		assert(red <= 4 and red >= 0 and white <= 4 and white >= 0 and red + white <= 4 and red + white >= 0)
	else:
		red, white = respond_to_guess(correct, guess_string)
	return Guess(guess_string, red, white), red == 4

def prune_candidates(previous_guess, candidates):

	if previous_guess == None:
		return candidates

	eligible_candidates = []
	for candidate in candidates:
		correct_red, correct_white = respond_to_guess(candidate, previous_guess.guess)
		if correct_red == previous_guess.red_result and correct_white == previous_guess.white_result:
			eligible_candidates.append(candidate)
	return eligible_candidates

def generate_random_guess():
	guess = ""
	for i in range(4):
		guess += colors[random.randrange(0, len(colors))]
	return guess

def run_one_test(live=True, ground_truth="", K=50, random_first=True, should_print=True):

	previous_guesses = [None]
	candidates = generate_all_possible()
	finished = False

	while not finished:
		random.shuffle(candidates)
		candidates = prune_candidates(previous_guesses[-1], candidates)

		if should_print:
			print("calculating (" + str(len(candidates)) + " option)...")
		candidates_to_use = candidates if len(candidates) < K else candidates[0:K]
		best_candidate = generate_random_guess()
		best_score = float("inf")

		if len(previous_guesses) > 1 or not random_first:


			for candidate in candidates_to_use:
				prune_dict = {}
				score = 0
				for hypothetical_correct in candidates_to_use:
					hypothetical_red, hypothetical_white = respond_to_guess(hypothetical_correct, candidate)
					if str(hypothetical_red) + str(hypothetical_white) not in prune_dict:
						prune_dict[str(hypothetical_red) + str(hypothetical_white)] = (len(prune_candidates(Guess(candidate, hypothetical_red, hypothetical_white), candidates_to_use)))
					score += prune_dict[str(hypothetical_red) + str(hypothetical_white)]
				if score < best_score:
					best_score = score
					best_candidate = candidate

		guess, finished = make_guess(ground_truth, best_candidate, live, should_print)
		previous_guesses.append(guess)

	return len(previous_guesses) - 1

def test(num_tests=100, K=5, random_first=False):

	start = time.time()
	total_guesses = 0
	worst_result = 0
	for i in tqdm(range(num_tests)):
		num_guesses = run_one_test(live=False, ground_truth=generate_random_guess(), K=K, random_first=random_first, should_print=False)
		total_guesses += num_guesses
		worst_result = max(num_guesses, worst_result)

	return total_guesses / num_tests, (time.time() - start) / num_tests, worst_result

def test_suite():
	for K in [1, 5, 10, 25, 50, 100]:
		for random_first in [False, True]:
			avg_results, avg_time, worst_guess = test(num_tests=10000, K=K, random_first=random_first)
			print("K:", K, "Random First:", random_first, "Results:", avg_results, "Time:", avg_time, "Worst:", worst_guess, "\n")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--live", action="store_true")
	parser.add_argument("--test", action="store_true")
	parser.add_argument("--gt")
	args = parser.parse_args()

	if args.test:
		test_suite()

	else:
		num_guesses = run_one_test(args.live, args.gt, should_print=True)
		print(num_guesses)














