#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>

#define ADDR_LEN	32	// address length in bits
#define LINE_LEN	ADDR_LEN + 6	// 1 whitespace char, max 3 interface digits, \n\0
#define DISCARD_VAL	-1	// interface value for discarded packets



#define DEBUG

typedef struct node{
	short interf;	// interface
	struct node *right, *left;
} node;

node *create_node(void);
void print_tree(node *tree);
void destroy_tree(node *tree);
void clear_interior_next_hops(node *tree);

#ifdef DEBUG
void print_tree(node *tree);
#endif



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
	if(sscanf(line, "* %hd", &empty_interf) != 1)	// no next hop defined for empty prefix. choose a value to signal that packets should be discarded
	{
		empty_interf = DISCARD_VAL;
		rewind(fp);	// reprocess first line bellow
		printf("First line of '%s' is not the empty prefix. Some packets may be discarded.\n", argv[1]);
	}

	/* load data from the forwarding table and create a balanced tree */

	node *tree = create_node();

	tree->interf = empty_interf;

	while(fgets(line, LINE_LEN, fp)!=NULL)
	{
		if(sscanf(line, "%[01] %hd", prefix, &interf) != 2)
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
					aux_node->right->interf = aux_node->interf;
					/* create next node */
					aux_node->left = create_node();
					aux_node->left->interf = aux_node->interf;
				}
				else	// next node is on the right
				{
					/* create leaf for balancing */
					aux_node->left = create_node();
					aux_node->left->interf = aux_node->interf;
					/* create next node */
					aux_node->right = create_node();
					aux_node->right->interf = aux_node->interf;
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
		aux_node->interf = interf;	// place interface number in this leaf
	}
	
	/* ORTC - step 1: discard interior next-hops ('-1' is a cleared node) */
	
	clear_interior_next_hops(tree);
	
	/* ORTC - step 2: calculate most frequent next-hops by traversing bottom up */
	
	
	
	
	

	#ifdef DEBUG
	printf("loaded tree (in-order traversal): ");
	print_tree(tree);
	puts("\n");
	#endif

	puts("Bye.\n");

	destroy_tree(tree);
	fclose(fp);
	exit(0);
}





node *create_node(void)
{
	node *aux = malloc(sizeof(node));
	if(aux==NULL)
	{
		puts("ERROR: Unable to allocate memory.");
		exit(-1);
	}
	#ifdef DEBUG
	aux->interf = 0;
	#endif
	aux->right = aux->left = NULL;
	return aux;
}

void print_tree(node *tree)
{
	if(tree==NULL)
		return;
	printf("%d ", tree->interf);
	print_tree(tree->left);
	print_tree(tree->right);
}

void destroy_tree(node *tree)
{
	if(tree==NULL)
		return;
	destroy_tree(tree->left);
	destroy_tree(tree->right);
	free(tree);
}

void clear_interior_next_hops(node *tree)
{
	if(tree->left != NULL)
	{
		tree->interf = DISCARD_VAL;
		
		clear_interior_next_hops(tree->left);
		clear_interior_next_hops(tree->right);	
	}
}

