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
	
	fringe = []
	fringe.append(orig)
	graph[orig]['visited'] = True
	graph[orig]['via'] = [0, 1]	# orig reached via provider
	newfringe = []

	while fringe:	# while fringe is not empty
		for node in fringe:
			if graph[node]['via'][1] == 1:
				explore = [3, 2, 1]	# this order is important
			else:
				explore = [3]

			for relation in explore:
				for neighbour in graph[node][relation]:
					if graph[neighbour]['visited'] == False:
						graph[neighbour]['visited'] = True
						graph[neighbour]['via'] = [node, relation]
						newfringe.append(neighbour)
						if neighbour == dest:
							route = []
							node = dest
							while node != orig:
								route = [node] + route
								node = graph[node]['via'][0]
							return [orig] + route
		fringe = list(newfringe)
		newfringe = []
	return None


def print_stats(paths_count, no_path):
	print "Provider paths: " + str(paths_count[1])
	print "Peer     paths: " + str(paths_count[2])
	print "Costumer paths: " + str(paths_count[3])
	print "Not connected : " + str(no_path)


def stats():
	""" generates stats for the network in graph """
	#global graph
	fringe = []
	newfringe = []
	nrnodes = len(graph)
	paths_count = {1:0, 2:0, 3:0}	# 1 - prov path, 2 - peer path, 3 - costumer path
	no_path = 0
	paths_graph = {}	# stores the path type each node is reached by
	path_translation = {(1,1):1, (1,2):1, (1,3):1, (2,3):2, (3,3):3, (3,1):1, (3,2):2}	# the last two cases are used to lie two the origin

	# populate paths_graph
	for node in graph:		
		paths_graph[node] = 0

	curr_state = 0
	for orig in graph:
		nr_unvisited = nrnodes
		if (policy_connected == True) and (not graph[orig][2]) and (not graph[orig][3]):
			paths_count[1] += nrnodes - 1
			nr_unvisited = 1
		else:
			initgraph()
			graph[orig]['visited'] = True
			graph[orig]['via'] = [0, 1]	# orig reached via provider
			fringe.append(orig)

			paths_graph[orig] = 3 # lie: origin has costumer route
			

			while fringe:	# while fringe is not empty
				for node in fringe:
					if graph[node]['via'][1] == 1:
						explore = [3, 2, 1]	# this order is important
					else:
						explore = [3]

					for relation in explore:
						for neighbour in graph[node][relation]:
							if graph[neighbour]['visited'] == False:
								nr_unvisited -= 1
								graph[neighbour]['visited'] = True
								graph[neighbour]['via'] = [node, relation]
								newfringe.append(neighbour)
								paths_graph[neighbour] = path_translation[(paths_graph[node], relation)]
								paths_count[paths_graph[neighbour]] += 1
				fringe = list(newfringe)
				newfringe = []

		no_path += nr_unvisited - 1	# minus one to account for origin
		curr_state += 1
		if curr_state % 100 == 0:
			print str(curr_state) + " origins analysed"
			print_stats(paths_count, no_path)
			print

	print "\n-- Network stats --"
	print_stats(paths_count, no_path)


def test_policy_connection():

	tier1 = set()
	for node in graph:
		if not graph[node][1]:
			tier1.add(node)
			
	for node in tier1:
		if not tier1 <= graph[node][2] | set([node]):
			print "The graph is NOT policy connected. At least " + str(node) + " cannot connect to some nodes."
			return False
	print "The graph is policy connected."
	return True


check_args()
loadgraph()
print "This network has " + str(len(graph)) + " nodes."
policy_connected = test_policy_connection()
stats()
#pprint.pprint(graph)
print "\nPress Return twice to exit."
while True:
	orig, dest = prompt()
	initgraph()
	print "The elected route is " + str(findroute(orig, dest))
	#pprint.pprint(graph)
