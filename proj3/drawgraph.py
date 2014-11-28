import networkx as nx
import matplotlib.pyplot as plt
import sys

no_show = False

def check_args():
	""" checks if a file was supplied to the script """
	if len(sys.argv) < 2:
		print "Usage: python " + sys.argv[0] + " <internet_file> [--no-show]\n"
		exit()
	elif len(sys.argv) == 3 and sys.argv[2] == "--no-show":
		global no_show
		no_show = True

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


def draw_graph(graph):
	""" prepares the graph to be shown or exported """
	G = nx.DiGraph()
	G.add_nodes_from(graph.keys())

	for node in graph:
		for neighbour in graph[node]:
			G.add_edge(node, neighbour)

	#pos = nx.circular_layout(G)
	#pos = nx.spring_layout(G)
	pos = nx.shell_layout(G)

	# draw nodes
	nx.draw_networkx_nodes(G, pos, node_color="w")

	#draw colored edges
	#nx.draw_networkx_edges(G, pos, edgelist = provider, edge_color = "r")
	nx.draw_networkx_edges(G, pos, edge_color = "k")
	nx.draw_networkx_labels(G, pos)


check_args()
graph = loadgraph(sys.argv[1])
draw_graph(graph)

plt.axis('off')
plt.savefig(sys.argv[1] + ".png")
if not no_show:
	plt.show()
