import sys
import pprint
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

	
def findroute(orig, dest):
	""" finds routes from orig to dest and returns that route as a list.
		returns None if no route exists connecting the nodes """
	global graph

	fringe = []
	fringe.append(orig)
	graph[orig]['visited'] = 1 # orig is tagged as visited by a node that sees him as a provider to avoid any further searches
	graph[orig]['via'] = [0, 1]	# orig reached via a node that sees him as a provider
	newfringe = []

	if orig == dest:
		return [orig]

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


def print_stats(route_stats):
	print "Provider paths: " + str(route_stats[1])
	print "Peer     paths: " + str(route_stats[2])
	print "Costumer paths: " + str(route_stats[3])
	print "Not connected : " + str(route_stats[0])

def stats():
	global graph
	nrnodes = len(graph)
	local_pref = [[None for i in range(nrnodes)] for j in range(nrnodes)] # None will be considered -infinity
	
	index_map = dict(zip(graph.keys(), range(nrnodes))) # nodes aren't necessarily numbered from 0 to nrnodes
	allowed_routes = [[1,1,1],[None,None,2],[None,None,3]] # for each combination of route type ik and kj, indexing this gives you the resulting type of route
	
	route_stats = {0:0, 1:0, 2:0, 3:0}
	pprint.pprint(route_stats)
	
	for u in graph.keys():
		print u, index_map[u]
		local_pref[index_map[u]][index_map[u]] = 0
		for relation in [1,2,3]:
			for v in graph[u][relation]:
				local_pref[index_map[u]][index_map[v]] = relation
				
	#pprint.pprint(local_pref)			
		
	for k in range(nrnodes):
		for i in range(nrnodes):
			for j in range(nrnodes):													#relation 1		relation 2
				if (min(local_pref[i][k], local_pref[k][j]) > local_pref[i][j]) and (allowed_routes[local_pref[i][k]-1][local_pref[k][j]-1] != None):
					local_pref[i][j] = min(local_pref[i][k], local_pref[k][j])
	
	
	
	for i in range(nrnodes):
		for j in range(nrnodes):
			if i != j:
				if local_pref[i][j] != None:
					route_stats[local_pref[i][j]] += 1			
				else: 
					route_stats[0] += 1
	print_stats(route_stats)
	#pprint.pprint(local_pref)

def test_policy_connection():
	""" tests if a network is policy connected.
		returns True or False accordingly """
	tier1 = set()
	for node in graph:
		if not graph[node][1]:
			tier1.add(node)  #find all tier 1 nodes. these are the nodes that have no providers, only peers or clients.
			
	for node in tier1: # check if each tier 1 node is a peer of all other tier 1 nodes, otherwise the internet is not policy connected
		if not tier1 <= graph[node][2] | set([node]): 
			print "The graph is not policy connected. At least " + str(node) + " cannot connect to some nodes."
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
