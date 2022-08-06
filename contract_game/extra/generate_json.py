import json

def map_abbr_to_commodity(abbr):

	if abbr == "ag":
		return "Agriculture"
	if abbr == "animals":
		return "Animals"
	if abbr == "energy":
		return "Energy"
	return "Metals"

cc_list = []
with open("contract_cards") as f:
	for line in f.readlines():
		split_line = line.split()

		if len(split_line) < 3:
			continue

		current = {}
		if "exclusive" in split_line:
			current["Auction Type"] = "Exclusive"
			current["Commodity"] = map_abbr_to_commodity(split_line[0])
			current["Quantity"] = int(split_line[-1])
		else:
			current["Auction Type"] = "Cournot"
			current["Commodity"] = map_abbr_to_commodity(split_line[0])

			split_entry = split_line[-1].split("-")
			current["Base Price"] = int(split_entry[0])
			current["Multiplier"] = int(split_entry[1].strip("q")) if len(split_entry[1]) > 1 else 1
		cc_list.append(current)


city_list = []
with open("asia_city_cards") as f:
	for line in f.readlines():
		split_line = line.split()
		if len(split_line) > 1:
			city_list.append({"City": " ".join(split_line[:-1]), "Duplicate": int(split_line[-1])})

overall = {"Contract Card": cc_list, "City Card": city_list}

with open("../asia/cards.json", "w") as f:
	json.dump(overall, f)


