import networkx as nx
import matplotlib.pyplot as plt
import sys

graph = {}
no_show = False

def check_args():
	""" checks if a file was supplied to the script """
	if len(sys.argv) < 2:
		print "Usage: python " + sys.argv[0] + " <internet_file> [--no-show]\n"
		exit()
	elif len(sys.argv) == 3 and sys.argv[2] == "--no-show":
		global no_show
		no_show = True

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


def draw_graph(graph):
	""" prepares the graph to be shown or exported """
	G = nx.DiGraph()
	G.add_nodes_from(graph.keys())

	provider = []
	peer = []
	costumer = []
	for node in graph:
		for relation in range(1, 4):
			for edge in graph[node][relation]:
				G.add_edge(node, edge)
				if relation == 1:
					provider.append((node, edge))
				elif relation == 2:
					peer.append((node, edge))
				else:
					costumer.append((node, edge))

	#pos = nx.circular_layout(G)
	#pos = nx.spring_layout(G)
	pos = nx.shell_layout(G)

	# draw nodes
	nx.draw_networkx_nodes(G, pos, node_color="w")

	# color nodes with no providers
	nx.draw_networkx_nodes(G, pos, nodelist = [i for i in graph if not graph[i][1]], node_color="r")
	# color nodes with only providers
	nx.draw_networkx_nodes(G, pos, nodelist = [i for i in graph if not graph[i][2] and not graph[i][3]], node_color="g")

	#draw colored edges
	#nx.draw_networkx_edges(G, pos, edgelist = provider, edge_color = "r")
	nx.draw_networkx_edges(G, pos, edgelist = peer, edge_color = "k", style="dotted")
	nx.draw_networkx_edges(G, pos, edgelist = costumer, edge_color = "g")
	nx.draw_networkx_labels(G, pos)


check_args()
loadgraph()
draw_graph(graph)

plt.axis('off')
plt.savefig(sys.argv[1] + ".png")
if not no_show:
	plt.show()

