board = []
with open("boggle_board") as f:
	for line in f.readlines():
		for letter in line.split():
			board.append(letter)

coordinates = []
with open("possible_coordinates") as f:
	for line in f.readlines():
		coordinates.append([])
		for coord in line.split():
			coordinates[-1].append(int(coord))

scrabble_dictionary = {}
with open("scrabble.txt") as f:
	for line in f.readlines():
		word = line.strip("\n ").lower()
		scrabble_dictionary[word] = False

pts = {0:0, 1:0, 2:0, 3:0, 4:1, 5:2, 6:3, 7:5, 8:8, 9:11}
gotten_words = {4:[], 5:[], 6:[], 7:[], 8:[], 9:[]}
total_pts = 0
for possible in coordinates:
	current = ""
	for coord in possible:
		current += (board[coord] if board[coord] != "q" else "qu")
	if current in scrabble_dictionary:
		if not scrabble_dictionary[current]:
			if not(len(current) == 4 and current[-1] == "s" and current[:-1] in scrabble_dictionary):
				scrabble_dictionary[current] = True
				trunc_length = min(len(current), 9)
				gotten_words[trunc_length].append(current)
				total_pts += pts[trunc_length]


counter = 9
while counter > 3:
	for word in gotten_words[counter]:
		print(word)
	counter -= 1

print(total_pts)
