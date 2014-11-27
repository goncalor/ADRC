import sys
from pprint import pprint

def check_args():
	""" checks if a file was supplied to the script """
	if len(sys.argv) < 2:
		print "Usage: python " + sys.argv[0] + " <internet_file> [--disable-stats]\n"
		exit()
	elif len(sys.argv) == 3 and sys.argv[2] == "--disable-stats":
		global disable_stats
		disable_stats = True

def loadgraph(filename):
	""" loads the graph from a file into memory """

	try:
		f = open(filename, 'r')
	except IOError:
		print "Failed to open '" + filename + "'."
		exit()

	graph = {}
	# first line is the number of nodes in the graph. skip it
	next(f)

	for line in f:
		tmp = line.split()
		if len(tmp) != 2:
			print "Malformed line in file."
			f.close()
			exit()
		tail = int(tmp[0])
		head = int(tmp[1])

		if tail not in graph:	# let us add a new node
			graph[tail] = set()
		graph[tail].add(head)	# tail can get to head
	f.close()	# close the file
	return graph

def prompt():
	""" prompts user to provide an origin and a destination """
	src = raw_input("\nSource: ")
	dest = raw_input("Destination: ")

	if not src.isdigit() or not dest.isdigit():
		if src == dest == '':
			print "You chose to quit. Bye."
		else:
			print "Invalid input. Need integers."
		exit()

	src = int(src)
	dest = int(dest)
	if src not in graph:
		print "No node " + str(src) + " in graph."
		exit()
	elif dest not in graph:
		print "No node " + str(dest) + " in graph."
		exit()
	return (src, dest)


def count_disjoint(src, dest):
	pass


check_args()
graph = loadgraph(sys.argv[1])
#pprint(graph)
