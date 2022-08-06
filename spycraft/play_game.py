import random, time


players = ["Rachel", "Daniel", "Will", "Sam", "Andrew", "Keith"]
spy = random.choice(players)

locations = []
with open("locations") as f:
	for line in f.readlines():
		locations.append(line.strip("\n"))

location = random.choice(locations)

for player in players:
	print(f"{player}:")
	input_text = ""
	while input_text not in ["here", "Here", "here!", "Here!", "HERE", "HERE!"]:
		input_text = input()
	if player != spy:
		print(f"Your location is {location}")
	else:
		print("You are the spy")
	time.sleep(1)
	for i in range(200):
		print()

print("Print 'ready' when game is done")
input_text_ready = ""
while input_text_ready != "ready":
	input_text_ready = input()

potential_options = random.sample(locations, k=20)
if location not in potential_options:
	potential_options[-1] = location

random.shuffle(potential_options)
for option in potential_options:
	print(option)
