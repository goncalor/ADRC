#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

#include "list.h"

#define ADDR_LEN	32	// address length in bits
#define LINE_LEN	ADDR_LEN + 6	// 1 whitespace char, max 3 interface digits, \n\0
#define DISCARD_VAL	-1	// interface value for discarded packets



//#define DEBUG

typedef struct node{
	list * interface_list; // list of interfaces the associated with the node
	struct node *right, *left;
} node;


node * loadToTree(FILE * fp, char **argv);
short * makeItem(short interface); // make an interface number into an Item type variable that can be passed to the listing functions 
short getItem(list * interface); // get the value of an interface from a list entry of a node
void changeItem(list * node_interfaces, short interface); // change the interface number on a list entry from a node
void destroyItem(Item item); // free the memory used by the item
node *create_node(void); // create a node for the tree
void print_tree(node *tree); // print the whole tree in a pre-order traversal (only the first interface of each node is printed)
void destroy_tree(node *tree); // free the memory for the whole tree
void clear_interior_next_hops(node *tree); // clear the interfaces from interior nodes (not leafs) [step 1 of ORTC]
list * percolate_2_nodes(list * nodeA_list, list * nodeB_list); // apply the percolation operation for a node [step 2 of ORTC]
void percolate_tree(node * tree); // apply the percolation operation for the whole tree [step 2 of ORTC]
void clean_redundancy(node * tree, list * ancestor_interfaces); // cleans redundancy in the tree [step 3 of ORTC]
void printToFile(node * tree, FILE * destination_file); // prints the resulting tree to a forwarding list file

list * queue = NULL;

int main(int argc, char **argv)
{
	if(argc < 2)
	{
		printf("Usage: %s forwarding_table_file\n\n", argv[0]);
		exit(0);
	}

	FILE *fp = fopen(argv[1], "r");
	if(fp == NULL)
	{
		printf("Unable to open '%s'\n\n", argv[1]);
		exit(-1);
	}

	/* load the list file to a binary tree data structure */

	node * tree = loadToTree(fp, argv);

	/* ORTC - step 1: discard interior next-hops */
	
	clear_interior_next_hops(tree);
	
	/* ORTC - step 2: calculate most frequent next-hops by traversing bottom up */
	
	percolate_tree(tree);
	
	/* ORTC - step 3: */
	
	clean_redundancy(tree, NULL);
	
	
	/* print to file */
	
	char destination[128];
	sprintf(destination, "%s.compressed", argv[1]);	
	FILE * destination_file = fopen(destination, "w");
	if(fp == NULL)
	{
		printf("Unable to open '%s'\n\n", argv[1]);
		exit(-1);
	}	
	
	printToFile(tree, destination_file);
	
	#ifdef DEBUG
	printf("final tree (pre-order traversal): ");
	print_tree(tree);
	puts("\n");
	#endif	

	destroy_tree(tree);
	LSTdestroy(queue, destroyItem);
	fclose(fp);
	fclose(destination_file);
	
	puts("done.\n");
	
	exit(0);
}

node * loadToTree(FILE * fp, char **argv)
{

	char line[LINE_LEN];
	char prefix[ADDR_LEN+1];	// +1 for \0
	short empty_interf;	// empty prefix interface
	short interf, i;
	node *aux_node;

	/* check if first line of file has empty prefix */

	fgets(line, LINE_LEN, fp);
	if(sscanf(line, "* %hdd", &empty_interf) != 1)	// no next hop defined for empty prefix. choose a value to signal that packets should be discarded
	{
		empty_interf = DISCARD_VAL;
		rewind(fp);	// reprocess first line bellow
		printf("First line of '%s' is not the empty prefix. Some packets may be discarded.\n", argv[1]);
	}

	/* load data from the forwarding table and create a balanced tree */

	node *tree = create_node();

	changeItem(tree->interface_list, empty_interf);

	while(fgets(line, LINE_LEN, fp)!=NULL)
	{
		if(sscanf(line, "%[01] %hdd", prefix, &interf) != 2)
		{
			printf("Malformed line in '%s'\n\n", argv[1]);
			exit(0);
		}
		aux_node = tree;

		for(i=0; prefix[i] != '\0'; i++)
		{
			if(aux_node->right == NULL)	// the node is a leaf. right == left == null. create children both on the left and on the right
			{
				if(prefix[i]=='0')	// next node is on the left
				{
					/* create leaf for balancing */
					aux_node->right = create_node();
					changeItem(aux_node->right->interface_list, getItem(aux_node->interface_list));
					/* create next node */
					aux_node->left = create_node();
					changeItem(aux_node->left->interface_list, getItem(aux_node->interface_list));
				}
				else	// next node is on the right
				{
					/* create leaf for balancing */
					aux_node->left = create_node();
					changeItem(aux_node->left->interface_list, getItem(aux_node->interface_list));
					/* create next node */
					aux_node->right = create_node();
					changeItem(aux_node->right->interface_list, getItem(aux_node->interface_list));
				}
			}

			/* keep going down the tree */
			if(prefix[i]=='0')	// next node is on the left
			{
				aux_node = aux_node->left;	// go to next node
			}
			else	// next node is on the right
			{
				aux_node = aux_node->right;	// go to next node
			}
		}
		changeItem(aux_node->interface_list, interf);	// place interface number in this leaf
	}
	return tree;
}

short * makeItem(short interface)
{
	short * temp = malloc(sizeof(short));
	
	if(temp == NULL)
	{
		puts("error allocating memory");
		exit(-1);
	}
	
	*temp = interface;
	
	return temp;
}

short getItem(list * node_interfaces)
{	
	if(node_interfaces == NULL)
		return DISCARD_VAL;
	else
		return *(short*)LSTgetitem(node_interfaces);	
}

void changeItem(list * node_interfaces, short interface)
{
	*(short*)LSTgetitem(node_interfaces) = interface;
} 

void destroyItem(Item item)
{
	if (item != NULL)
		free(item);
	
	return;
}

node *create_node(void)
{
	node *aux = malloc(sizeof(node));
	if(aux==NULL)
	{
		puts("ERROR: Unable to allocate memory.");
		exit(-1);
	}

	aux->interface_list = LSTadd(NULL, makeItem(DISCARD_VAL));
	aux->right = aux->left = NULL;
	return aux;
}

void print_tree(node *tree)
{
	if(tree==NULL)		
		return;
	
	printf("%hd\n", getItem(tree->interface_list));
	print_tree(tree->left);
	print_tree(tree->right);
	puts("back up");
}

void destroy_tree(node * tree)
{
	if(tree==NULL)
		return;
	destroy_tree(tree->left);
	destroy_tree(tree->right);
	LSTdestroy(tree->interface_list, destroyItem);
	free(tree);
}

void clear_interior_next_hops(node *tree)
{
	if(tree->left != NULL)
	{
		changeItem(tree->interface_list, DISCARD_VAL);
		
		clear_interior_next_hops(tree->left);
		clear_interior_next_hops(tree->right);	
	}
}

list * percolate_2_nodes(list * nodeA_list, list * nodeB_list)
{
	list * C = NULL;
	list * auxA = nodeA_list;
	list * auxB = nodeB_list;
	
	/* A#B = { intersection(A, B) if intersection(A, B) != empty set
			  junction(A, B) if intersection(A, B) = empty set }	
	
	A has interface list
	B has interface list

	create temporary list C

	for each element from A's list, if it is present on B's list add it to list C
	if no element from A's list exists on B's list, add both lists to C
	
	*/	
	
	/* fill list C if intersection(A, B) != empty set)  */
	while (auxA != NULL)
	{
		auxB = nodeB_list;
		while(auxB != NULL)
		{
			if(getItem(auxA) == getItem(auxB))
			{
				C = LSTadd(C, makeItem(getItem(auxA)));
			}
			auxB = LSTfollowing(auxB);
		}
		auxA = LSTfollowing(auxA);
	}
	
	auxA = nodeA_list;
	auxB = nodeB_list;
	
	/* if there were no matching elements from A's list and B's list, add both to C */
	if(C == NULL)
	{
		while (auxA != NULL)
		{
			C = LSTadd(C, makeItem(getItem(auxA)));
			auxA = LSTfollowing(auxA);
		}
		while (auxB != NULL)
		{
			C = LSTadd(C, makeItem(getItem(auxB)));
			auxB = LSTfollowing(auxB);
		}
	}
	
	return C;
}

void percolate_tree(node * tree)
{
	if(tree == NULL)
	{
		return;
	}
	
	percolate_tree(tree->left);
	percolate_tree(tree->right);

	if((tree->left != NULL) && (tree->right != NULL))
	{
		LSTdestroy(tree->interface_list, destroyItem);
		tree->interface_list = percolate_2_nodes(tree->left->interface_list, tree->right->interface_list);
		
		#ifdef DEBUG 
			list * aux = tree->interface_list;
			while(aux != NULL)
			{
				printf("%hd ", getItem(aux));
				aux = LSTfollowing(aux);
			}
			puts("\n");
		#endif
	}
	
	return;
}

void clean_redundancy(node * tree, list * ancestor_interfaces)
{
	if(tree == NULL)
		return;
	
	
	/* For each child, if it has a matching interface with it's parent, 
	   delete it's own list and tell it's own children 
	   (keep a memory of the last ancestor that didn't delete it's own list) */
	

	list * aux_self = tree->interface_list;
	list * aux_ancestor = ancestor_interfaces;
	list * temp = NULL;
	short match_found = 0;
	
	/* see if there are matching interfaces between current node and ancestor */
	while(aux_ancestor != NULL && match_found == 0)	
	{
		aux_self = tree->interface_list;
		while(aux_self != NULL && match_found == 0)
		{
			if(getItem(aux_self) == getItem(aux_ancestor)) // match found, delete current node interfaces to avoid redundancy 
			{
				LSTdestroy(tree->interface_list, destroyItem);
				tree->interface_list = NULL; 
				match_found = 1;
			}
			aux_self = LSTfollowing(aux_self);
		}		
		aux_ancestor = LSTfollowing(aux_ancestor);		
	}
	
	/* no matches found, choose a random interface from the node (first is fine, no need for actual random choice) */
	if(match_found == 0)
	{
		temp = LSTadd(NULL, makeItem(getItem(tree->interface_list)));
		LSTdestroy(tree->interface_list, destroyItem);
		tree->interface_list = temp;		
	}
	

	if(match_found == 1)
	{
		clean_redundancy(tree->left, ancestor_interfaces);
		clean_redundancy(tree->right, ancestor_interfaces);
	}
	else
	{
		clean_redundancy(tree->left, tree->interface_list);
		clean_redundancy(tree->right, tree->interface_list);
	}
}

void printToFile(node * tree, FILE * destination_file)
{
	list * queue_aux = queue;	
	
	if (getItem(tree->interface_list) != -1) // if this node has a next-hop, write it to the file
	{
		queue_aux = queue;
		if(queue_aux == NULL) // still at root node, print '*' to simbolize default next-hop
		{	
			fprintf(destination_file, "*\t%hd\n", *(short*)LSTgetitem(tree->interface_list));			
		}
		else 
		{	/* ugly hacks here to change LIFO to FIFO */
			list * queue_fix_head = NULL;
			list * queue_fix = NULL;			
			while(queue_aux != NULL) // not root, print the prefix (path taken) of the next-hop
			{
				queue_fix = LSTadd(queue_fix, makeItem(*(short*)LSTgetitem(queue_aux)));				 
				queue_aux = LSTfollowing(queue_aux);
			}
			queue_fix_head = queue_fix;
			while(queue_fix != NULL) // not root, print the prefix (path taken) of the next-hop
			{
				fprintf(destination_file, "%hd", *(short*)LSTgetitem(queue_fix));			 
				queue_fix = LSTfollowing(queue_fix);
			}

			LSTdestroy(queue_fix_head, destroyItem);
			fprintf(destination_file, "\t%hd\n", *(short*)LSTgetitem(tree->interface_list)); // print the next-hop itself and change line
		}
	}
	
	// do the same for the rest of the tree
	if(tree->left != NULL)
	{
		queue = LSTadd(queue, makeItem(0)); 
		printToFile(tree->left, destination_file);
	}
	if(tree->right != NULL)
	{
		queue = LSTadd(queue, makeItem(1));
		printToFile(tree->right, destination_file);		
	}
	
	// going back up, remove the last entered bit of the prefix
	queue = LSTremove(NULL, queue, destroyItem); 
}

	

	
	
