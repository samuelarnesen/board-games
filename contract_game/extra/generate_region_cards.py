import pandas as pd 
import json


df = pd.read_csv("usa_units.csv")

big_list = []

for i in range(df.values.shape[0]):

	current = {}
	row = df.iloc[i]
	current["Unit ID"] = int(row["No"])
	current["name"] = row["Name"]
	for col in ["Agriculture", "Animals", "Energy", "Metals"]:
		current[col] = int(row[col])

	city_list = []
	for col in ["City_One", "City_Two", "City_Three"]:
		if isinstance(row[col], str):
			city_list.append(row[col])
	current["Adjacent Cities"] = city_list

	current["Region"] = row["Region"]
	split_adjacent_units = row["Adjacent Units"].split(",")
	adjacent = [int(au.strip(" ")) for au in split_adjacent_units]
	sorted(adjacent)
	current["Adjacent Units"] = adjacent

	big_list.append(current)


for unit in big_list:
	unit_id = unit["Unit ID"]
	if unit_id in unit["Adjacent Units"]:
		print(f"{unit_id} has a self-loop")
	for other_unit in unit["Adjacent Units"]:
		#print(other_unit - (1 if other_unit < 59 else 0))
		#if unit_id not in big_list[other_unit - (1 if other_unit < 59 else 2)]["Adjacent Units"]:
		if unit_id not in big_list[other_unit - 1]["Adjacent Units"]:
			print(f"{unit_id} missing from {other_unit}")

with open("../usa/units.json", "w") as f:
	json.dump({"Unit": big_list}, f)