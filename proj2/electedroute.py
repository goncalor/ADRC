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
		graph[head][relation].append([tail, False])	# add tail to head's relations and initialise edge as unused

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


def electroute(orig, dest, path, prev, prev_rel):
	global elected

	if prev != None:
		# check if incoming edge has been used previously
		tmp = graph[orig][{1:3,2:2,3:1}[prev_rel]]	# translate prev_rel to match this node's point of view
		if [prev, True] in tmp:	# edge has been used
			return

		# mark the incoming edge as used
		tmp[tmp.index([prev, False])][1] = True

	# add current node to path
	path.extend([orig])
	#print path

	# check if this node is the destination and if it was reached via a peer
	if orig == dest and prev_rel != 2:
		elected.append(path)	# add path to elected
		return

	if prev_rel == 3 or prev_rel == 2:	# this node is either a costumer of prev or a peer of prev. use only costumers
		explore = [3]
	elif prev_rel == 1: # this node is a provider of prev. explore any node
		explore = [3, 2, 1]	# the order is important. explore costumers first

	for relation in explore:
		for (node, used) in graph[orig][relation]:
			if used == False:	#unused edge
				electroute(node, dest, list(path), orig, relation)


check_args()
loadgraph()
#pprint.pprint(graph)
orig, dest = prompt()
elected = []
electroute(orig, dest, [], None, 1)
print elected
