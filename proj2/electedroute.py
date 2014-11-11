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
			graph[head] = {1:[], 2:[], 3:[]}	# 1 - providers, 2 - peers, 3 - costumers
		graph[head][relation].append([tail, False])	# add tail to head's relations and initialise edge as unused

	f.close()	# close the file


def initgraph():
	""" resets all edges to unused state """
	global graph
	for nodeedges in graph.values():
		for edges in nodeedges.values():
			for edge in edges:
				edge[1] = False


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


def findroutes(orig, dest, path, prev, prev_rel):
	""" finds routes from orig to dest and saves them in a global
		variable routes. prev is the previous node used to reach
		orig. path is the path until prev. prev_rel is the relation
		between prev and orig from orig's point of view """
	global routes

	if len(routes) > 0 and orig in routes[0]:
		route_aux = list(routes[0])
		for i, node in enumerate(route_aux):
			if node == orig:
				routes.append(path + route_aux[i:])
				routes = [electroute()]	# find which route is best: the new or the current
				break	# all done with this route

	# add current node to path
	path.extend([orig])
	#print path

	# check if this node is the destination
	if orig == dest:
		routes.append(path)	# add path to routes
		routes = [electroute()]	# find which route is best: the new or the current
		return

	if prev_rel == 3 or prev_rel == 2:	# this node is either a costumer of prev or a peer of prev. use only costumers
		explore = [3]
	elif prev_rel == 1: # this node is a provider of prev. explore any node
		explore = [3, 2, 1]	# the order is important. explore costumers first. prevents loops

	# backup current edges state for this node for use bellow
	bak = copy.deepcopy(graph[orig])

	# mark all edges with correct relation from this node as used. this prevents using this node again
	for relation in explore:
		for i, (node, used) in enumerate(graph[orig][relation]):
			graph[orig][relation][i][1] = True	# mark outgoing edge as used

	# follow unused edges
	for relation in explore:
		for node, used in bak[relation]:
			if used == False and node != prev:	# unused edge which does not go to prev
				findroutes(node, dest, list(path), orig, relation)


def neighbour_rel(node, tosearch):
	""" finds the relation node has to tosearch """
	for relation, neighbours in graph[node].items():
		for neighbour in neighbours:
			if neighbour[0] == tosearch:
				return relation
	return None


def electroute():
	""" finds the elected route from a list of valid routes.
		returns that route as a list """
	str_routes = []

	# map a route into its relations from the point of view of the destination
	# example: if origin traverses only clients (33...33) the destinantion will see a path of providers (11...11)
	for route in routes:
		str_routes.append(''.join(str(neighbour_rel(route[i], route[i-1])) for i in range(1, len(route))))

	# sort routes. most prefered first, that is sort alphabetically and in length
	ordered_routes = [y for (x,y) in sorted(zip(str_routes, routes))]
	#print sorted(str_routes)
	#print ordered_routes
	if not ordered_routes:	# list is empty
		return None
	return ordered_routes[0]


check_args()
loadgraph()
#pprint.pprint(graph)
print "Press Return twice to exit."
while True:
	orig, dest = prompt()
	routes = []
	findroutes(orig, dest, [], None, 1)
	#print routes
	print "The elected route is " + str(routes[0] if len(routes) > 0 else None)
	#print "The elected route is " + '-'.join(map(str, routes[0] if len(routes) > 0 else [None]))
	#pprint.pprint(graph)
	initgraph()
