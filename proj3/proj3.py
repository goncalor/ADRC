import sys
from pprint import pprint
import copy

def check_args():
	""" checks if a file was supplied to the script """
	disable_stats = False
	disable_prompt = False
	
	if len(sys.argv) < 2 or len(sys.argv) > 4:
		print "Usage: python " + sys.argv[0] + " <internet_file> [--disable-stats] [--disable-prompt]\n"
		exit()
		
	else:
		if len(sys.argv) >= 3:
			if sys.argv[2] == "--disable-stats":
				disable_stats = True
			if sys.argv[2] == "--disable-prompt":
				disable_prompt = True
		if len(sys.argv) == 4:
			if sys.argv[3] == "--disable-stats":
				disable_stats = True
			if sys.argv[3] == "--disable-prompt":
				disable_prompt = True
	return disable_stats, disable_prompt


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
		if head not in graph:
			graph[head] = set()
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
	if dest not in graph:
		print "No node " + str(dest) + " in graph."
		exit()
	return (src, dest)


def count_disjoint(graph, src, dest): # Edmond Karp

	if src == dest:
		return 0	# 0 ?

	graph = copy.deepcopy(graph)	# change graph only in this scope
	visited = {}

	for node in graph:
		visited[node] = (False, None)


	# all disjoint paths have been found when we can't find dest anymore
	nr_disjoint = -1
	dest_found = True
	while dest_found:
		dest_found = False
		nr_disjoint += 1
		fringe = set([src])
		newfringe = set()

		# all nodes not visited
		for node in graph:
			visited[node] = (False, None)

		# do a BFS to find dest
		while fringe:
			for node in fringe:
				if node == dest:
					dest_found = True
					fringe = set()	# breaks the while loop
					break

				for neighbour in graph[node]:
					if not visited[neighbour][0]:
						newfringe.add(neighbour)
						visited[neighbour] = (True, node)

			fringe = set(newfringe)
			newfringe = set()

		# backtrace from dest to scr and invert edges
		if dest_found:
			node = dest
			while node != src:
				via = visited[node][1]
				graph[node].add(via)
				graph[via].remove(node)
				node = via

	return nr_disjoint


def statistics(graph, disable_stats):
	
	separated_by = {} # k indexes the dictionary. separated_by[k] = number of pairs of nodes that get separeted if k links fail
		
	for nodeA in graph: 
		for nodeB in graph:
			if nodeA != nodeB: # for each pair of distinct nodes compute the number of disjoint paths
				current_k = count_disjoint(graph, nodeA, nodeB) 
				if current_k != 0: # if the pair has at least k >= 1 disjoint paths, increment the number of pairs that get disconnected by k link failures 
					try:
						separated_by[current_k] += 1
					except KeyError, err:
						separated_by[current_k] = 1 # create new dictionary entries only has needed, instead of initializing a large number of possible indexes
		break
	if not disable_stats: 
		print_statistics(separated_by)


def print_statistics(separated_by):
	total_connections = 0
	total_failures = 0
	try: 
		max_k = max(separated_by)
	except ValueError:
		return # if the graph has only one node this will fail and link_connectivity() already has an apropriate print
	
	for k in separated_by: # count the total number of connections that exist by adding all the values of the dictionary
		total_connections += separated_by[k]

	for k in range(1, max_k+1): # print all values of k until the maximum one, not only the values that make new connections fail
		try:
			total_failures += separated_by[k]
		except KeyError:
			pass	# if, for example, k=3 added no new failures, separated_by[3] does not exist so we ignore the KeyError
		
		if k == 1: 
			print "k=" + str(k) + ': ' + str(total_failures) + "/" + str(total_connections) + " existing connections fail." + "\tStill connected: " + '|' * ((total_connections) - total_failures)
		else:
			print "k=" + str(k) + ': ' + str(total_failures) + "/" + str(total_connections) + " existing connections fail." + "\tStill connected: " + '|' * ((total_connections) - total_failures)
	# print "(run with argument [--disable-stats] to supress the prints above)"
	print


def link_connectivity(graph):
	min_k = None
	for nodeA in graph:
		for nodeB in graph:
			if nodeA != nodeB:
				k = count_disjoint(graph, nodeA, nodeB)
				
				if k == 0: # means at least one pair is already disconnected
					print "The graph is already disconnected, " + str(nodeA) + " can't connect to " + str(nodeB)
					return
				if k < min_k or min_k == None: # if found a new minimum k or first k computed 
					min_k = k
					exampleA = nodeA
					exampleB = nodeB
	
	if min_k == None: # only happens if there are no pairs, i.e. there's only one node
		print "The graph has only one node and therefore cannot become disconnected"
		return
	if min_k == 1:
		print "1 broken link is enough for the network to become disconnected"
		print "for example: " + str(exampleA) + " can be separated from " + str(exampleB) + " by only 1 broken link"
	else:
		print str(min_k) + " broken links are enough for the network to become disconnected"
		print "for example: " + str(exampleA) + " can be separated from " + str(exampleB) + " by only " + str(min_k) + " broken links"
	return



disable_stats, disable_prompt = check_args()
graph = loadgraph(sys.argv[1])
#pprint(graph)
statistics(graph, disable_stats)
link_connectivity(graph)
if not disable_prompt:
	while True:
		src, dest = prompt()
		print "No. of disjoint paths: " + str(count_disjoint(graph, src, dest))
