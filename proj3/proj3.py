import sys
from pprint import pprint
import copy

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


def count_disjoint(graph, src, dest):

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

def k_distribution(graph):
	
	separated_by = {} # k indexes the dictionary. separated_by[k] = number of pairs of nodes that get separeted if k links fail
		
		for nodeA in graph:
			for nodeB in graph:
				if nodeA != nodeB:
					current_k = count_disjoint(graph, nodeA, nodeB)
					if current_k != 0:
						try:
							separated_by[current_k] += 1
						except KeyError, err:
							separated_by[current_k] = 1
	
	print separated_by

check_args()
graph = loadgraph(sys.argv[1])
#pprint(graph)
k_distribution(graph)
while True:
	src, dest = prompt()
	print "No. of disjoint paths: " + str(count_disjoint(graph, src, dest))
