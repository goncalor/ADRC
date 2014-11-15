import sys
import pprint
import copy

import time

path_type = {1:"Provider path", 2:"Peer path", 3: "Customer path"}
disable_stats = False
graph = {}

def check_args():
	""" checks if a file was supplied to the script """
	if len(sys.argv) < 2:
		print "Usage: python " + sys.argv[0] + " <internet_file> [--disable-stats]\n"
		exit()
	elif len(sys.argv) == 3 and sys.argv[2] == "--disable-stats":
		global disable_stats
		disable_stats = True

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
			graph[head] = {1:set(), 2:set(), 3:set(), "visited":None, "via":[0,0]}	# 1 - providers, 2 - peers, 3 - costumers
		graph[head][relation].add(tail)	# add tail to head's relations and initialise edge as unused

	f.close()	# close the file

def initgraph():
	""" resets all edges to unused state """
	global graph
	for node in graph.values():
		node['visited'] = None

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
'''
def flip_relation(relation): #flip_relation(relation) converts from the perspective of the visiting node to the perspective of the visited node.
	return 4-relation # from 1 (P) = to 3 (C) ; from 2 (R) = to 2 (R) ; from 3 (C) = to 1 (P)
'''
	
def findroute(orig, dest):
	""" finds routes from orig to dest and returns that route as a list.
		returns None if no route exists connecting the nodes """
	global graph
	
	fringe = []
	fringe.append(orig)
	graph[orig]['visited'] = 1 # orig is tagged as visited by a node that sees him as a provider to avoid any further searches
	graph[orig]['via'] = [0, 1]	# orig reached via a node that sees him as a provider
	newfringe = []

	while fringe:	# while fringe is not empty
		for node in fringe:
			if graph[node]['via'][1] == 1: # if the node was reached by a node that sees him as a provider, share every connection with him
				explore = [3, 2, 1]	# this order is important, clients, then peers and finally providers
			else: # else, the node only gets money if the traffic is for one of his customers, share only those
				explore = [3] 

			for relation in explore:
				for neighbour in graph[node][relation]:
					if (relation == 1 and graph[neighbour]['visited'] != 1) or graph[neighbour]['visited'] == None:
						graph[neighbour]['visited'] = relation
						graph[neighbour]['via'] = [node, relation]
						newfringe.append(neighbour)
						if neighbour == dest:
							route = []
							node = dest
							second_node = node
							while node != orig:
								second_node = node
								route = [node] + route
								node = graph[node]['via'][0]
								
							print "\n" + path_type[graph[second_node]['via'][1]]
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
	paths_count = {1:0, 2:0, 3:0}	# 1 - provider path, 2 - peer path, 3 - costumer path
	no_path = 0
	paths_graph = {}	# stores the path type each node is reached by
	path_translation = {(1,1):1, (1,2):1, (1,3):1, (2,3):2, (3,3):3, (3,1):1, (3,2):2}	# the last two cases are used to lie to the origin

	# populate paths_graph
	for node in graph:		
		paths_graph[node] = 0

	curr_state = 0
	start_time = time.time()

	for orig in graph:
		nr_unvisited = nrnodes

		curr_state += 1
		if curr_state % 100 == 0:
			print str(curr_state) + " origins analysed" + "   (t = " + str(time.time() - start_time) + " s)"
			print_stats(paths_count, no_path)
			print

		if (policy_connected == True) and (not graph[orig][2]) and (not graph[orig][3]):	# network is policy connected and orig has only providers
			paths_count[1] += nrnodes - 1	# minus one to account for origin
			continue	# all done for this orig

		initgraph()
		graph[orig]['visited'] = 1
		graph[orig]['via'] = [0, 1]	# orig reached via a node that sees him as a provider
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
						if (relation == 1 and graph[neighbour]['visited'] != 1) or graph[neighbour]['visited'] == None:

							paths_graph[neighbour] = path_translation[(paths_graph[node], relation)]
							if graph[neighbour]['visited'] == None:
								nr_unvisited -= 1
								#print orig, node, neighbour
								paths_count[paths_graph[neighbour]] += 1

							graph[neighbour]['visited'] = relation
							graph[neighbour]['via'] = [node, relation]
							newfringe.append(neighbour)
							#print orig, node, neighbour, paths_graph, paths_count
							#pprint.pprint(graph)

			fringe = list(newfringe)
			newfringe = []
		no_path += nr_unvisited - 1	# minus one to account for origin

	print "\n-- Network stats --"
	if (paths_count[1]+paths_count[2]+paths_count[3]+no_path) > ((nrnodes-1) * nrnodes):
		print "\n\tI AM WRONG!\n"
	print_stats(paths_count, no_path)


def test_policy_connection():

	tier1 = set()
	for node in graph:
		if not graph[node][1]:
			tier1.add(node)  #find all tier 1 nodes. these are the nodes that have no providers, only peers or clients.
			
	for node in tier1: # check if each tier 1 node is a peer of all other tier 1 nodes, otherwise the internet is not policy connected
		if not tier1 <= graph[node][2] | set([node]): 
			print "The graph is NOT policy connected. At least " + str(node) + " cannot connect to some nodes."
			return False
	print "The graph is policy connected."
	return True


check_args()
loadgraph()
print "This network has " + str(len(graph)) + " nodes."
policy_connected = test_policy_connection()

if not disable_stats:
	start_time = time.time()
	stats()
	elapsed_time = time.time() - start_time
	print "\nelapsed time: " + str(elapsed_time) + " seconds"

#pprint.pprint(graph)
print "\nPress Return twice to exit."
while True:
	orig, dest = prompt()
	initgraph()
	print "The elected route is " + str(findroute(orig, dest))
	#pprint.pprint(graph)
	#for i in graph:
	#	for j in graph:
	#		initgraph()
	#		#print str(findroute(i, j))
	#		findroute(i, j)
