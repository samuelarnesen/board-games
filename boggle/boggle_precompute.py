import itertools, sys

def check_if_continuous(seq):
	previous = ((seq[0] % 5), int(seq[0] / 5))
	for elem in seq[1:]:
		current =  ((elem % 5), int(elem / 5))
		if abs(current[0] - previous[0]) > 1 or abs(current[1] - previous[1]) > 1:
			return False
		previous = current
	return True

for i in range(4, 8):
	print(i, file=sys.stderr)
	perms = itertools.permutations(range(0, 25), i)
	for i, seq in enumerate(perms):
		if i % 10000000 == 0 and i != 0:
			print(i, file=sys.stderr)
		if check_if_continuous(seq):
			for elem in seq:
				print(elem, end="\t")
			print()

			