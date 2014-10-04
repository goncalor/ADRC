#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

#include "list.h"

#define ADDR_LEN	32	// address length in bits
#define LINE_LEN	ADDR_LEN + 6	// 1 whitespace char, max 3 interface digits, \n\0
#define DISCARD_VAL	-1	// interface value for discarded packets



#define DEBUG

typedef struct node{
	list * interface_list; // list of interfaces the associated with the node
	struct node *right, *left;
} node;

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
	
	/* ORTC - step 1: discard interior next-hops */
	
	clear_interior_next_hops(tree);
	
	/* ORTC - step 2: calculate most frequent next-hops by traversing bottom up */
	
	percolate_tree(tree);
	
	/* ORTC - step 3: */
	
	
		

	#ifdef DEBUG
	printf("loaded tree (pre-order traversal): ");
	print_tree(tree);
	puts("\n");
	#endif	

	destroy_tree(tree);
	fclose(fp);
	
	puts("Bye.\n");
	
	exit(0);
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
		return *(short*)(node_interfaces->item);	
}

void changeItem(list * node_interfaces, short interface)
{
	*(short*)(node_interfaces->item) = interface;
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
	printf("%hd ", getItem(tree->interface_list));
	print_tree(tree->left);
	print_tree(tree->right);
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
	
	/* A#B = { A e B se A e B != vazio
			  A com B se A e B = vazio }

	A tem lista
	B tem lista

	cria lista temporária C

	para cada elemento da lista de A, se tb estiver presente na lista B, adicionar à lista C
	se nenhum elemento de A estiver presente em B, juntar ambas em C
	
	*/	
	
	/* fill list C if((A /\ B) != empty set)  */
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
	
	
