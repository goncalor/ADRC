import sys
import pprint
import copy

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
			graph[head] = {1:set(), 2:set(), 3:set(), "visited":False, "via":[0,0]}	# 1 - providers, 2 - peers, 3 - costumers
		graph[head][relation].add(tail)	# add tail to head's relations and initialise edge as unused

	f.close()	# close the file

def initgraph():
	""" resets all edges to unused state """
	global graph
	for node in graph.values():
		node['visited'] = False

def prompt():
	""" prompts user to provide an origin and a destination """
	orig = raw_input("\nOrigin: ")
	dest = raw_input("Destination: ")

	if not orig.isdigit() or not dest.isdigit():
		if orig == dest == '':
			print "You chose to quit. Bye."
		else:
			print "Invalid input. Need integers."
		exit()

	orig = int(orig)
	dest = int(dest)
	if orig not in graph:
		print "No node " + str(orig) + " in graph."
		exit()
	elif dest not in graph:
		print "No node " + str(dest) + " in graph."
		exit()
	return (orig, dest)


def findroute(orig, dest):
	""" finds routes from orig to dest and returns that route as a list.
		returns None if no route exists connecting the nodes """
	global graph	

	fringe = set()
	fringe.add(orig)
	graph[orig]['visited'] = True
	graph[orig]['via'] = [0, 1]	# orig reached via provider
	nrnodes = len(graph)
	newfringe = set()

	print "nr nodes: " + str(nrnodes)
	while fringe:	# while fringe is not empty
		newfringe.clear()
		for node in fringe:
			if graph[node]['via'][1] == 1:
				explore = [1, 2, 3]
			else:
				explore = [3]

			for relation in explore:
				for neighbour in graph[node][relation]:
					if graph[neighbour]['visited'] == False:
						graph[neighbour]['visited'] = True
						graph[neighbour]['via'] = [node, relation]
						newfringe.add(neighbour)
						if neighbour == dest:
							print "found dest"
							route = []
							node = dest
							while node != orig:
								route = [node] + route
								node = graph[node]['via'][0]
							return [orig] + route
		fringe = set(newfringe)
	return None


def test_policy_connection():

	tier1 = set()
	for node in graph:
		if not graph[node][1]:
			tier1.add(node)
			
	for node in tier1:
		if not tier1 <= graph[node][2] | set([node]):
			print "The graph is NOT policy connected. At least " + str(node) + " cannot connect to some nodes."
			return
	print "The graph is policy connected."


check_args()
loadgraph()
test_policy_connection()
#pprint.pprint(graph)
print "Press Return twice to exit."
while True:
	orig, dest = prompt()
	initgraph()
	#print routes
	print "The elected route is " + str(findroute(orig, dest))
	#pprint.pprint(graph)

