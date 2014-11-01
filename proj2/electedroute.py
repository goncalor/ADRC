import sys
import pprint

graph = {}

def check_args():
	""" checks if a file was supplied to the script """
	if len(sys.argv) < 2:
		print "Usage: python " + sys.argv[0] + " <internet_file>\n"
		exit()

def loadgraph():
	""" loads the graph from a file into memory """
	global graph

	filename = sys.argv[1]
	try:
		f = open(filename, 'r')
	except IOError:
		print "Failed to open '" + filename + "'."
		exit()

	for line in f:
		tmp = line.split()
		if len(tmp) != 3:
			print "Malformed line in file."
			f.close()
			exit()
		tail = int(tmp[0])
		head = int(tmp[1])
		relation = int(tmp[2])

		if head not in graph:	# let us add a new node
			graph[head] = {1:[], 2:[], 3:[]}	# 1 - providers, 2 - peers, 3 - costumers
		graph[head][relation].extend([tail])	# add tail to head's relations

	f.close()	# close the file

def prompt():
	""" prompts user to provide an origin and a destination """
	orig = raw_input("Origin: ")
	dest = raw_input("Destination: ")

	if not orig.isdigit() or not dest.isdigit():
		print "Invalid input. Need integers."
		exit()

	orig = int(orig)
	dest = int(dest)
	return (orig, dest)


check_args()
loadgraph()
#pprint.pprint(graph)
orig, dest = prompt()

