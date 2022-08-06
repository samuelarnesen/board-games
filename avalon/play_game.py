from game_engine import GameEngine

number_of_good_guy_wins = 0
num_trials = 10000
for i in range(num_trials):
	engine = GameEngine()
	good_guys_win = engine.play_game()
	if good_guys_win:
		number_of_good_guy_wins += 1
	
print(number_of_good_guy_wins / num_trials)